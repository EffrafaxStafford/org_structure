from django.contrib import admin
from django.urls import path

from .apps import DepartmentConfig
from .views import DepartmentCreateAPIView, EmployeeCreateAPIView


app_name = DepartmentConfig.name

urlpatterns = [
    path('', DepartmentCreateAPIView.as_view()),
    path('<int:id>/employees/', EmployeeCreateAPIView.as_view()),

]
