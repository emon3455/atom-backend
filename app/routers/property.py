from fastapi import APIRouter, HTTPException, Query, Path
from sqlalchemy import text
from app.database import Session

router = APIRouter()

@router.get("/filter")
def filter_data(search_text: str = Query(..., description="Search text for filtering data")):
    session = Session()
    try:
        sql = text("""
        SELECT * FROM properties
        WHERE JSON_UNQUOTE(JSON_EXTRACT(address, '$.zip')) LIKE :search_text
        OR JSON_UNQUOTE(JSON_EXTRACT(address, '$.address')) LIKE :search_text
        OR JSON_UNQUOTE(JSON_EXTRACT(address, '$.city')) LIKE :search_text
        OR JSON_UNQUOTE(JSON_EXTRACT(address, '$.state')) LIKE :search_text
        """)
        params = {"search_text": f"%{search_text}%"}

        result_proxy = session.execute(sql, params)
        results = result_proxy.fetchall()

        if results:
            columns = result_proxy.keys()
            results_list = [dict(zip(columns, row)) for row in results]
            return results_list
        else:
            raise HTTPException(status_code=404, detail="No matching records found.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        session.close()

@router.get("/{property_id}")
def get_property_by_id(property_id: int = Path(..., description="ID of the property to retrieve")):
    session = Session()
    try:
        sql = text("SELECT * FROM properties WHERE id = :property_id")
        params = {"property_id": property_id}

        result_proxy = session.execute(sql, params)
        result = result_proxy.fetchone()

        if result:
            columns = result_proxy.keys()
            return dict(zip(columns, result))
        else:
            raise HTTPException(status_code=404, detail="Property not found.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        session.close()
