from fastapi import FastAPI
from src.api.whatsapp import router as whatsapp_router
from src.api import sms

app = FastAPI(title="WhatsApp AI Bot")

# Add WhatsApp webhook routes
app.include_router(whatsapp_router, prefix="/whatsapp", tags=["whatsapp"])

# Add SMS router
app.include_router(sms.router, prefix="/sms", tags=["sms"])

@app.get("/")
async def root():
    return {"status": "running"} 