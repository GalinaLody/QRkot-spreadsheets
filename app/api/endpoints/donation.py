from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user, current_superuser
from app.crud.donation import donation_crud
from app.crud.charity_project import CharityProject
from app.models.donation import Donation
from app.models import User
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB

router = APIRouter()

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.get(
    '/',
    response_model=list[DonationFullInfoDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
    responses={
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
async def get_all_donations(
    session: SessionDep
):
    """Показать список всех пожертвований.

    Доступно только суперпользователю.
    """
    all_donations = await donation_crud.get_multi(session)
    return all_donations


@router.get(
    '/my',
    response_model=list[DonationDB],
    responses={
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
    }
)
async def get_user_donations(
    session: SessionDep,
    user: Annotated[User, Depends(current_user)]
):
    """Получение всех пожертвовани для пользователя,
    выполнившего запрос. Доступно только зарегистрированному пользователю.
    """
    donations = await donation_crud.get_by_user(session, user)
    return donations


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
    responses={
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
    }
)
async def donation_create(
    new_donation: DonationCreate,
    session: SessionDep,
    user: Annotated[User, Depends(current_user)]
) -> Donation:
    """Создать пожертвование.

    Доступно только зарегистрированному пользователю.
    """
    donation_db = (
        await donation_crud.create_with_investment_process(
            new_donation, session, CharityProject, user
        )
    )
    return donation_db
