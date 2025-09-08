from sqlalchemy import Column, Integer, String, DateTime, Boolean, BigInteger, Float, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship

# Настройка асинхронного подключения к SQLite3
DB_URL = "sqlite+aiosqlite:///db/database.db"
engine = create_async_engine(DB_URL)  # Асинхронный движок SQLAlchemy
Session = async_sessionmaker(expire_on_commit=False, bind=engine)  # Фабрика сессий


class Base(DeclarativeBase, AsyncAttrs):
    """Базовый класс для декларативных моделей с поддержкой асинхронных атрибутов"""
    pass


class User(Base):
    """Модель для хранения запросов на подписку"""
    __tablename__ = "user"

    user_id = Column(BigInteger, primary_key=True)  # ID пользователя Telegram
    username = Column(String, nullable=True)  # @username пользователя
    first_name = Column(String, nullable=True)  # Имя пользователя
    last_name = Column(String, nullable=True)  # Фамилия пользователя
    user_is_block = Column(Boolean, default=False)  # Флаг блокировки пользователя
    time_start = Column(DateTime, nullable=True)  # Время начала работы


class ProductLink(Base):
    """Модель для хранения ссылок на товары пользователей"""
    __tablename__ = "product_link"

    link_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id"), nullable=False)
    link_url = Column(String, nullable=False)
    name = Column(String, nullable=True)
    price = Column(Integer, nullable=True)

    # Связь с пользователем
    user = relationship("User")


async def create_tables():
    """Создает таблицы в базе данных"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
