
from django.urls import path
from .views import LoginView,DoctorManagement,ScheduleManage

urlpatterns = [
    path('api/adminLogin', LoginView.as_view()),
    path('api/doctorManage', DoctorManagement.as_view()),
    path('api/scheduleManage', ScheduleManage.as_view()),
]