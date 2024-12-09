from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import API_KEY

bot = Bot(token=API_KEY)
dp = Dispatcher(storage=MemoryStorage())
