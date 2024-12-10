from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from config import API_KEY

session = AiohttpSession(timeout=60)  # Увеличиваем таймаут до 60 секунд
bot = Bot(token=API_KEY)
dp = Dispatcher(storage=MemoryStorage())
