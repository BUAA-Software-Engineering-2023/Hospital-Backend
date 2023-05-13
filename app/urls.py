from django.urls import path
from .views import DepartmentList, DoctorList,NotificationList,CarouselMapList,NewsList,VacancyList,DoctorDetail,PatientList,UserInfo

urlpatterns = [
    path('api/departmentList', DepartmentList.as_view()),
    path('api/doctorList', DoctorList.as_view()),
    path('api/notificationList', NotificationList.as_view()),
    path('api/carouselList',CarouselMapList.as_view()),
    path('api/newsList',NewsList.as_view()),
    path('api/vacancyList',VacancyList.as_view()),
    path('api/doctorDetail/<slug:doctor_id>', DoctorDetail.as_view()),
    path('api/patientList/<slug:user_id>', PatientList.as_view()),
    #显示指定用户的用户信息（get）
    path('api/userInfo/<slug:user_id>', UserInfo.as_view()),
    # path('api/login', UserInfo.as_view()),
    # path('api/register', UserInfo.as_view()),
]
