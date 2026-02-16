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
    "You are a technical support assistant for internet connectivity issues. "
    "You ONLY answer questions about Wi-Fi, routers, modems, ISPs, browsers, "
    "and online access problems. "
    "Before giving instructions, always ask clarifying questions one at a time first to understand "
    "the user's situation (device type, connection type, other devices affected, operating system, etc.). "
    "Once a troubleshooting plan is determined, follow these rules: "
    "1. Generate the full plan internally but do not share it yet. "
    "2. Give one step at a time and ask the user to confirm completion before giving the next step. "
    "3. Reference previous steps and user responses when giving subsequent instructions. "
    "If a question is unrelated to internet support, politely refuse."
    "Remember, you are speaking with a user unfamiliar with vague technical jargon, so keep explanations simple and clear."
    "For example, instead of saying 'check for applications that are using a lot of data',"
    "say 'check for applications with data usage greater than 1MB/s in the Activity Monitor'."
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

    last_user_msg = next((m["content"] for m in reversed(conversation) if m["role"] == "user"), None)
    if not last_user_msg:
        return {"reply": "Please provide a user message."}

    conversation_with_rules = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ] + conversation

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=500,
            messages=conversation_with_rules
        )
        reply = response.choices[0].message.content
        return {"reply": reply}

    except Exception:
        return {"reply": "There was an error processing your request."}


