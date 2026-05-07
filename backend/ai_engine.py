import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 🤖 AI GENERATION (Groq Cloud API)
# ==========================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

def generate_reply(data):
    tone = "friendly" if data.user_type.lower() == "student" else "professional"
    prompt = f"Write a short, {tone} customer service email responding to this issue: '{data.message}'. Do not include a subject line."

    try:
        print(f"⏳ Asking Llama 3.1 to write a {tone} email...")
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=150,
        )
        ai_text = chat_completion.choices[0].message.content.strip()
        
        if not ai_text or len(ai_text) < 15:
            ai_text = default_reply(data, tone)
            
    except Exception as e:
        print("❌ AI Error:", e)
        ai_text = default_reply(data, tone)

    return f"Name: {data.name}\nProduct Number: {data.product}\n\nResponse:\n{ai_text}"

def default_reply(data, tone):
    if tone == "friendly":
        return "Hey! 😊 We received your request. Don't worry, we're working on it soon."
    else:
        return "Dear Customer, we have received your request. Our team is reviewing it shortly."

# 👇 HERE IS THE NEW FUNCTION THAT FASTAPI WAS LOOKING FOR! 👇
def generate_resolution_reply(ticket):
    """Generates an email when the Admin clicks 'Mark Done'"""
    tone = "friendly" if ticket.user_type.lower() == "student" else "professional"
    
    prompt = f"Write a short, {tone} email to {ticket.name} letting them know their customer support ticket regarding '{ticket.query_type}' has been fully resolved and closed. Thank them for their patience. Do not include a subject line."

    try:
        print(f"⏳ Asking Llama 3.1 to write a Resolution email for {ticket.name}...")
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.7,
            max_tokens=150,
        )

        ai_text = chat_completion.choices[0].message.content.strip()

    except Exception as e:
        print("❌ AI Error on Resolution:", e)
        ai_text = f"Dear {ticket.name},\n\nWe wanted to let you know that your ticket regarding '{ticket.query_type}' is now fully resolved. Thank you!"

    return f"Name: {ticket.name}\nTicket Status: RESOLVED ✅\n\nMessage:\n{ai_text}"