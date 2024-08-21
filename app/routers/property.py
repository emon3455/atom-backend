from fastapi import APIRouter, HTTPException, Query, Path
from sqlalchemy import text
from app.database import Session
from typing import List, Dict, Any
from dotenv import load_dotenv
import requests
import json
import os

router = APIRouter()
load_dotenv()

attom_api_key = os.getenv('ATTOM_API_KEY')
ATTOM_API_URL = "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail"


@router.get("/")
def get_properties(
    limit: int = Query(10, description="Number of results to return"),
    offset: int = Query(0, description="Number of results to skip")
):
    session = Session()
    try:
        sql = text(f"""
            SELECT * FROM location_properties
            LIMIT :limit OFFSET :offset
        """)

        result_proxy = session.execute(sql, {"limit": limit, "offset": offset})
        results = result_proxy.fetchall()

        if results:
            columns = result_proxy.keys()
            results_list = [dict(zip(columns, row)) for row in results]
            return results_list
        else:
            return []

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        session.close()

@router.get("/filter")
def filter_properties_by_search_text(searchText: str = Query(..., description="Search text for filtering data")):
    session = Session()
    try:
        search_value = f"%{searchText}%"

        sql = text("""
            SELECT * FROM location_properties
            WHERE property_address_oneLine LIKE :searchText
        """)

        result_proxy = session.execute(sql, {"searchText": search_value})
        results = result_proxy.fetchall()

        if results:
            columns = result_proxy.keys()
            results_list = [dict(zip(columns, row)) for row in results]
            return results_list
        else:
            # Search ATTOM API
            attom_data = get_attom_property(searchText)
            if not attom_data:
                return []

            # Convert and insert into local database
            converted_data = convert_attom_response(attom_data)
            insert_property_into_db(converted_data)

            # Return the newly inserted data
            return [converted_data]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        session.close()

def convert_attom_response(attom_response: Dict[str, Any]) -> Dict[str, Any]:
    property_data = attom_response.get("property", [{}])[0]

    # Extract fields from ATTOM response
    identifier = property_data.get("identifier", {})
    lot = property_data.get("lot", {})
    area = property_data.get("area", {})
    address = property_data.get("address", {})
    location = property_data.get("location", {})
    summary = property_data.get("summary", {})
    utilities = property_data.get("utilities", {})
    building = property_data.get("building", {})
    vintage = property_data.get("vintage", {})

    # Convert and map fields to match database schema
    converted_data = {
        "property_identifier_attomId": identifier.get("attomId"),
        "property_identifier_fips": identifier.get("fips"),
        "property_identifier_apn": identifier.get("apn"),
        "property_identifier_apnOrig": None,  # Not provided in ATTOM response

        "property_lot_depth": str(lot.get("depth", "")),
        "property_lot_frontage": str(lot.get("frontage", "")),
        "property_lot_lotnum": lot.get("lotnum"),
        "property_lot_lotsize1": str(lot.get("lotsize1", "")),
        "property_lot_lotsize2": lot.get("lotsize2"),
        "property_lot_lottype": None,  # Not provided in ATTOM response
        "property_lot_poolind": None,  # Not provided in ATTOM response
        "property_lot_pooltype": lot.get("pooltype"),

        "property_area_blockNum": area.get("blockNum"),
        "property_area_loctype": area.get("loctype"),
        "property_area_countrysecsubd": area.get("countrysecsubd"),
        "property_area_countyuse1": area.get("countyuse1"),
        "property_area_muncode": area.get("muncode"),
        "property_area_munname": area.get("munname"),
        "property_area_taxcodearea": area.get("taxcodearea"),

        "property_address_bldgName": None,  # Not provided in ATTOM response
        "property_address_country": address.get("country"),
        "property_address_countrySubd": address.get("countrySubd"),
        "property_address_line1": address.get("line1"),
        "property_address_line2": address.get("line2"),
        "property_address_locality": address.get("locality"),
        "property_address_matchCode": address.get("matchCode"),
        "property_address_oneLine": address.get("oneLine"),
        "property_address_postal1": address.get("postal1"),
        "property_address_postal2": address.get("postal2"),
        "property_address_postal3": address.get("postal3"),

        "property_location_accuracy": location.get("accuracy"),
        "property_location_elevation": None,  # Not provided in ATTOM response
        "property_location_latitude": float(location.get("latitude", 0.0)),
        "property_location_longitude": float(location.get("longitude", 0.0)),
        "property_location_distance": str(location.get("distance", "")),
        "property_location_geoid": location.get("geoid"),

        "property_summary_absenteeInd": summary.get("absenteeInd"),
        "property_summary_propclass": summary.get("propclass"),
        "property_summary_propsubtype": summary.get("propsubtype"),
        "property_summary_proptype": summary.get("proptype"),
        "property_summary_yearbuilt": summary.get("yearbuilt"),
        "property_summary_propLandUse": summary.get("propLandUse"),
        "property_summary_propIndicator": summary.get("propIndicator"),
        "property_summary_legal1": summary.get("legal1"),
        "property_summary_legal2": None,  # Not provided in ATTOM response
        "property_summary_legal3": None,  # Not provided in ATTOM response

        "property_utilities_coolingtype": None,  # Not provided in ATTOM response
        "property_utilities_energyType": utilities.get("energyType"),
        "property_utilities_heatingfuel": utilities.get("heatingfuel"),
        "property_utilities_heatingtype": utilities.get("heatingtype"),
        "property_utilities_sewertype": utilities.get("sewertype"),
        "property_utilities_waterType": utilities.get("waterType"),

        "property_building": json.dumps({
            "size": {
                "bldgsize": building.get("size", {}).get("bldgsize"),
                "grosssizeadjusted": building.get("size", {}).get("grosssizeadjusted"),
                "groundfloorsize": building.get("size", {}).get("groundfloorsize"),
                "livingsize": building.get("size", {}).get("livingsize"),
                "sizeInd": building.get("size", {}).get("sizeInd"),
                "universalsize": building.get("size", {}).get("universalsize"),
            },
            "rooms": {
                "bathsfull": building.get("rooms", {}).get("bathsfull"),
                "bathstotal": building.get("rooms", {}).get("bathstotal"),
                "beds": building.get("rooms", {}).get("beds"),
            },
            "interior": building.get("interior"),
            "construction": {
                "condition": building.get("construction", {}).get("condition"),
                "foundationtype": building.get("construction", {}).get("foundationtype"),
                "wallType": building.get("construction", {}).get("wallType"),
            },
            "parking": building.get("parking"),
            "summary": {
                "archStyle": building.get("summary", {}).get("archStyle"),
                "bldgsNum": building.get("summary", {}).get("bldgsNum"),
                "levels": building.get("summary", {}).get("levels"),
                "unitsCount": building.get("summary", {}).get("unitsCount"),
                "view": building.get("summary", {}).get("view"),
            }
        }),

        "property_vintage_lastModified": vintage.get("lastModified"),
        "property_vintage_pubDate": vintage.get("pubDate"),
    }

    return converted_data

def get_attom_property(search_text: str) -> Dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "apiKey":  attom_api_key
    }
    params = {
        "address": search_text,
    }
    response = requests.get(ATTOM_API_URL, headers=headers, params=params)
    response.raise_for_status()  # Raise an exception for HTTP errors
    return response.json()

def insert_property_into_db(property_data: Dict[str, Any]):
    session = Session()
    try:
        sql = text("""
            INSERT INTO location_properties (
                property_identifier_attomId, property_identifier_fips, property_identifier_apn,
                property_identifier_apnOrig, property_lot_depth, property_lot_frontage,
                property_lot_lotnum, property_lot_lotsize1, property_lot_lotsize2,
                property_lot_lottype, property_lot_poolind, property_lot_pooltype,
                property_area_blockNum, property_area_loctype, property_area_countrysecsubd,
                property_area_countyuse1, property_area_muncode, property_area_munname,
                property_area_taxcodearea, property_address_bldgName, property_address_country,
                property_address_countrySubd, property_address_line1, property_address_line2,
                property_address_locality, property_address_matchCode, property_address_oneLine,
                property_address_postal1, property_address_postal2, property_address_postal3,
                property_location_accuracy, property_location_elevation, property_location_latitude,
                property_location_longitude, property_location_distance, property_location_geoid,
                property_summary_absenteeInd, property_summary_propclass, property_summary_propsubtype,
                property_summary_proptype, property_summary_yearbuilt, property_summary_propLandUse,
                property_summary_propIndicator, property_summary_legal1, property_summary_legal2,
                property_summary_legal3, property_utilities_coolingtype, property_utilities_energyType,
                property_utilities_heatingfuel, property_utilities_heatingtype, property_utilities_sewertype,
                property_utilities_waterType, property_building, property_vintage_lastModified,
                property_vintage_pubDate
            ) VALUES (
                :property_identifier_attomId, :property_identifier_fips, :property_identifier_apn,
                :property_identifier_apnOrig, :property_lot_depth, :property_lot_frontage,
                :property_lot_lotnum, :property_lot_lotsize1, :property_lot_lotsize2,
                :property_lot_lottype, :property_lot_poolind, :property_lot_pooltype,
                :property_area_blockNum, :property_area_loctype, :property_area_countrysecsubd,
                :property_area_countyuse1, :property_area_muncode, :property_area_munname,
                :property_area_taxcodearea, :property_address_bldgName, :property_address_country,
                :property_address_countrySubd, :property_address_line1, :property_address_line2,
                :property_address_locality, :property_address_matchCode, :property_address_oneLine,
                :property_address_postal1, :property_address_postal2, :property_address_postal3,
                :property_location_accuracy, :property_location_elevation, :property_location_latitude,
                :property_location_longitude, :property_location_distance, :property_location_geoid,
                :property_summary_absenteeInd, :property_summary_propclass, :property_summary_propsubtype,
                :property_summary_proptype, :property_summary_yearbuilt, :property_summary_propLandUse,
                :property_summary_propIndicator, :property_summary_legal1, :property_summary_legal2,
                :property_summary_legal3, :property_utilities_coolingtype, :property_utilities_energyType,
                :property_utilities_heatingfuel, :property_utilities_heatingtype, :property_utilities_sewertype,
                :property_utilities_waterType, :property_building, :property_vintage_lastModified,
                :property_vintage_pubDate
            )
        """)
        session.execute(sql, property_data)
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()
