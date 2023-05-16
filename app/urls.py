from django.urls import path
from .views import DepartmentList, DoctorList, NotificationList, CarouselMapList, NewsList, VacancyList, DoctorDetail, \
    PatientList, UserInfo, PatientDetail, UserView, SendCode,LoginCode,LoginPassWd

urlpatterns = [
    path('api/departmentList', DepartmentList.as_view()),  # API endpoint for retrieving a list of departments
    path('api/doctorList', DoctorList.as_view()),  # API endpoint for retrieving a list of doctors
    path('api/notificationList', NotificationList.as_view()),  # API endpoint for retrieving a list of notifications
    path('api/carouselList', CarouselMapList.as_view()),  # API endpoint for retrieving a list of carousel maps
    path('api/newsList', NewsList.as_view()),  # API endpoint for retrieving a list of news
    path('api/vacancyList', VacancyList.as_view()),  # API endpoint for retrieving a list of vacancies
    path('api/doctorDetail/<slug:doctor_id>', DoctorDetail.as_view()),
    # API endpoint for retrieving details of a specific doctor
    path('api/patientList/<slug:user_id>', PatientList.as_view()),
    # API endpoint for retrieving a list of patients for a specific user
    path('api/userInfo/<slug:user_id>', UserInfo.as_view()),
    # API endpoint for retrieving information of a specific user
    path('api/patientDetail/<slug:patient_id>', PatientDetail.as_view()),
    # API endpoint for retrieving details of a specific patient
    path('api/sendCode/<slug:phone_number>', SendCode.as_view()),
    # API endpoint for sending verification code to a specific phone number
    path('api/register', UserView.as_view()),  # API endpoint for user registration
    path('api/loginWithPasswd', LoginPassWd.as_view()),  # API endpoint for user login with password
    path('api/loginWithCode', LoginCode.as_view()),  # API endpoint for user login with verification code

]
