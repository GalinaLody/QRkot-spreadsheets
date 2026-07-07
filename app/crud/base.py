from typing import Optional

from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import COMMON_MIXIN_INVESTED_AMOUNT_DEFAULT
from app.models import User
from app.services.invested import investment_process


class CRUDBase:
    """Базовый класс для CRUD-операци."""

    def __init__(self, model):
        self.model = model

    async def create(
        self,
        obj_in_request,
        session: AsyncSession,
        commit: bool = True,
        user: Optional[User] = None
    ):
        """Универсальный метод для создания объектов заданной модели."""
        obj_in_data = obj_in_request.model_dump()
        if user is not None:
            obj_in_data['user_id'] = user.id
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        if commit:
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def create_with_investment_process(
            self,
            obj_in_request,
            session: AsyncSession,
            invest_model,
            user: Optional[User] = None
    ):
        """Универсальный метод создания объекта с запуском
        процесса инвестирования.
        """
        obj_db = await self.create(obj_in_request, session, commit=False)
        obj_db.invested_amount = COMMON_MIXIN_INVESTED_AMOUNT_DEFAULT
        open_uninvested_objects = await session.execute(
            select(invest_model).where(
                invest_model.fully_invested.is_(False)
            ).order_by(asc(invest_model.create_date))
        )
        open_uninvested_objects = open_uninvested_objects.scalars().all()
        investment_process(obj_db, open_uninvested_objects)
        await session.commit()
        await session.refresh(obj_db)
        return obj_db

    async def get_multi(
        self,
        session: AsyncSession
    ):
        """Универсальный метод для получения всех объектов заданной модели."""
        db_objs = await session.execute(select(self.model))
        return db_objs.scalars().all()

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ):
        """Универсальный метод для получения объекта по его id."""
        db_obj = await session.execute(
            select(self.model).where(
                self.model.id == obj_id
            )
        )
        return db_obj.scalars().first()

    async def update(
        self,
        db_obj,
        obj_in,
        session: AsyncSession,
    ):
        """Универсальный метод для обновления записи по id."""
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        db_obj,
        session: AsyncSession,
    ):
        """Универсальный метод для удаления объекта."""
        await session.delete(db_obj)
        await session.commit()
        return db_obj
