from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, NonNegativeInt, PositiveInt

from app.core.constants import (
    FULL_AMOUNT_EXAMPLE,
    CHARITY_PROJECT_DESCRIPTION_MIN_LENGTH,
    CHARITY_PROJECT_NAME_MIN_LENGTH,
    CHARITY_PROJECT_NAME_MAX_LENGTH
)


class CharityProjectBase(BaseModel):
    """Базовый класс схемы, от которой наследуют все остальные."""

    name: Optional[str] = Field(
        None,
        min_length=CHARITY_PROJECT_NAME_MIN_LENGTH,
        max_length=CHARITY_PROJECT_NAME_MAX_LENGTH
    )
    description: Optional[str] = Field(
        None,
        min_length=CHARITY_PROJECT_DESCRIPTION_MIN_LENGTH
    )
    full_amount: Optional[PositiveInt] = Field(
        None,
        examples=[FULL_AMOUNT_EXAMPLE]
    )

    model_config = ConfigDict(extra='forbid')


class CharityProjectCreate(CharityProjectBase):
    """Класс схемы, описывающий создание проекта."""

    name: str = Field(
        ...,
        min_length=CHARITY_PROJECT_NAME_MIN_LENGTH,
        max_length=CHARITY_PROJECT_NAME_MAX_LENGTH
    )
    description: str = Field(
        ...,
        min_length=CHARITY_PROJECT_DESCRIPTION_MIN_LENGTH
    )
    full_amount: PositiveInt = Field(
        ...,
        examples=[FULL_AMOUNT_EXAMPLE]
    )


class CharityProjectUpdate(CharityProjectBase):
    """Класс схемы, описывающей обновление проекта."""


class CharityProjectDB(CharityProjectCreate):
    """Класс схемы, описывающей ответ на запрос."""

    id: int
    invested_amount: NonNegativeInt
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
