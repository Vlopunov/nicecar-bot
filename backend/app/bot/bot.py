from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import settings

bot = Bot(token=settings.BOT_TOKEN, parse_mode=ParseMode.HTML) if settings.BOT_TOKEN else None
dp = Dispatcher(storage=MemoryStorage())
