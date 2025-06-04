# FixIt Tech Solutions Backend

This is the FastAPI backend for FixIt Tech Solutions, a tech repair service. It provides endpoints for:
- Booking repair appointments
- Viewing available services
- Checking ticket status
- Chatbot (Groq API integration)
- Admin features

## Features
- Booking management
- Service listing
- Ticket status tracking
- AI-powered chat (Groq API)
- Admin endpoints
- SQLite integration
- Email notifications
- CORS enabled for frontend integration

## Setup
1. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```
2. **Configure environment variables:**
   Create a `.env` file in the backend directory with the following (edit as needed):
   ```env
   DATABASE_URL=sqlite+aiosqlite:///./fixit.db
   FRONTEND_ORIGIN=http://localhost:3000
   GROQ_API_URL=your_groq_api_url
   GROQ_API_KEY=your_groq_api_key
   SMTP_SERVER=smtp.example.com
   SMTP_PORT=587
   SMTP_USER=your_email@example.com
   SMTP_PASSWORD=your_password
   FROM_EMAIL=your_email@example.com
   ```
3. **Initialize the database:**
   ```powershell
   python -c "from db import Base, engine; Base.metadata.create_all(bind=engine)"
   ```
4. **Run the server:**
   ```powershell
   uvicorn main:app --reload
   ```

## API Endpoints
- `/booking` - Booking operations
- `/services` - List services
- `/ticket` - Ticket status
- `/chat` - AI chatbot
- `/admin` - Admin features

## Notes
- Ensure all environment variables are set for full functionality.
- For production, use a secure SMTP provider and set proper CORS origins.

## Environment Variables
- Configure secrets and email settings in a `.env` file (see `.env.example`).

## Project Structure
- `main.py` - FastAPI app entry point
- `models.py` - Database models
- `schemas.py` - Pydantic schemas
- `crud.py` - Database operations
- `api/` - API route modules
- `utils/` - Utility functions (email, chat, etc.)

---

For more details, see code comments and docstrings.
