from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
import re

app = FastAPI()

# Allow frontend requests (lock to real domain later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Strict topic filter
KEYWORDS = re.compile(
    r"(internet|wifi|wi-fi|router|modem|isp|network|connection|browser|ethernet|latency|speed)",
    re.I,
)

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

    if not KEYWORDS.search(last_user_msg):
        return {"reply": "I can only help with internet and connectivity issues."}

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=500,
            messages=conversation
        )
        reply = response.choices[0].message.content
        return {"reply": reply}

    except Exception as e:
        return {"reply": "There was an error processing your request."}

