import datetime
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError

from db.models import Session, User, ProductLink

router = Router()


@router.message(Command("start"))
async def start_handler(message: Message):
    """Обработчик команды /start"""
    async with Session() as session:
        try:
            # Проверяем существует ли пользователь
            result = await session.execute(
                select(User).where(User.user_id == message.from_user.id)
            )
            user = result.scalar_one_or_none()

            # Если пользователя нет - создаем
            if not user:
                new_user = User(
                    user_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                    time_start=datetime.datetime.now()
                )
                session.add(new_user)
                await session.commit()

            # Отправляем приветственное сообщение
            await message.answer(
                "/add ссылка на товар - команда добавляет ссылку на проверку\n"
                "/remove ссылка на товар - команда удаляет ссылку из проверки\n"
                "/links команда для получения актуальных ссылок"
            )

        except SQLAlchemyError as e:
            await message.answer("Произошла ошибка при работе с базой данных")
            print(f"Database error: {e}")


@router.message(Command("add"))
async def add_link_handler(message: Message):
    """Обработчик команды /add"""
    if not message.text or len(message.text.split()) < 2:
        await message.answer("Пожалуйста, укажите ссылку после команды /add")
        return

    link_url = message.text.split()[1]
    async with Session() as session:
        try:
            new_link = ProductLink(
                user_id=message.from_user.id,
                link_url=link_url
            )
            session.add(new_link)
            await session.commit()
            await message.answer("Ссылка успешно добавлена!")
        except SQLAlchemyError as e:
            await message.answer("Произошла ошибка при добавлении ссылки")
            print(f"Database error: {e}")


@router.message(Command("remove"))
async def remove_link_handler(message: Message):
    """Обработчик команды /remove"""
    if not message.text or len(message.text.split()) < 2:
        await message.answer("Пожалуйста, укажите ссылку после команды /remove")
        return

    link_url = message.text.split()[1]
    async with Session() as session:
        try:
            # Сначала проверяем, существует ли ссылка у пользователя
            result = await session.execute(
                select(ProductLink).where(
                    ProductLink.user_id == message.from_user.id,
                    ProductLink.link_url == link_url
                )
            )
            link = result.scalar_one_or_none()

            if not link:
                await message.answer("У вас нет такой ссылки в списке")
                return
            await session.execute(
                delete(ProductLink).where(
                    ProductLink.user_id == message.from_user.id,
                    ProductLink.link_url == link_url
                )
            )
            await session.commit()
            await message.answer("Ссылка успешно удалена!")
        except SQLAlchemyError as e:
            await message.answer("Произошла ошибка при удалении ссылки")
            print(f"Database error: {e}")


@router.message(Command("links"))
async def links_handler(message: Message):
    """Обработчик команды /links"""
    async with Session() as session:
        try:
            result = await session.execute(
                select(ProductLink).where(
                    ProductLink.user_id == message.from_user.id
                )
            )
            links = result.scalars().all()

            if not links:
                await message.answer("У вас нет добавленных ссылок")
                return

            links_text = "Ваши ссылки:\n\n" + "\n".join(
                [f"• {link.link_url}" for link in links]
            )
            await message.answer(links_text)

        except SQLAlchemyError as e:
            await message.answer("Произошла ошибка при получении ссылок")
            print(f"Database error: {e}")
