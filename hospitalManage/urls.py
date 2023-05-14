from django.urls import path
from .views import DepartmentManage, NotificationManage,VacancyManage
urlpatterns = [
    path('api/departmentManage', DepartmentManage.as_view()),
    path('api/notificationManage',NotificationManage.as_view()),
    path('api/vacancyManage',VacancyManage.as_view())
]
