import random
import string

from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .models import Department, Doctor, Notification, CarouselMap, News, Vacancy, Schedule, Patient, User, \
    MedicalRecord, Code
import json
from datetime import datetime, timedelta


# Create your views here.

class DepartmentList(View):
    def get(self, request):
        type = []
        data = Department.objects.values('department_type').distinct()
        for obj in data:
            child = []
            b = Department.objects.filter(department_type=obj.get('department_type')).values('department_name',
                                                                                             'department_id')
            for c in b:
                child.append({
                    "id": c.get('department_id'),
                    "name": c.get('department_name')
                })
            print()
            type.append({
                "name": obj.get('department_type'),
                "children": child
            })
            response = {
                'result': 1,
                'data': data
            }

            return JsonResponse(response)


class DoctorList(View):
    def get(self, request):
        keyword = request.GET.get('keyWord')

        # Filter doctors by keyword if provided
        if keyword:
            doctors = Doctor.objects.filter(doctor_name__icontains=keyword)
        else:
            doctors = Doctor.objects.all()

        # Serialize doctor objects to JSON
        data = []
        for doctor in doctors:
            doctor_data = {
                'id': doctor.doctor_id,
                'name': doctor.doctor_name,
                'department': doctor.department_id.department_name,
                'image': doctor.doctor_image.url if doctor.doctor_image else None,
                'introduction': doctor.doctor_introduction
            }
            data.append(doctor_data)

        response = {
            'result': 1,
            'data': data
        }

        return JsonResponse(response)


class NotificationList(View):
    def get(self, request):
        notifications = Notification.objects.all()

        # Serialize notification objects to JSON
        data = []
        for notification in notifications:
            notification_data = {
                'id': notification.notification_id,
                'title': notification.title,
                'link': notification.notification_link,
                'date': notification.notification_time,
            }
            data.append(notification_data)

        response = {
            'result': 1,
            'data': data
        }
        return JsonResponse(response)


class DoctorDetail(View):
    def get(self, request, doctor_id):
        try:
            doctor = Doctor.objects.get(doctor_id=doctor_id)
            schedules = Schedule.objects.filter(doctor_id=doctor_id).values('schedule_day')
            schedules_data = []
            for schedule in schedules:
                schedules_data.append(schedule['schedule_day'])
            data = {
                "id": doctor.doctor_id,
                "name": doctor.doctor_name,
                "department": doctor.department_id.department_name,
                'image': doctor.doctor_image.url if doctor.doctor_image else None,
                "introduction": doctor.doctor_introduction,
                "available": schedules_data
            }
            response = {
                "result": 1,
                "data": data
            }
            return JsonResponse(response)
        except Doctor.DoesNotExist:
            response = {
                "result": 0,
                "message": "Doctor does not exist."
            }
            return JsonResponse(response)


class CarouselMapList(View):
    def get(self, request):
        carousel_maps = CarouselMap.objects.all()

        # Serialize notification objects to JSON
        data = []
        for carousel_map in carousel_maps:
            carousel_map_data = {
                'id': carousel_map.carousel_map_id,
                'img': carousel_map.carousel_map_img,
                'link': carousel_map.carousel_map_link,

            }
            data.append(carousel_map_data)

        response = {
            'result': 1,
            'data': data
        }
        return JsonResponse(response)


class NewsList(View):
    def get(self, request):
        news = News.objects.all()

        # Serialize notification objects to JSON
        data = []
        for new in news:
            news_data = {
                'id': new.news_id,
                'title': new.news_title,
                'link': new.news_link,
                'date': new.news_date,
            }
            data.append(news_data)

        response = {
            'result': 1,
            'data': data
        }
        return JsonResponse(response)


class VacancyList(View):
    def get(self, request):
        data = []
        departmentId = request.GET.get('department')
        date = request.GET.get('date')
        doctor_id_list = Vacancy.objects.filter(start_time__contains=date).values('doctor_id').distinct()
        for doctor_id in doctor_id_list:
            doctor_id = doctor_id['doctor_id']
            doctor_info = Doctor.objects.get(doctor_id=doctor_id)
            vacancies = Vacancy.objects.filter(start_time__contains=date, doctor_id=doctor_id).values('vacancy_count',
                                                                                                      'start_time')
            available = []
            for vacancy in vacancies:
                available.append({"time": vacancy['start_time'], "num": vacancy['vacancy_count']})
            data.append({
                "id": doctor_id,
                "name": doctor_info.doctor_name,
                "department": Department.objects.get(department_id=departmentId).department_name,
                "image": '',
                "introduction": doctor_info.doctor_introduction,
                "available|1-2": available
            })

        response = {
            "result": "1",
            "data": data,
        }
        return JsonResponse(response)


class PatientList(View):
    def get(self, request, user_id):
        try:
            data = []
            patients = Patient.objects.filter(user_id=user_id).values('patient_gender', 'patient_name', 'phone_number',
                                                                      'identification', 'absence', 'address',
                                                                      'patient_id')
            for patient in patients:
                info = {
                    "id": patient['patient_id'],
                    "name": patient['patient_name'],
                    "gender": patient['patient_gender'],
                    "identification": patient['identification'],
                    "phone": patient['phone_number'],
                    "cnt": patient['absence'],
                    'address': patient['address'],
                }

                data.append(info)
            response = {
                "result": "1",
                "data": data
            }
            return JsonResponse(response)
        except:
            response = {
                "result": "0"
            }
            return JsonResponse(response)


class UserInfo(View):
    def get(self, request, user_id):
        try:
            data = []
            users = User.objects.filter(user_id=user_id).values('phone_number')
            for user in users:
                info = {
                    "phone": user['phone_number'],
                }
                data.append(info)

            response = {
                "result": "1",
                "data": data
            }
            return JsonResponse(response)

        except:
            response = {
                "result": "0"
            }
            return JsonResponse(response)


def generate_verification_code():
    characters = string.digits + string.ascii_letters
    code = ''.join(random.choice(characters) for _ in range(6))
    return code


class SendCode(View):
    def get(self, request, phone_number):
        verification_code = generate_verification_code()
        date_time = datetime.now()
        info = Code.objects.get(phone_number=phone_number)
        if info is None:
            pass
        else:
            Code.delete(info)
        code = Code(
            verification_code=verification_code,
            phone_number=phone_number,
            create_time=date_time,
            expire_time=date_time + timedelta(minutes=30)
        )
        code.save()
        return JsonResponse({"result": 1, 'message': 'Code sent successfully'})


class UserView(View):
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        phone_number = json_obj['phone_number']
        password = json_obj['password']
        verification_code = json_obj['verification_code']
        info = Code.objects.get(phone_number=phone_number)
        if info.verification_code == verification_code:
            user = User(
                phone_number=phone_number,
                passwd=password,
            )
            user.save()
            return JsonResponse({'message': 'User registered successfully'})
        else:
            return JsonResponse({'result': 0, 'message': "Wrong code"})


class PatientDetail(View):
    def get(self, request, patient_id):
        patient = Patient.objects.get(patient_id=patient_id)
        medical_records = MedicalRecord.objects.filter(patient_id=patient_id)
        medical_records_data = []
        for medical_record in medical_records:
            medical_records_data.append({
                "medical_record_date": medical_record.medical_record_date,
                "symptom": medical_record.symptom,
                "prescription": medical_record.prescription,
                "result": medical_record.result,
                "advice": medical_record.advice,
            })
        response = {"result": 1,
                    "data": [{
                        "id": patient.patient_id,
                        "name": patient.patient_name,
                        "gender": patient.patient_gender,
                        "absence": patient.absence,
                        "address": patient.address,
                        "medicalRecord": medical_records_data
                    }]}
        return JsonResponse(response)
