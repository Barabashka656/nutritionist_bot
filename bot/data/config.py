import os
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN')
OPEN_AI_TOKEN = os.getenv('OPEN_AI_TOKEN')
