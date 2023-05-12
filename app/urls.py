
from django.urls import path
from .views import DepartmentList
urlpatterns = [
    path('api/departmentList', DepartmentList.as_view()),
]

