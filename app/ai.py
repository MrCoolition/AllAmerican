from openai import OpenAI
from .config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

SYSTEM_PROMPT = """You are the voice agent for a professional moving company.
- Be concise, warm, and decisive.
- Capabilities: schedule appointments; provide estimates (ask miles, rooms, stairs, special items); order status lookup by name/phone/order #; FAQs (insurance, packing, windows, etc.); escalate to human if stuck.
- Always confirm key details back to the caller.
"""

def stream_completion(history: list[dict], user_text: str):
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [
        {"role": "user", "content": user_text}
    ]
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2,
        stream=True
    )
    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta and delta.content:
            yield delta.content
