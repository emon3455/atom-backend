from fastapi import APIRouter, HTTPException, Query, Path
from sqlalchemy import text
from app.database import Session

router = APIRouter()

@router.get("/filter")
def filter_properties_by_search_text(searchText: str = Query(..., description="Search text for filtering data")):
    session = Session()
    try:
        search_value = f"%{searchText}%"

        sql = text("""
            SELECT * FROM location_properties
            WHERE property_address_postal1 LIKE :searchText
            OR property_address_postal2 LIKE :searchText
            OR property_address_postal3 LIKE :searchText
            OR property_address_oneLine LIKE :searchText
            OR property_area_countrysecsubd LIKE :searchText
        """)

        result_proxy = session.execute(sql, {"searchText": search_value})
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
