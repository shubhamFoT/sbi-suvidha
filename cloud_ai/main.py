from fastapi import FastAPI, Form, Response
from twilio.twiml.messaging_response import MessagingResponse
import json

app = FastAPI(title="SBI Suvidha Cloud Pipeline")

# ----------------------------------------------------
# 1. MOCK PUBLIC SANDBOX APIs (DigiLocker & Account Aggregator)
# ----------------------------------------------------
@app.get("/api/digilocker/fetch")
def mock_digilocker_fetch(aadhaar_id: str):
    """Simulates checking citizen credentials via DigiLocker Sandbox"""
    # In a real environment, this validates against government crypt-keys
    return {
        "status": "Success",
        "source": "DigiLocker Verified",
        "data": {
            "full_name": "Shubham",
            "pan_number": "ABCDE1234F",
            "address_verified": True
        }
    }

@app.get("/api/account-aggregator/consent")
def mock_financial_fetch(consent_id: str):
    """Simulates pulling structured banking cash-flows"""
    return {
        "status": "Consented",
        "source": "Account Aggregator Ecosystem",
        "metrics": {
            "avg_monthly_credit": 450000,
            "existing_defaults": 0,
            "risk_score": "Low Risk"
        }
    }

# ----------------------------------------------------
# 2. WHATSAPP CONVERSATIONAL INGESTION (Twilio Webhook)
# ----------------------------------------------------
@app.post("/webhook/whatsapp")
def incoming_whatsapp(Body: str = Form(...), From: str = Form(...)):
    """Receives real-time text streams from the WhatsApp Sandbox"""
    user_message = Body.strip().lower()
    twilio_response = MessagingResponse()
    
    print(f"Incoming message from customer ({From}): '{user_message}'")
    
    # Simple state routing simulating the LangChain logic pipeline
    if "loan" in user_message or "suvidha" in user_message:
        reply = ("Welcome to *SBI Suvidha* Autonomous Pipeline! 🏦\n\n"
                 "To begin your seamless verification, please reply with your mock Aadhaar Number.")
        
    elif user_message.isdigit() and len(user_message) == 4:
        # Trigger the internal mock DigiLocker verification step
        digilocker_data = mock_digilocker_fetch(aadhaar_id=user_message)
        customer_name = digilocker_data["data"]["full_name"]
        
        # Trigger the mock alternative credit data check
        credit_data = mock_financial_fetch(consent_id="CONSENT-991")
        
        # Build the final dossier payload for the branch desk
        dossier = {
            "token_id": "105",
            "customer_name": customer_name,
            "status": "AI-Verified",
            "risk_profile": credit_data["metrics"]["risk_score"],
            "action": "Proceed to Counter 3 for Signature"
        }
        
        # Save payload locally to serve to the physical hardware node
        with open("queue_state.json", "w") as file:
            json.dump(dossier, file)
            
        reply = (f"Thank you, *{customer_name}*!\n\n"
                 "✅ *Phase 1 (Ingestion) Complete.*\n"
                 "✅ *Phase 2 (Multi-Agent Underwriting) Complete.*\n\n"
                 "Your dossier is marked *Branch-Ready*. When you arrive at the branch, "
                 "your file will load instantly at the teller desk. Proceed directly to the counter.")
    else:
        reply = "SBI Suvidha Pipeline Active. Type 'Loan' to begin processing."

    twilio_response.message(reply)
    return Response(content=str(twilio_response), media_type="application/xml")

# ----------------------------------------------------
# 3. PHYGITAL INTERCEPT HARDWARE BRIDGE
# ----------------------------------------------------
@app.get("/queue_state.json")
def serve_hardware_queue():
    """Endpoint for the ESP32 node to fetch the latest pipeline state"""
    try:
        with open("queue_state.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"status": "Idle", "message": "No customer transactions active in queue"}