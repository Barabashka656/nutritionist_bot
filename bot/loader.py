from bot.data.config import OPEN_AI_TOKEN, TELEGRAM_API_TOKEN

from aiogram import Bot
from aiogram import Dispatcher
from openai import AsyncOpenAI, OpenAI

bot = Bot(token=TELEGRAM_API_TOKEN)
dp = Dispatcher()
client = AsyncOpenAI(api_key=OPEN_AI_TOKEN)
