
from django.urls import path
from .views import LoginView,DoctorManagement,ScheduleManage,DepartmentManage, NotificationManage, VacancyManage, LeaveList, ProcessLeave


urlpatterns = [
    path('api/adminLogin', LoginView.as_view()),
    path('api/doctorManage', DoctorManagement.as_view()),
    path('api/scheduleManage', ScheduleManage.as_view()),
    path('api/departmentManage', DepartmentManage.as_view()),
    path('api/notificationManage', NotificationManage.as_view()),
    path('api/vacancyManage', VacancyManage.as_view()),
    path('api/leaveList', LeaveList.as_view()),
    path('api/processLeave/<slug:leave_status>', ProcessLeave.as_view())
]
