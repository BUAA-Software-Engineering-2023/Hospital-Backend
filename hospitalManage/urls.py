from django.urls import path
from .views import DepartmentManage, NotificationManage, VacancyManage, LeaveList, ProcessLeave

urlpatterns = [
    path('api/departmentManage', DepartmentManage.as_view()),
    path('api/notificationManage', NotificationManage.as_view()),
    path('api/vacancyManage', VacancyManage.as_view()),
    path('api/leaveList', LeaveList.as_view()),
    path('api/processLeave/<slug:leave_status>', ProcessLeave.as_view())
]
