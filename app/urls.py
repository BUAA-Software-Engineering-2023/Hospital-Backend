from django.urls import path
from .views import DepartmentList, DoctorList,NotificationList,CarouselMapList,NewsList,VacancyList,DoctorDetail

urlpatterns = [
    path('api/departmentList', DepartmentList.as_view()),
    path('api/doctorList', DoctorList.as_view()),
    path('api/notificationList', NotificationList.as_view()),
    path('api/carouselList',CarouselMapList.as_view()),
    path('api/newsList',NewsList.as_view()),
    path('api/vacancyList',VacancyList.as_view()),
    path('api/doctorDetail/<slug:doctor_id>', DoctorDetail.as_view()),
]
