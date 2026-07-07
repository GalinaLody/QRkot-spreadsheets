from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, NonNegativeInt

from app.core.constants import FULL_AMOUNT_EXAMPLE


class DonationBase(BaseModel):
    """Базовый класс схемы, от которой наследуют все остальные."""

    full_amount: PositiveInt = Field(..., examples=[FULL_AMOUNT_EXAMPLE])
    comment: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


class DonationCreate(DonationBase):
    """Класс схемы, описывающий создание проекта."""


class DonationDB(DonationBase):
    """Класс схемы, описывающей ответ на запрос."""

    id: int
    create_date: datetime

    model_config = ConfigDict(from_attributes=True)


class DonationFullInfoDB(DonationDB):
    """Класс схемы, описывающей ответ на запрос
    получения списка всех объектов.
    """

    user_id: int
    invested_amount: NonNegativeInt
    fully_invested: bool
    close_date: Optional[datetime]
