from fastapi import APIRouter, status

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
def read_health():
    """
    Check the health of the application.
    """
    return {"status": "ok"}
