from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import CommonMixin, ProjectDonationBase
from app.core.constants import (
    CHARITY_PROJECT_NAME_MAX_LENGTH, CHARITY_PROJECT_DESCRIPTION_MIN_LENGTH
)


class CharityProject(CommonMixin, ProjectDonationBase):
    """Описывает целевые проекты по сбору пожертвований."""

    name: Mapped[str] = mapped_column(
        String(CHARITY_PROJECT_NAME_MAX_LENGTH),
        unique=True,
        nullable=False
    )
    description: Mapped[str] = mapped_column(
        String(),
        CheckConstraint(
            f'LENGTH(description) >= {CHARITY_PROJECT_DESCRIPTION_MIN_LENGTH}',
            name='description'
        ),
        nullable=False
    )
