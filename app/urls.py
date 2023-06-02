from django.urls import path
from .views import DepartmentList, DoctorList, NotificationList, CarouselMapList, NewsList, VacancyList, DoctorDetail, \
    PatientList, UserInfo, PatientDetail, UserView, SendCode, LoginCode, LoginPassWd, MakeAppointment, MakeMedicalRecord \
    , MakeLeave, CancelLeave, LeaveList, VacancyDetail, PatientWaiting, PatientAppointment, CancelAppointment, \
    GetMedicalRecord, AddPatient, DeletePatient, UpdatePatient, UploadAvatar, GetMessage, UnreadMessage, ReadMessage, \
    Pay, GetPaymentStatus, PaymentList,NotificationDetail,NewsDetail,ChangePassword,ChangePhone

urlpatterns = [
    path('api/departmentList', DepartmentList.as_view()),  # API endpoint for retrieving a list of departments
    path('api/doctorList', DoctorList.as_view()),  # API endpoint for retrieving a list of doctors
    path('api/notificationList', NotificationList.as_view()),  # API endpoint for retrieving a list of notifications
    path('api/notificationDetail/<slug:notification_id>', NotificationDetail.as_view()),  # API endpoint for retrieving a list of notifications
    path('api/carouselList', CarouselMapList.as_view()),  # API endpoint for retrieving a list of carousel maps
    path('api/newsList', NewsList.as_view()),  # API endpoint for retrieving a list of news
    path('api/newsDetail/<slug:news_id>', NewsDetail.as_view()),  # API endpoint for retrieving a list of news
    path('api/vacancyList', VacancyList.as_view()),  # API endpoint for retrieving a list of vacancies
    path('api/doctorDetail/<slug:doctor_id>', DoctorDetail.as_view()),
    # API endpoint for retrieving details of a specific doctor
    path('api/patientList/', PatientList.as_view()),
    # API endpoint for retrieving a list of patients for a specific user
    path('api/userInfo', UserInfo.as_view()),
    # API endpoint for retrieving information of a specific user
    path('api/patientDetail/<slug:patient_id>', PatientDetail.as_view()),
    # API endpoint for retrieving details of a specific patient
    path('api/sendCode/<slug:phone_number>', SendCode.as_view()),# API endpoint for sending verification code to a specific phone number
    path('api/register', UserView.as_view()),  # API endpoint for user registration
    path('api/loginWithPassword', LoginPassWd.as_view()),  # API endpoint for user login with password
    path('api/changePassword', ChangePassword.as_view()),
    path('api/changePhone', ChangePhone.as_view()),
    path('api/loginWithCode', LoginCode.as_view()),  # API endpoint for user login with verification code
    path('api/makeAppointment', MakeAppointment.as_view()),
    path('api/cancelAppointment', CancelAppointment.as_view()),
    path('api/makeMedicalrecord', MakeMedicalRecord.as_view()),
    path('api/makeLeave', MakeLeave.as_view()),
    path('api/cancelLeave', CancelLeave.as_view()),
    path('api/leaveList', LeaveList.as_view()),
    path('api/vacancyDetail', VacancyDetail.as_view()),
    path('api/patientWaiting', PatientWaiting.as_view()),
    path('api/getMedicalRecord/<slug:patient_id>', GetMedicalRecord.as_view()),
    path('api/patientAppointment/<slug:patient_id>', PatientAppointment.as_view()),
    path('api/addPatient', AddPatient.as_view()),
    path('api/deletePatient', DeletePatient.as_view()),
    path('api/updatePatient/<slug:patient_id>', UpdatePatient.as_view()),
    path('api/uploadAvatar', UploadAvatar.as_view()),
    path('api/getMessage', GetMessage.as_view()),
    path('api/unreadMessage', UnreadMessage.as_view()),
    path('api/readMessage/<slug:message_id>', ReadMessage.as_view()),
    path('api/pay/<slug:payment_id>', Pay.as_view()),
    path('api/getPaymentStatus/<slug:payment_id>', GetPaymentStatus.as_view()),
    path('api/paymentList/<slug:appointment_id>', PaymentList.as_view()),
    # path('api/')
]
