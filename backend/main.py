from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import engine, SessionLocal
import models
from ai_engine import generate_reply, generate_resolution_reply
from email_service import send_email
# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Query(BaseModel):
    name: str
    email: str
    phone: str
    product: str
    user_type: str
    query_type: str
    message: str

@app.post("/submit")
def submit_query(q: Query, db: Session = Depends(get_db)):
    print("📥 Received data:", q)

    # Generate AI reply
    reply = generate_reply(q)

    if not reply or len(reply.strip()) < 10:
        reply = "Thank you for contacting us. We will resolve your issue shortly."

    print("🤖 Generated reply:", reply)

    # Save ticket
    ticket = models.Ticket(
        name=q.name,
        email=q.email,
        phone=q.phone,
        product=q.product,
        user_type=q.user_type,
        query_type=q.query_type,
        message=q.message,
        response=reply,
        status="Pending"
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    # Send email
    try:
        send_email(q.email, reply)
    except Exception as e:
        print("❌ Email failed:", e)

    return {
        "reply": reply,
        "ticket_id": ticket.id
    }

@app.get("/tickets")
def get_tickets(db: Session = Depends(get_db)):
    return db.query(models.Ticket).all()

@app.put("/tickets/{ticket_id}")
def mark_done(ticket_id: int, db: Session = Depends(get_db)):
    # Find the ticket in the database
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()

    if ticket:
        # 1. Update the database status
        ticket.status = "Done"
        db.commit()

        # 2. Ask Groq to write the resolution email
        resolution_message = generate_resolution_reply(ticket)

        # 3. Send the email to the customer
        try:
            send_email(ticket.email, resolution_message)
            print(f"✅ Resolution email sent successfully to {ticket.email}!")
        except Exception as e:
            print("❌ Failed to send resolution email:", e)

        return {"message": "Ticket marked done and email sent!"}

    return {"error": "Ticket not found"}

@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if ticket:
        db.delete(ticket)
        db.commit()
        return {"message": "Ticket deleted successfully"}
    return {"error": "Ticket not found"}