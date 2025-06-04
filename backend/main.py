import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="FixIt Tech Solutions Backend")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for local development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import and include routers (absolute imports)
from api_booking import router as booking_router
from api_services import router as services_router
from api_ticket import router as ticket_router
from api_chat import router as chat_router
from api_admin import router as admin_router
from api_contact import router as contact_router

app.include_router(booking_router)
app.include_router(services_router)
app.include_router(ticket_router)
app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(contact_router)

@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "FixIt Tech Solutions Backend is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
