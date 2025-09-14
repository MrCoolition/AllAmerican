from fastapi import APIRouter, Request
from fastapi.responses import Response
from .config import settings

router = APIRouter(prefix="/voice", tags=["voice"])

@router.post("/incoming")
async def incoming_call(_: Request):
    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Connect action="{settings.BASE_URL}/voice/after">
    <ConversationRelay
      url="{settings.WS_URL}"
      ttsProvider="ElevenLabs"
      voice="{settings.ELEVENLABS_VOICE_ID}"
      language="en-US"
      interruptible="speech"
      reportInputDuringAgentSpeech="speech"
      welcomeGreeting="Hi, thanks for calling {settings.COMPANY_NAME}. How can I help with your move today?" />
  </Connect>
</Response>"""
    return Response(content=xml, media_type="text/xml")

@router.post("/after")
async def after_connect(request: Request):
    form = await request.form()
    handoff = form.get("HandoffData", "")
    if "live-agent" in handoff:
        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say>Connecting you to a specialist now.</Say>
  <Dial>{settings.TWILIO_FORWARD_NUMBER}</Dial>
</Response>"""
    else:
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response><Say>Thanks for calling. Goodbye!</Say></Response>"""
    return Response(content=xml, media_type="text/xml")
