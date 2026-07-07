from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_project_by_name(
            self,
            project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        """Метод получения объекта модели(проекта) по атрибуту name."""
        db_project_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        return db_project_id.scalars().first()

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession
    ) -> list[dict[str, int]]:
        """Метод получает все закрытые проекты и списком возвращает
        данные о каждом проекте:
        - наименование проекта;
        - время, потраченное на сбор полной суммы подертвований;
        - описание проекта."""
        projects = await session.execute(
            select(
                CharityProject.name,
                CharityProject.create_date,
                CharityProject.close_date,
                CharityProject.description
            ).where(
                CharityProject.fully_invested
            ).order_by(CharityProject.close_date - CharityProject.create_date)
        )
        projects = projects.all()
        data = [
            {
                'project_name': project_name,
                'full_collection_time': (close_date - create_date),
                'description': description
            }
            for project_name, create_date, close_date, description in projects
        ]
        return data


charity_project_crud = CRUDCharityProject(CharityProject)
