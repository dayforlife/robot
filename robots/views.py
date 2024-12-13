from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Robot
from django.core.exceptions import ValidationError
from django.utils.dateparse import parse_datetime

from django.http import HttpResponse
from openpyxl import Workbook
from django.utils.timezone import now, timedelta
from .models import Robot

@api_view(["POST"])
def create_robot(request):
    # Проверяем наличие данных в запросе
    data = request.data

    if not isinstance(data, dict):
        return Response({"error": "Invalid JSON format."}, status=status.HTTP_400_BAD_REQUEST)

    # Извлекаем поля
    model = data.get("model")
    version = data.get("version")
    created = data.get("created")

    # Проверяем наличие обязательных полей
    if not all([model, version, created]):
        return Response({"error": "Missing required fields: 'model', 'version', 'created'."}, status=status.HTTP_400_BAD_REQUEST)

    # Ограничения для model и version из модели Robot
    if len(model) > 2 or len(version) > 2:
        return Response({"error": "'model' and 'version' must be at most 2 characters long."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Парсим дату
        created_datetime = parse_datetime(created)
        if not created_datetime:
            raise ValueError("Invalid datetime format.")

        # Создаем запись в БД
        robot = Robot.objects.create(model=model, version=version, created=created_datetime)

        return Response({"message": "Robot created successfully.", "id": robot.id}, status=status.HTTP_201_CREATED)

    except ValueError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except ValidationError as e:
        return Response({"error": e.message}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    






def generate_production_report(request):
    # Создаем Excel-файл
    wb = Workbook()
    sheet = wb.active
    sheet.title = "Отчет по производству"

    # Получаем данные за последнюю неделю
    last_week = now() - timedelta(days=7)
    robots = Robot.objects.filter(created__gte=last_week)

    # Группируем данные по модели и версии
    grouped_data = {}
    for robot in robots:
        key = (robot.model, robot.version)
        grouped_data[key] = grouped_data.get(key, 0) + 1

    if grouped_data:
        # Добавляем заголовки
        sheet.append(["Модель", "Версия", "Количество за неделю"])

        # Добавляем данные
        for (model, version), count in grouped_data.items():
            sheet.append([model, version, count])
    else:
        # Если данных нет, добавляем сообщение
        sheet.append(["За последнюю неделю не найдено записей."])

    # Сохраняем в HTTP-ответ
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = f'attachment; filename="production_report_{now().strftime("%Y%m%d")}.xlsx"'
    wb.save(response)
    return response