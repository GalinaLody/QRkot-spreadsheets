from typing import Optional

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import CommonMixin, ProjectDonationBase


class Donation(CommonMixin, ProjectDonationBase):
    """Описывает данные об отдельном пожертвовании."""

    comment: Mapped[Optional[str]] = mapped_column(String())
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.id', name='fk_donation_user_id_user'),
        nullable=True
    )
