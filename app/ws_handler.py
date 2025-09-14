import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .ai import stream_completion
from .db import SessionLocal
from .models import ConversationLog
from .quotes import compute_quote, MoveSpec

router = APIRouter()

def _append_log(db, session_id, call_sid, from_number, to_number, role, text):
    rec = db.query(ConversationLog).filter_by(session_id=session_id).first()
    if not rec:
        rec = ConversationLog(session_id=session_id, call_sid=call_sid,
                              from_number=from_number, to_number=to_number, transcript=[])
        db.add(rec)
    rec.transcript.append({"role": role, "text": text})
    db.commit()

@router.websocket("/voice/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    history: list[dict] = []
    call_sid = session_id = from_number = to_number = None

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)

            if msg.get("type") == "setup":
                session_id = msg["sessionId"]
                call_sid = msg["callSid"]
                from_number = msg.get("from", "")
                to_number = msg.get("to", "")
                continue

            if msg.get("type") == "prompt":
                user_text = msg.get("voicePrompt", "")
                history.append({"role": "user", "content": user_text})
                with SessionLocal() as db:
                    _append_log(db, session_id, call_sid, from_number, to_number, "user", user_text)

                lower = user_text.lower()
                if "schedule" in lower or "book" in lower or "appointment" in lower:
                    response_text = "Sure, let’s schedule your move. What date and time work best, and from where to where?"
                    await websocket.send_text(json.dumps({"type": "text", "token": response_text, "last": True}))
                    history.append({"role": "assistant", "content": response_text})
                    with SessionLocal() as db:
                        _append_log(db, session_id, call_sid, from_number, to_number, "assistant", response_text)
                    continue

                if "quote" in lower or "estimate" in lower or "price" in lower:
                    response_text = "I can estimate that. How many miles, how many rooms, any stairs or special items like a piano, and is it a weekend move?"
                    await websocket.send_text(json.dumps({"type": "text", "token": response_text, "last": True}))
                    history.append({"role": "assistant", "content": response_text})
                    with SessionLocal() as db:
                        _append_log(db, session_id, call_sid, from_number, to_number, "assistant", response_text)
                    continue

                if "status" in lower or "order" in lower or "job" in lower:
                    response_text = "I can check your order. What’s the order number or name and phone on the order?"
                    await websocket.send_text(json.dumps({"type": "text", "token": response_text, "last": True}))
                    history.append({"role": "assistant", "content": response_text})
                    with SessionLocal() as db:
                        _append_log(db, session_id, call_sid, from_number, to_number, "assistant", response_text)
                    continue

                if "human" in lower or "agent" in lower or "representative" in lower:
                    await websocket.send_text(json.dumps({
                        "type": "end",
                        "handoffData": "{\"reasonCode\":\"live-agent-handoff\"}"
                    }))
                    break

                buffer = ""
                async def send_token(token: str, last: bool=False):
                    await websocket.send_text(json.dumps({"type": "text", "token": token, "last": last}))

                for token in stream_completion(history, user_text):
                    buffer += token
                    await send_token(token, last=False)

                await send_token("", last=True)
                history.append({"role": "assistant", "content": buffer})
                with SessionLocal() as db:
                    _append_log(db, session_id, call_sid, from_number, to_number, "assistant", buffer)

            elif msg.get("type") == "interrupt":
                continue

    except WebSocketDisconnect:
        pass
    finally:
        try:
            await websocket.send_text(json.dumps({"type": "end"}))
        except Exception:
            pass
