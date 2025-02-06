from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from ..config import get_settings

router = APIRouter()

@router.post("/incoming")
async def incoming_sms(request: Request):
    try:
        form_data = await request.form()
        message = form_data.get('Body')
        from_number = form_data.get('From')
        
        print(f"\nReceived SMS:")
        print(f"From: {from_number}")
        print(f"Message: {message}\n")
        
        return {"status": "success"}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"status": "error"} 