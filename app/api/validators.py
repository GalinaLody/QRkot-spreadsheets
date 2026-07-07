from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core. constants import COMMON_MIXIN_INVESTED_AMOUNT_DEFAULT
from app.crud.charity_project import charity_project_crud
from app.models.charity_project import CharityProject


async def check_unique_name(
        project_name: str,
        session: AsyncSession,
) -> None:
    """Проверяет уникальность имени проекта."""
    project_id = await charity_project_crud.get_project_by_name(
        project_name, session
    )
    if project_id is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!'
        )


async def check_project_exists(
        project_id: int,
        session: AsyncSession,
) -> CharityProject:
    """Проверяет наличие проекта в базе данных."""
    charity_project = await charity_project_crud.get(project_id, session)
    if charity_project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден!'
        )
    return charity_project


async def check_project_invested_amount_exists(
        project_id: int,
        session: AsyncSession
) -> CharityProject:
    """Проверяет наличие инвестированных в проект средств."""
    charity_project = await charity_project_crud.get(project_id, session)
    if charity_project.invested_amount > COMMON_MIXIN_INVESTED_AMOUNT_DEFAULT:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
    return charity_project


async def check_project_close(
        project_id: int,
        session: AsyncSession
) -> CharityProject:
    """Проверяет состояние проекта (открыт или закрыт)."""
    charity_project = await charity_project_crud.get(project_id, session)
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!'
        )
    return charity_project


async def check_full_amount_less_than_invested_amount(
        project_id: int,
        new_full_amount: int,
        session: AsyncSession
):
    """Проверяет, чтобы новая сумма full_amount была больше вложенной суммы."""
    charity_project = await charity_project_crud.get(project_id, session)
    if new_full_amount < charity_project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=(
                'Нелья установить значение full_amount'
                'меньше уже вложенной суммы.'
            )
        )
