import hashlib
import json
import random
import string
import time
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from tool.logging_dec import logging_check
from .models import Department, Doctor, Notification, CarouselMap, News, Vacancy, Schedule, Patient, User, \
    MedicalRecord, Code, Appointment, Leave


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
    @method_decorator(logging_check)
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
            morning_cnt = 0
            afternoon_cnt = 0
            morning_judge = False
            afternoon_judge = False
            for vacancy in vacancies:
                if vacancy['start_time'].hour < 12:
                    morning_cnt += vacancy['vacancy_count']
                    morning_judge = True
                else:
                    afternoon_cnt += vacancy['vacancy_count']
                    afternoon_judge = True
            if morning_judge:
                available.append({"is_morning": True,"time": date, "num": morning_cnt})
            if afternoon_judge:
                available.append({"is_morning": False, "time": date, "num": afternoon_cnt})
            data.append({
                "id": doctor_id,
                "name": doctor_info.doctor_name,
                "department": Department.objects.get(department_id=departmentId).department_name,
                "image": '',
                "introduction": doctor_info.doctor_introduction,
                "available": available
            })

        response = {
            "result": "1",
            "data": data,
        }
        return JsonResponse(response)

class VacancyDetail(View):
    def get(self,request):
        try:
            data = []
            doctor_id = request.GET.get('doctor_id')
            date = request.GET.get('date')
            is_morning = int(request.GET.get('is_morning'))

            vacancies = Vacancy.objects.filter(start_time__contains=date,doctor_id=doctor_id)
            for vacancy in vacancies:
                print(type(vacancy.start_time.hour))
                if (vacancy.start_time.hour<12 and is_morning==1)or(vacancy.start_time.hour>12 and is_morning==0):
                    info={
                        "vacancy_id":vacancy.vacancy_id,
                        "start_time":vacancy.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time":vacancy.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "count":vacancy.vacancy_count
                    }
                    data.append(info)
            response={
                "result":"1",
                "data":data
            }
            return JsonResponse(response)
        except:
            return JsonResponse({
                "result": "0"
            })

class PatientList(View):
    @method_decorator(logging_check)
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

class PatientWaiting(View):
    def get(self,request,doctor_id):
        patient_id_list = Appointment.objects.filter(doctor_id=doctor_id).values('patient_id').distinct()
        data = []
        for patient in patient_id_list:
            patient_id = patient['patient_id']
            patient_info = Patient.objects.get(patient_id=patient_id)
            info = {
                "patient_id":patient_id,
                "patient_name":patient_info.patient_name,
            }
            data.append(info)
        response = {
            "result": "1",
            "data": data
        }
        return JsonResponse(response)

class LeaveList(View):
    def get(self,request,doctor_id):
        # try:
            data = []
            leaves = Leave.objects.filter(doctor_id=doctor_id)
            for leave in leaves:
                info = {
                    "leave_id":leave.leave_id,
                    "start_time":leave.start_time,
                    "end_time":leave.end_time,
                    "type":leave.type,
                    "reason":leave.reseon,
                    "leave_status":leave.leave_status
                }
                data.append(info)
            response = {
                "result": "1",
                "data":data
            }
            return JsonResponse(response)
        # except:
        #     return JsonResponse({"result": 0, "message": "error"})
class UserInfo(View):
    @method_decorator(logging_check)
    def get(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION')
            jwt_token = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms='HS256')
            user_id=User.objects.get(phone_number=jwt_token['username']).user_id
            data = []
            users = User.objects.filter(user_id=user_id).values('phone_number')
            for user in users:
                info = {
                    "user_id":user_id,
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
        info = Code.objects.filter(phone_number=phone_number).first()
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
        return JsonResponse({"result": 1, 'message': 'Code sent successfully',"vertification_code":verification_code})


class LoginPassWd(View):
    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token is None:
            json_str = request.body
            json_obj = json.loads(json_str)
            phone_number = json_obj['phone_number']
            passwd = json_obj['password']
            m = hashlib.md5()
            m.update(passwd.encode())
            md5_pwd = m.hexdigest()

            data_passwd = User.objects.filter(phone_number=phone_number).first().passwd
            if data_passwd is None:
                response = {
                    "result": "0",
                    "reason": "电话号码错误"
                }
                return JsonResponse(response)
            else:
                if data_passwd == md5_pwd:
                    token = make_token(phone_number)
                    response = {
                        "result": "1",
                        "data": {"token": token}
                    }
                    return JsonResponse(response)
                else:
                    response = {
                        "result": "0",
                        "reason": "密码错误"
                    }
                    return JsonResponse(response)
        else:
            try:
                jwt_token = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms='HS256')
                response = {
                    "result": "0",
                    "reason": "已登录，请勿重复登录"
                }
                return JsonResponse(response)
            except:
                response = {
                    "result": "0",
                    "reason": "登录状态异常"
                }
                return JsonResponse(response),401


class LoginCode(View):
    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token is None:
            json_str = request.body
            json_obj = json.loads(json_str)
            phone_number = json_obj['phone_number']
            code = json_obj['code']
            data_code = Code.objects.filter(phone_number=phone_number).first().data_code
            if data_code is None:
                response = {
                    "result": "0",
                    "reason": "请先获取验证码"
                }
                return JsonResponse(response)
            else:
                if code == data_code:
                    token = make_token(phone_number)
                    response = {
                        "result": "1",
                        "data": {"token": token}
                    }
                    return JsonResponse(response)
                else:
                    response = {
                        "result": "0",
                        "reason": "验证码错误"
                    }
                    return JsonResponse(response)
        else:
            try:
                jwt_token = jwt.decode(token, settings.JWT_TOKEN_KEY)
                response = {
                    "result": "0",
                    "reason": "已登录，请勿重复登录"
                }
                return JsonResponse(response)
            except:
                response = {
                    "result": "0",
                    "reason": "登录状态异常"
                }
                return JsonResponse(response),401


def make_token(username, expire=3600 * 24):
    key = settings.JWT_TOKEN_KEY
    now_t = time.time()
    payload_data = {'username': username, 'exp': now_t + expire}
    return jwt.encode(payload_data, key, algorithm='HS256')


class UserView(View):
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        phone_number = json_obj['phone_number']
        password = json_obj['password']
        verification_code = json_obj['verification_code']
        info = Code.objects.filter(phone_number=phone_number).first()
        if info is not None:
            info = Code.objects.get(phone_number=phone_number)
            m = hashlib.md5()
            m.update(password.encode())
            md5_pwd = m.hexdigest()
            if info.verification_code == verification_code:
                user = User(
                    phone_number=phone_number,
                    passwd=md5_pwd,
                    type="user"
                )
                user.save()
                return JsonResponse({'result': 1, 'reason': '注册成功'})
            else:
                return JsonResponse({'result': 0, 'reason': "验证码错误"})
        else:
            return JsonResponse({'result': 0, 'reason': '手机号已经被注册'})


class PatientDetail(View):
    @method_decorator(logging_check)
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


class MakeAppointment(View):
    @method_decorator(logging_check)
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        doctor_id = json_obj['doctor_id']
        start_time = json_obj['start_time']
        patient_id = json_obj['patient_id']
        vacancy = Vacancy.objects.filter(doctor_id_id=doctor_id, start_time=start_time).first()
        try:
            if vacancy.vacancy_left > 0:
                vacancy.vacancy_left = vacancy.vacancy_left - 1
                appointment = Appointment(
                    appointment_time=start_time,
                    appointment_status="Scheduled",
                    doctor_id_id=doctor_id,
                    patient_id_id=patient_id
                )
                appointment.save()
                vacancy.save()
                return JsonResponse({"result": 1, "message": "Make appointment successfully"})
        except:
            return JsonResponse({"result": 0, "message": "error"})
    def delete(self,request):
        json_str = request.body
        json_obj = json.loads(json_str)
        appointment_id =json_obj['appointment_id']
        doctor_id = json_obj['doctor_id']
        start_time = json_obj['start_time']
        vacancy = Vacancy.objects.filter(doctor_id_id=doctor_id, start_time=start_time).first()
        try:
            vacancy.vacancy_left = vacancy.vacancy_left + 1
            appointment = Appointment.objects.get(appointment_id=appointment_id)
            Appointment.delete(appointment)
            Appointment.delete(appointment)
            vacancy.save()
            return JsonResponse({"result": 1, "message": "Delete appointment successfully"})
        except:
            return JsonResponse({"result": 0, "message": "error"})



class MakeMedicalRecord(View):
    @method_decorator(logging_check)
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        doctor_id = json_obj['doctor_id']
        medical_record_date = json_obj['medical_record_date']
        patient_id = json_obj['patient_id']
        department_id = json_obj['department_id']
        symptom = json_obj['symptom']
        prescription = json_obj['prescription']
        result = json_obj['result']
        advice = json_obj['advice']
        try:
            medical_record = MedicalRecord.objects.filter(patient_id_id=patient_id, department_id_id=department_id,
                                                          doctor_id_id=doctor_id).first()
            appointment_id = medical_record.appointment_id
            appointment = Appointment.objects.get(appointment_id=appointment_id)
            appointment.appointment_status="arrival"
            appointment.save()
            if medical_record:
                medical_record.medical_record_date = medical_record_date
                medical_record.advice = advice
                medical_record.result = result
                medical_record.symptom = symptom
                medical_record.prescription = prescription
            else:
                medical_record = MedicalRecord(
                    medical_record_date=medical_record_date,
                    advice=advice,
                    result=result,
                    symptom=symptom,
                    prescription=prescription,
                    doctor_id_id=doctor_id,
                    patient_id_id=patient_id,
                    department_id_id=department_id
                )
            medical_record.save()
            return JsonResponse({"result": 1, "message": "Make medical record successfully"})
        except:
            return JsonResponse({"result": 0, "message": "error"})



class MakeLeave(View):
    @method_decorator(logging_check)
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        doctor_id = json_obj['doctor_id']
        start_time = json_obj['start_time']
        end_time = json_obj['end_time']
        leave_type = json_obj['type']
        reason = json_obj['reason']
        try:
            leave = Leave(
                doctor_id_id=doctor_id,
                start_time=start_time,
                end_time=end_time,
                type=leave_type,
                reseon=reason,
                leave_status="申请中"
            )
            leave.save()
            return JsonResponse({"result": 1, "message": "successfully"})
        except:
            return JsonResponse({"result": 0, "message": "error"})
    def delete(self,request):
        json_str = request.body
        json_obj = json.loads(json_str)
        leave_id = json_obj['leave_id']
        try:
            leave = Leave.objects.get(leave_id=leave_id)
            Leave.delete(leave)
            return JsonResponse({"result": 1, "message": "successfully"})
        except:
            return JsonResponse({"result": 0, "message": "error"})



class CancelLeave(View):
    @method_decorator(logging_check)
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        doctor_id = json_obj['doctor_id']
        start_time = json_obj['start_time']
        end_time = json_obj['end_time']
        leave = Leave.objects.filter(doctor_id_id=doctor_id, start_time=start_time, end_time=end_time).first()
        if leave:
            leave.delete()
        return JsonResponse({"result": 1, "message": "successfully"})


