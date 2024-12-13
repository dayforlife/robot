from django.urls import path
from .views import create_robot, generate_production_report

urlpatterns = [
    path('api/create_robot/', create_robot, name='create_robot'),
    path('api/production_report/', generate_production_report, name='production_report'),
]