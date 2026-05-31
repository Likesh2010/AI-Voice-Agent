from typing import Optional

from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Play, Say

from ..core.config import settings


class TwilioService:
    def __init__(self) -> None:
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
        self.from_phone = settings.twilio_phone_number

    def create_outbound_call(self, destination_number: str, callback_url: str) -> dict[str, str]:
        call = self.client.calls.create(
            to=destination_number,
            from_=self.from_phone,
            url=callback_url,
        )
        return {"sid": call.sid, "status": call.status}

    def build_twiml_prompt(self, audio_url: Optional[str] = None, text: Optional[str] = None) -> str:
        response = VoiceResponse()
        if audio_url:
            response.play(audio_url)
        elif text:
            response.say(text, voice="alice", language="en-US")
        else:
            response.say("Thank you for joining the recruitment screening. Please hold for the next question.", voice="alice", language="en-US")
        return str(response)

    def build_twiml_record(self, question: str, action_url: str) -> str:
        response = VoiceResponse()
        response.say(question, voice="alice", language="en-US")
        response.record(action=action_url, max_length=60, play_beep=True, timeout=3)
        return str(response)
