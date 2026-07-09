from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.constants import NAME_FOLDER_REPORT
from app.core.yandex_client import get_yandex_client, YandexDiskClient
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.services.yandex_api import create_simple_report

router = APIRouter()


@router.post(
    '/',
    response_model=str,
    dependencies=[Depends(current_superuser)],
    summary='Создать Excel-отчёт на Яндекс Диске',
    description="""
    Создает Excel-файл с отчётом о количестве закрытых проектов
    с указанием времени, потребовавшегося для сбора необходимой суммы
    пожертвований. Файл сохраняется на Яндекс Диске
    и становится доступен по публичной ссылке.
    """
)
async def get_report(
    session: AsyncSession = Depends(get_async_session),
    yandex_client: YandexDiskClient = Depends(get_yandex_client)
) -> str:
    """Создание отчёта в Excel-файле на Яндекс Диске."""
    projects = await charity_project_crud.get_projects_by_completion_rate(
        session=session
    )
    if not projects:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Нет данных для формирования отчёта"
        )
    try:
        return await create_simple_report(
            yandex_client, projects, NAME_FOLDER_REPORT
        )
    except Exception as error:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f'Ошибка при создании отчета: {str(error)}'
        )
