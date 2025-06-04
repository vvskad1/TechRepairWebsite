from fastapi import APIRouter, HTTPException, Depends
import httpx
import os
import json
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from sqlalchemy.orm import Session
from db import SessionLocal
import crud, schemas
from typing import Dict, List

router = APIRouter(prefix="/chat", tags=["Chat"])

# Store conversation history in memory (you might want to move this to a database for production)
conversations: Dict[str, List[dict]] = {}

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = None  # Optional, will be generated if not provided
    model_config = ConfigDict(from_attributes=True)

# System prompt for the chatbot
SYSTEM_PROMPT = """You are FixIt Tech Solutions' virtual assistant.
Your primary goal is guide users and let them know about our website
Your secondary goal is to help users book tech repair services and provide clear information.

When handling bookings:
1. Collect all required info in sequence:
   - Full name
   - Email address
   - Phone number
   - Device type AND model (be specific, e.g., "HP Pavilion" not just "HP")
   - Issue description (get specific details)
   - Preferred date AND time

2. Before creating the booking:
   - Show collected information for confirmation
   - Format as 'BOOKING_SUMMARY: I have collected the following details:
     - Name: [name]
     - Email: [email]
     - Phone: [phone]
     - Device: [device]
     - Issue: [issue]
     - Appointment: [date and time]
     Is this information correct?'
   - Wait for user confirmation

3. After confirmation:
   - Send: 'BOOKING_INFO:{"name":"...","email":"...","phone":"...","device":"...","issue":"...","date":"YYYY-MM-DDTHH:MM:00"}'

4. After booking creation:
   - Always provide a complete summary including our location
   - Format appointment times clearly (e.g., "June 6th at 3:00 PM")
   - Include our address: 123 Tech Lane, Innovation City, 12345

Company Details:
- Location: 123 Tech Lane, Innovation City, 12345
- Services: screen replacement, battery replacement, water damage repair, data recovery
- Devices: phones, laptops, tablets, and other electronics
- Contact: support@fixittech.com, +1 (555) 123-4567
- 10+ years experience, certified technicians, transparent pricing

Guidelines:
- Be friendly and concise
- For missing info, politely ask one question at a time
- When asking for device info, request both type AND specific model
- For appointment times, confirm both date AND time
- If user asks for summary, show all booking details and our location
- If unsure, offer to connect with human support
- Mention our fast service, quality parts, and friendly support"""

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def parse_booking_info(text: str) -> dict:
    """Extract booking info from AI response if it contains BOOKING_INFO:"""
    if "BOOKING_INFO:" in text:
        try:
            booking_str = text.split("BOOKING_INFO:")[1].strip()
            # Remove any text after the JSON
            booking_str = booking_str.split("\n")[0]
            return json.loads(booking_str.replace("'", '"'))
        except:
            return None
    return None

@router.post("/")
async def chat_with_ai(request: ChatRequest, db: Session = Depends(get_db)):
    # Always reload env vars to pick up changes
    groq_api_url = os.getenv("GROQ_API_URL")
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_url or not groq_api_key:
        raise HTTPException(status_code=500, detail="Groq API not configured.")
    
    # Generate conversation ID if not provided
    if not request.conversation_id:
        request.conversation_id = str(hash(datetime.now().isoformat()))
    
    # Initialize conversation history if it doesn't exist
    if request.conversation_id not in conversations:
        conversations[request.conversation_id] = []
    
    # Get existing conversation history
    conversation = conversations[request.conversation_id]
    
    # Add user message to history
    conversation.append({"role": "user", "content": request.message})
    
    # Prepare messages for API call
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *conversation  # Include all previous messages
    ]

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            groq_api_url,
            headers={"Authorization": f"Bearer {groq_api_key}"},
            json=payload
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Groq API error: {response.text}")
        
        ai_response = response.json()
        assistant_message = ai_response["choices"][0]["message"]["content"]
        
        # Add assistant's response to conversation history
        conversation.append({"role": "assistant", "content": assistant_message})
        
        # Check if the response contains booking information
        booking_info = parse_booking_info(assistant_message)
        if booking_info:
            try:
                # Create booking from the extracted information
                booking = schemas.BookingCreate(
                    name=booking_info["name"],
                    email=booking_info["email"],
                    phone=booking_info["phone"],
                    device=booking_info["device"],
                    issue=booking_info["issue"],
                    date=datetime.fromisoformat(booking_info["date"])
                )
                crud.create_booking(db, booking)
                # Remove the BOOKING_INFO from the response
                assistant_message = "I've created a booking with the information you provided. " + \
                    assistant_message.split("BOOKING_INFO:")[0]
            except Exception as e:
                assistant_message = "I encountered an error while creating your booking. " + \
                    "Please try again or contact our support team."
        
        return {
            "response": assistant_message,
            "conversation_id": request.conversation_id
        }
