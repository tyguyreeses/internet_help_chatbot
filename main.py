from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os

app = FastAPI()

# Allow frontend requests (lock to real domain later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://internethelpdesksupport.com"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "You are a technical support assistant. "
    "You **ONLY** answer questions about internet connectivity, Wi-Fi, routers, "
    "modems, ISPs, browsers, online access issues, etc. "
    "If a question is unrelated, politely refuse and say you only handle internet support."
)

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: Request):
    data = await req.json()
    conversation = data.get("conversation", [])

    if not conversation:
        return {"reply": "No conversation received."}

    # Hard topic gate: only check last user message
    last_user_msg = None
    for msg in reversed(conversation):
        if msg["role"] == "user":
            last_user_msg = msg["content"]
            break

    if not last_user_msg:
        return {"reply": "Please provide a user message."}

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=500,
            messages=conversation
        )
        reply = response.choices[0].message.content
        return {"reply": reply}

    except Exception:
        return {"reply": "There was an error processing your request."}

