from datetime import datetime
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_unique_name, check_project_exists,
    check_project_invested_amount_exists, check_project_close,
    check_full_amount_less_than_invested_amount
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.models.donation import Donation
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)


router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,

)
async def get_all_projects(
    session: SessionDep,
):
    """Показать список всех целевых проектов."""
    all_projects = await charity_project_crud.get_multi(session)
    return all_projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
    responses={
        HTTPStatus.BAD_REQUEST: {
            'description': (
                'Неправильные операции.'
            ),
            'content': {
                'application/json': {
                    'examples': {
                        'name_exists': {
                            'summary': (
                                'Неуникальное имя'
                            ),
                            'value': {
                                'detail': (
                                    'Проект с таким именем уже существует!'
                                )
                            }
                        },
                    }
                }
            }
        },
        HTTPStatus.UNAUTHORIZED: {
            'description': (
                'Неавторизованный пользователь.'
            ),
            'content': {
                'application/json': {
                    'example': {'detail': ('string')}
                }
            }
        },
        HTTPStatus.FORBIDDEN: {
            'description': (
                'Не суперпользователь.'
            ),
            'content': {
                'application/json': {
                    'example': {'detail': ('string')}
                }
            }
        },
    }
)
async def new_project_create(
        new_project: CharityProjectCreate,
        session: SessionDep,
):
    """Создать целевой проект.

    Создание доступно только суперпользователю.
    """
    await check_unique_name(new_project.name, session)
    project_db = (
        await charity_project_crud.create_with_investment_process(
            new_project, session, Donation
        )
    )
    return project_db


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
    responses={
        HTTPStatus.BAD_REQUEST: {
            'description': (
                'Неправильные операции.'
            ),
            'content': {
                'application/json': {
                    'examples': {
                        'invested': {
                            'summary': (
                                'full_amount меньше вложенной суммы'
                            ),
                            'value': {
                                'detail': (
                                    'Нелья установить значение full_amount'
                                    ' меньше уже вложенной суммы.'
                                )
                            }
                        },
                        'name_exists': {
                            'summary': (
                                'Неуникальное имя'
                            ),
                            'value': {
                                'detail': (
                                    'Проект с таким именем уже существует!'
                                )
                            }
                        },
                        'close_project': {
                            'summary': (
                                'Закрытый проект'
                            ),
                            'value': {
                                'detail': (
                                    'Закрытый проект нельзя редактировать!'
                                )
                            }
                        }
                    }
                }
            }
        },
        HTTPStatus.UNAUTHORIZED: {
            'description': (
                'Неавторизованный пользователь.'
            ),
            'content': {
                'application/json': {
                    'example': {'detail': ('string')}
                }
            }
        },
        HTTPStatus.FORBIDDEN: {
            'description': (
                'Не суперпользователь.'
            ),
            'content': {
                'application/json': {
                    'example': {'detail': ('string')}
                }
            }
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Проект не найден.',
            'content': {
                'application/json': {
                    'examples': {
                        'invested': {
                            'summary': 'Не найден проект',
                            'value': {
                                'detail': 'Проект не найден!'
                            }
                        }
                    }
                }
            }
        }
    }
)
async def partial_update_project(
    project_id: int,
    obj_in_request: CharityProjectUpdate,
    session: SessionDep
):
    """Редактировать целевой проект.

    Редактирование доступно только суперпользователю.
    Закрытый проект нельзя редактировать; нельзя установить требуемую сумму
    меньше уже вложенной.
    """
    await check_project_exists(project_id, session)
    project = await check_project_close(project_id, session)
    if obj_in_request.name is not None:
        await check_unique_name(obj_in_request.name, session)
    if obj_in_request.full_amount is not None:
        await check_full_amount_less_than_invested_amount(
            project_id, obj_in_request.full_amount, session
        )
        if obj_in_request.full_amount == project.invested_amount:
            project.fully_invested = True
            project.close_date = datetime.now()
    project = await charity_project_crud.update(
        project, obj_in_request, session
    )
    return project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
    responses={
        HTTPStatus.BAD_REQUEST: {
            'description': (
                'Нельзя удалять закрытый проект или проект,'
                'в который уже были инвестированы средства.'
            ),
            'content': {
                'application/json': {
                    'examples': {
                        'invested': {
                            'summary': (
                                'Были внесены средства и(или) проект закрыт'
                            ),
                            'value': {
                                'detail': (
                                    'В проект были внесены средства,'
                                    'не подлежит удалению!'
                                )
                            }
                        }
                    }
                }
            }
        },
        HTTPStatus.UNAUTHORIZED: {
            'description': (
                'Неавторизованный пользователь.'
            ),
            'content': {
                'application/json': {
                    'example': {'detail': ('string')}
                }
            }
        },
        HTTPStatus.FORBIDDEN: {
            'description': (
                'Не суперпользователь.'
            ),
            'content': {
                'application/json': {
                    'example': {'detail': ('string')}
                }
            }
        },
        HTTPStatus.NOT_FOUND: {
            'description': 'Проект не найден.',
            'content': {
                'application/json': {
                    'examples': {
                        'invested': {
                            'summary': 'Не найден проект',
                            'value': {
                                'detail': 'Проект не найден!'
                            }
                        }
                    }
                }
            }
        }
    }
)
async def delete_charity_project(
    project_id: int,
    session: SessionDep,
):
    """Удалить целевой проект.

    Удаление доступно только суперпользователю.
    Нельзя удалить проект, в который уже были инвестированы средства.
    """
    charity_project = await check_project_exists(
        project_id, session
    )
    charity_project = await check_project_invested_amount_exists(
        project_id, session
    )
    charity_project = await charity_project_crud.remove(
        charity_project, session
    )
    return charity_project
