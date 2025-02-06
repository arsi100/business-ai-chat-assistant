from fastapi import APIRouter, Request, HTTPException
from twilio.request_validator import RequestValidator
from ..config import get_settings
from openai import OpenAI
import logging

router = APIRouter()
settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)

@router.post("/webhook")
async def webhook(request: Request):
    try:
        # Get the form data from the request
        form_data = await request.form()
        
        # Extract message details
        message_body = form_data.get("Body", "")
        from_number = form_data.get("From", "")
        
        # Print message details
        print(f"\nReceived Message:")
        print(f"From: {from_number}")
        print(f"Message: {message_body}\n")
        
        # Generate AI response
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for Dubai real estate services and inforamtion. Keep responses clear and concise, under 1500 characters. Provide brief, actionable information."},
                {"role": "user", "content": message_body}
            ]
        )
        ai_response = response.choices[0].message.content
        print(f"AI Response: {ai_response}\n")
        
        # Send response
        from ..api.messaging import TwilioProvider
        provider = TwilioProvider()
        await provider.send_message(to=from_number, message=ai_response)
        
        return {"status": "success"}
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
