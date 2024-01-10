import io

from bot.handlers.ai.services import OpenAIService
from bot.loader import bot

from aiogram import types
from aiogram import F, Router
from aiogram.types import BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext


router = Router()

@router.message(F.text)
async def assistant_dialogue(message: types.Message, state: FSMContext):
    msg = await message.answer('пожалуйста, подождите...')
    await bot.send_chat_action(message.chat.id, 'record_voice')
    fsm_data = await state.get_data()
    thread_id = fsm_data.get('thread_id')
    response, thread_id = await OpenAIService.get_assistant_response(thread_id, message.text)
    print(response)
    
    await msg.edit_text(text=response)
    await state.update_data(thread_id=thread_id)

@router.message(F.voice)
async def handle_voice(message: types.Message, state: FSMContext):
    msg = await message.answer('пожалуйста, подождите...')
    await bot.send_chat_action(message.chat.id, 'record_voice')
    voice = message.voice
    result: io.BytesIO = await bot.download(voice)

    fsm_data = await state.get_data()
    thread_id = fsm_data.get('thread_id')

    transcript = await OpenAIService.speech_to_text(result)
    response, thread_id = await OpenAIService.get_assistant_response(thread_id, transcript)

    bytes_voice = await OpenAIService.text_to_speech(response)
    await msg.delete()
    await message.answer_voice(
        BufferedInputFile(
            bytes_voice,
            filename="voice.ogg"
        )
    )
    await state.update_data(thread_id=thread_id)
    
# @router.message(F.text)
# async def handle_voice(message: types.Message):
#     msg = await message.answer('пожалуйста, подождите...')
#     text = message.text
#     bytes_voice = await OpenAIService.text_to_speech(text)
    
#     await message.answer_voice(
#         BufferedInputFile(
#             bytes_voice,
#             filename="voice.ogg"
#         )
#     )

@router.message(F.photo)
async def handle_voice(message: types.Message, state: FSMContext):
    msg = await message.answer('пожалуйста, подождите...')
    await bot.send_chat_action(message.chat.id, 'record_voice')
    photo = message.photo[-1]
    bytes_image: io.BytesIO = await bot.download(photo)

    fsm_data = await state.get_data()
    thread_id = fsm_data.get('thread_id')

    encrypt_imgage = await OpenAIService.get_response_by_image(bytes_image)
    print(encrypt_imgage)
    response, thread_id = await OpenAIService.get_assistant_response(thread_id, encrypt_imgage)
    bytes_voice = await OpenAIService.text_to_speech(response)
    print(thread_id)
    await msg.delete()
    await message.answer_voice(
        BufferedInputFile(
            bytes_voice,
            filename="voice.ogg"
        )
    )
    await state.update_data(thread_id=thread_id)

@router.message(Command('/clear'))
async def delete_history(message: types.Message, state: FSMContext):
    await state.clear()
    reply_text = "История удалена"
    await message.answer(text=reply_text)
