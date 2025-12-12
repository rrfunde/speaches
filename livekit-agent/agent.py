import logging
import os

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions
from livekit.plugins import noise_cancellation, openai, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv()

logger = logging.getLogger(__name__)


class VoiceAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a helpful voice AI assistant.
            Keep responses concise and conversational.
            Do not use complex formatting, emojis, or special characters.""",
        )


async def entrypoint(ctx: agents.JobContext) -> None:
    await ctx.connect()

    speaches_base_url = os.getenv("SPEACHES_BASE_URL", "http://localhost:8000/v1")
    logger.info(f"Using Speaches STT at {speaches_base_url}")

    session = AgentSession(
        # STT: Speaches (faster-whisper) via OpenAI-compatible API
        stt=openai.STT(
            base_url=speaches_base_url,
            api_key="not-needed",
            model="Systran/faster-whisper-large-v3",
            language="en",
        ),
        # LLM: OpenAI
        llm=openai.LLM(model="gpt-4o-mini"),
        # TTS: OpenAI
        tts=openai.TTS(model="tts-1", voice="alloy"),
        # VAD: Silero for voice activity detection
        vad=silero.VAD.load(),
        # Turn detection for natural conversation flow
        turn_detection=MultilingualModel(),
    )

    await session.start(
        room=ctx.room,
        agent=VoiceAssistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await session.generate_reply(instructions="Greet the user and offer your assistance.")


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
