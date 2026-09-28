from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router, BaseMiddleware, F
from aiogram.types import Message, BotCommand, ReplyKeyboardMarkup, KeyboardButton, FSInputFile
from aiogram.filters import CommandStart, Command
from typing import Any, Awaitable, Callable
from pathlib import Path

import os, logging, asyncio, sys

class LoggingMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:

        print(
            f"ID: {event.from_user.id} | "
            f"Username: @{event.from_user.username} | "
            f"Text: {event.text}"
        )

        return await handler(event, data)

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Плагины"),
            KeyboardButton(text="Помощь"),
        ],
    ],
    resize_keyboard=True,
)

FILES_DIR = Path("plugins")


def get_files():
    return sorted(
        [
            file
            for file in FILES_DIR.iterdir()
            if file.is_file()
        ],
        key=lambda file: file.name.lower()
    )


load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

router = Router()
router.message.middleware(LoggingMiddleware())

@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f'Привет, {message.from_user.full_name}! '  
                         'Это телеграм бот для управления исходниками крутого перца айдара',
        reply_markup=main_keyboard)
    

@router.message(F.text=="Плагины")
async def get_plugins_handler(message: Message):
    files = get_files()
    if not files:
        await message.answer("В папке пока нет плагинов.")
        return

    text = "Доступные файлы:\n\n"

    for number, file in enumerate(files, start=1):
        text += f"{number})   {file.stem}\n"

    text += "\nОтправьте номер плагина"

    await message.answer(text)
    
    
@router.message(F.text=="Помощь")
async def help_handler(message: Message):
    await message.answer("По всем вопросам обращаться:\n\n@CarrmA56 - владелец\n@rccun - разработчик")

@router.message(F.text.regexp(r"^\d+$"))
async def send_file_handler(message: Message):
    files = get_files()

    number = int(message.text)

    if number < 1 or number > len(files):
        await message.answer("Файла с таким номером нет.")
        return

    selected_file = files[number - 1]

    try:
        await message.answer_document(
            document=FSInputFile(selected_file), caption="Выбранный плагин"
        )
    except Exception as e:
        await message.answer(
            f"Ошибка при отправке файла:\n\n"
            f"{type(e).__name__}: {e}"
        )

@router.message()
async def message_handler(messaage: Message):
    await messaage.answer("Неизвестная команда или сообщение")


async def main() -> None:
    bot = Bot(token=BOT_TOKEN)
    await bot.set_my_commands([
        BotCommand(
            command="start",
            description="Запустить бота"
        ),])
    dp = Dispatcher()
    dp.include_router(router)
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
