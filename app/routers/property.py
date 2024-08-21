from fastapi import APIRouter, HTTPException, Query, Path
from sqlalchemy import text
from app.database import Session

router = APIRouter()


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
            WHERE  property_address_oneLine LIKE :searchText
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


@router.get("/attom-search")
def get_properties(searchText: str = Query(..., description="Search text for filtering data")):
    session = Session()
    try:
      print("printing...")

      # here you have to search product by using the searchText from atom api

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        session.close()
