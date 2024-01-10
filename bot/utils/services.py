import base64
from io import BytesIO

from bot.loader import client
from openai.types.beta.threads import Run, ThreadMessage

import asyncio


class OpenAIService:
    assistant_id: str | None = None

    @classmethod
    async def create_assistant(cls):
        instruction = "You are a personal doctor nutritionist. " +\
            "analyze the following dishes and determine whether they are harmful or healthy" +\
            "Answer questions briefly, in a sentence or less. " +\
            "Give all answers in Russian" 

        assistant = await client.beta.assistants.create(
                    name="doctor nutritionist",
                    instructions=instruction,
                    model="gpt-4-1106-preview",
        )
        cls.assistant_id = assistant.id
    
    @staticmethod
    def bytes_to_base64(bytes_obj: BytesIO) -> str:
        return base64.b64encode(bytes_obj.read()).decode('utf-8')
    
    @classmethod
    async def get_response_by_image(cls, bytes_image: BytesIO) -> str:
        text = "tell me the name of the dishes that are shown in the image. " +\
            "Please avoid numbering, unnecessary details and lengthy explanations"
        url = f"data:image/jpeg;base64,{cls.bytes_to_base64(bytes_image)}"
        response = await client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": text},
                            {
                            "type": "image_url",
                            "image_url": {
                                "url": url
                            },
                            },
                        ],
                    }
                ],
                max_tokens=300,
        )    
        return response.choices[0].message.content
    
    @staticmethod
    async def text_to_speech(input_text: str) -> bytes:
        response = await client.audio.speech.create(
            model="tts-1-hd",
            voice="alloy",
            input=input_text,
            response_format='opus'
        )
        return response.content

    @staticmethod
    async def speech_to_text(bytes_audio: BytesIO) -> str:
        bytes_audio.name = "voice.ogg"
        return await client.audio.transcriptions.create(
            model="whisper-1",
            response_format='text',
            file=bytes_audio
        )
    
    @classmethod
    async def submit_message(
        cls,
        thread_id: str,
        user_message: str
    ) -> Run:
        await client.beta.threads.messages.create(
            thread_id=thread_id, role="user", content=user_message
        )
        return await client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=cls.assistant_id,
        )
    
    @staticmethod
    async def get_response(thread_id: str):
        return await \
            client.beta.threads.messages.list(thread_id=thread_id)

    @classmethod
    async def create_thread_and_run(cls, user_input) -> tuple[str, Run]:
        thread = await client.beta.threads.create()
        run = await cls.submit_message(thread.id, user_input)
        return thread.id, run
    
    @staticmethod
    async def retrieve_run(run, thread_id):
        while run.status == "queued" or run.status == "in_progress":
            run = await client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id,
            )
            await asyncio.sleep(0.3)
    
    @classmethod
    async def get_assistant_response(
        cls, 
        thread_id: None | str, 
        user_input: str
    ) -> tuple[str, str]:
        if thread_id:
            run = await cls.submit_message(thread_id, user_input)
        else:
            thread_id, run = await cls.create_thread_and_run(user_input)

        await cls.retrieve_run(run, thread_id)
        response = await cls.get_response(thread_id)
        message: ThreadMessage = response.data[0]
        return message.content[0].text.value, thread_id
