import io
from datetime import datetime, timedelta
from typing import List, Dict, Any
import xlsxwriter

from app.core.config import settings
from app.core.constants import NAME_FOLDER_REPORT
from app.core.yandex_client import YandexDiskClient


def format_time_delta(full_collection_time: timedelta) -> str:
    """Вычисляет количество дней, часов и минут,
    за которое был закрыт сбор по проекту.
    """
    total_seconds = int(full_collection_time.total_seconds())
    days, remainder_for_hours = divmod(total_seconds, 86400)
    hours, remainder_for_minutes = divmod(remainder_for_hours, 3600)
    minutes, remainder = divmod(remainder_for_minutes, 60)
    if not days:
        collection_time_in_format = f'{hours} ч. {minutes} мин.'
    else:
        collection_time_in_format = f'{days} дн. {hours} ч.'
    return collection_time_in_format


async def create_simple_report(
        yandex_client: YandexDiskClient,
        projects: List[Dict[str, Any]],
        folder: str = NAME_FOLDER_REPORT
) -> str:
    """Создает Excel-файл. Получите от Яндекс Диска ссылку для загрузки.
    Заполняет файл необходимыми данными из базы  в формате отчета.
    Загружает файл с отчетом на Яндекс Диск. Публикует файл
    и возвращает публичную ссылку."""
    now_date_time = datetime.now().strftime(settings.report_format)
    filename = (
        f'QRKot_Report_{now_date_time}'.replace(':', '-').replace(' ', '_')
    )
    upload_url, file_path = (
        await yandex_client.create_excel_file(filename, folder)
    )
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Отчет')

    title_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'left'
    })
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#2F75B5',
        'font_color': 'white',
        'border': 1,
        'align': 'left'
    })
    cell_format = workbook.add_format({
        'border': 1,
        'align': 'left'
    })
    total_format = workbook.add_format({
        'bold': True,
        'border': 1,
        'align': 'left'
    })
    worksheet.merge_range('A1:C1', f'Отчет от {now_date_time}', title_format)
    headers = ['Название проекта', 'Время сбора', 'Описание']
    for col, header in enumerate(headers):
        worksheet.write(1, col, header, header_format)

    for row, project in enumerate(projects, start=2):
        worksheet.write(row, 0, project['project_name'], cell_format)
        worksheet.write(
            row, 1,
            format_time_delta(project['full_collection_time']),
            cell_format
        )
        worksheet.write(row, 2, project['description'], cell_format)

    last_row = len(projects) + 2
    worksheet.merge_range(
        last_row, 0,
        last_row, 2,
        f'Всего проектов: {len(projects)}',
        total_format
    )
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 15)
    worksheet.set_column('C:C', 30)

    workbook.close()
    output.seek(0)
    await yandex_client.upload_file(upload_url, output.getvalue())
    return await yandex_client.publish_file(file_path)
