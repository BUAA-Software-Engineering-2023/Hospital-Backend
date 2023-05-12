from django.urls import path
from .views import DepartmentList, DoctorList,NotificationList,CarouselMapList,NewsList,VacancyList

urlpatterns = [
    path('api/departmentList', DepartmentList.as_view()),
    path('api/doctorList', DoctorList.as_view()),
    path('api/notificationList', NotificationList.as_view()),
    path('api/carouselList',CarouselMapList.as_view()),
    path('api/newsList',NewsList.as_view()),
    # path('api/doctorDetail'),
    path('api/vacancyList',VacancyList.as_view())
]
