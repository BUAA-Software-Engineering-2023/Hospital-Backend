from django.urls import path
from .views import DepartmentList, DoctorList,NotificationList,CarouselMapList

urlpatterns = [
    path('api/departmentList', DepartmentList.as_view()),
    path('api/doctorList', DoctorList.as_view()),
    # path('api/notificationList',),
    path('api/carouselList',CarouselMapList.as_view()),
    # path('api/newsList'),
    # path('api/doctorDetail'),
    # path('api/vacancyList')
]
