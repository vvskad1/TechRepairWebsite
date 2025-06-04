from fastapi import APIRouter, HTTPException, Depends
import httpx
import os
import json
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db import SessionLocal
import crud, schemas
from typing import Dict, List
from rag_utils import retrieve_relevant_kb

router = APIRouter(prefix="/chat", tags=["Chat"])

# Store conversation history in memory (you might want to move this to a database for production)
conversations: Dict[str, List[dict]] = {}

class ChatRequest(BaseModel):
    message: str
    conversation_id: str = None  # Optional, will be generated if not provided
    model_config = ConfigDict(from_attributes=True)

# System prompt for the chatbot
SYSTEM_PROMPT = """You are FixIt Tech Solutions' virtual assistant.
Your primary goal is to guide users and let them know about our website.
Your secondary goal is to help users book tech repair services and provide clear information.

You are also friendly and conversational. If a user greets you (e.g., 'hi', 'hello', 'yo', 'hey'), respond warmly and offer to help with repairs or questions. If a user asks a general question or makes small talk, respond politely and try to steer the conversation toward how you can assist with tech repair, booking, or company information.

When handling bookings:
1. Collect all required info in sequence:
   - Full name
   - Email address
   - Phone number
   - Device type AND model (be specific, e.g., 'HP Pavilion' not just 'HP')
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
   - Format appointment times clearly (e.g., 'June 6th at 3:00 PM')
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
- Mention our fast service, quality parts, and friendly support
- Always respond politely to greetings and small talk, and offer to help with repairs or questions."""

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

    # Always reload env vars to pick up changes
    groq_api_url = os.getenv("GROQ_API_URL")
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_url or not groq_api_key:
        raise HTTPException(status_code=500, detail="Groq API not configured.")

    # --- RAG: Retrieve relevant KB entries ---
    relevant_kb = retrieve_relevant_kb(request.message, top_k=2)
    kb_context = "\n\n".join(f"{e['title']}: {e['content']}" for e in relevant_kb)
    rag_prompt = SYSTEM_PROMPT + (f"\n\nKnowledge Base:\n{kb_context}" if kb_context else "")

    # Prepare messages for API call
    messages = [
        {"role": "system", "content": rag_prompt},
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
        # Log the full Groq API response for debugging
        print('Groq API raw response:', ai_response)
        assistant_message = ai_response["choices"][0]["message"]["content"]

        # Add assistant's response to conversation history
        conversation.append({"role": "assistant", "content": assistant_message})

        # Fallback: If the LLM response is empty or generic, provide a friendly default
        fallback_phrases = [
            "Sorry, I couldn't understand that.",
            "I'm not sure how to help with that.",
            "Could you please rephrase your question?"
        ]
        if assistant_message.strip().lower() in [p.lower() for p in fallback_phrases] or not assistant_message.strip():
            assistant_message = "Hi! I'm FixIt Tech Solutions' assistant. I can help you book a repair, answer questions about our services, or provide company info. How can I assist you today?"

        # Check if the response contains booking information
        booking_info = parse_booking_info(assistant_message)
        if booking_info:
            try:
                # Fix: Accept both 'Tomorrow' and date strings, and always store in DB
                from dateutil import parser as date_parser
                import re
                date_str = booking_info["date"]
                # If user says 'Tomorrow', convert to date
                if re.match(r"(?i)tomorrow", date_str):
                    dt = datetime.now() + timedelta(days=1)
                    # Try to extract time from string
                    time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", date_str, re.I)
                    if time_match:
                        hour = int(time_match.group(1))
                        minute = int(time_match.group(2) or 0)
                        ampm = (time_match.group(3) or '').lower()
                        if ampm == 'pm' and hour < 12:
                            hour += 12
                        dt = dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    else:
                        dt = dt.replace(hour=10, minute=0, second=0, microsecond=0)  # default 10am
                else:
                    try:
                        dt = date_parser.parse(date_str)
                    except Exception:
                        dt = datetime.now()
                booking = schemas.BookingCreate(
                    name=booking_info["name"],
                    email=booking_info["email"],
                    phone=booking_info["phone"],
                    device=booking_info["device"],
                    issue=booking_info["issue"],
                    date=dt
                )
                crud.create_booking(db, booking)
                assistant_message = "I've created a booking with the information you provided. " + \
                    assistant_message.split("BOOKING_INFO:")[0]
            except Exception as e:
                assistant_message = f"I encountered an error while creating your booking: {e}. Please try again or contact our support team."
        
        # Always return the assistant's final response
        return {"message": assistant_message, "conversation_id": request.conversation_id}
