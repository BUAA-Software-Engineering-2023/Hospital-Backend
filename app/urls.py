from django.urls import path
from .views import DepartmentList, DoctorList, NotificationList

urlpatterns = [
    path('api/departmentList', DepartmentList.as_view()),
    path('api/doctorList', DoctorList.as_view()),
    path('api/notificationList',NotificationList.as_view()),
    # path('api/carouselList'),
    # path('api/newsList'),
    # path('api/doctorDetail'),
    # path('api/vacancyList')
]
