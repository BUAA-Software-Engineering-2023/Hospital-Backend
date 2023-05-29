from django.urls import path
from .views import LoginView, DoctorManagement, ScheduleManage, DepartmentManage, NotificationManage, VacancyManage, \
    LeaveListManage, ProcessLeave, vacancy_check, DoctorImage, VacancySettingManage, UploadImage, NewsManage,ChangeAdminPasswd,AdminIntroduction

urlpatterns = [
    #
    path('api/adminLogin', LoginView.as_view()),
    path('api/changeAdminPasswd', ChangeAdminPasswd.as_view()),
    #
    path('api/doctorManage', DoctorManagement.as_view()),
    #
    path('api/scheduleManage', ScheduleManage.as_view()),
    path('api/adminIntroduction', AdminIntroduction.as_view()),
    #
    path('api/departmentManage', DepartmentManage.as_view()),
    #
    path('api/notificationManage', NotificationManage.as_view()),
    #
    path('api/vacancySettingManage', VacancySettingManage.as_view()),
    #
    path('api/leaveListManage', LeaveListManage.as_view()),
    path('api/processLeave/<slug:leave_status>', ProcessLeave.as_view()),
    path('api/doctorImage/<slug:doctor_id>', DoctorImage.as_view()),
    path('api/testcheck', vacancy_check),
    path('api/uploadImage', UploadImage.as_view()),
    path('api/newsManage', NewsManage.as_view())
]
