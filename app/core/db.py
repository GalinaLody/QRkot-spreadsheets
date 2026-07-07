from datetime import datetime

from sqlalchemy import CheckConstraint, Boolean, DateTime, Integer, MetaData
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import (
    DeclarativeBase, declared_attr, Mapped, mapped_column
)

from app.core.config import settings
from app.core.constants import (
    COMMON_MIXIN_FULL_AMOUNT_MIN_VALUE, COMMON_MIXIN_INVESTED_AMOUNT_DEFAULT
)


class Base(DeclarativeBase):
    """Базовый класс для моделей."""

    convention = {
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'ix': 'ix_%(column_0_label)s'
    }
    metadata = MetaData(naming_convention=convention)


class CommonMixin:
    """Класс-миксин для моделей.

    Имя таблиц создается из названия моделей
    в нижнем регистре.
    Добавляет в модель первичный ключ ID.

    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


class ProjectDonationBase(Base):
    """Родительский(абстрактный) класс для моделей  CharityProject и Donation.

    Добавляет в модели общие поля: full_amount, invested_amount,fully_invested
    create_date, close_date.
    """

    __abstract__ = True
    full_amount: Mapped[int] = mapped_column(
        Integer(),
        CheckConstraint(
            f'full_amount > {COMMON_MIXIN_FULL_AMOUNT_MIN_VALUE}',
            name='full_amount'
        )
    )
    invested_amount: Mapped[int] = mapped_column(
        Integer(), default=COMMON_MIXIN_INVESTED_AMOUNT_DEFAULT
    )
    fully_invested: Mapped[bool] = mapped_column(Boolean(), default=False)
    create_date: Mapped[datetime] = mapped_column(
        DateTime(), default=datetime.now
    )
    close_date: Mapped[datetime] = mapped_column(DateTime(), nullable=True)


engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
