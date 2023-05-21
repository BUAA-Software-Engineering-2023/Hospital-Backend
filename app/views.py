import hashlib
import json
import random
import string
import time
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.db import transaction
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from tool.logging_dec import logging_check
from .models import Department, Doctor, Notification, CarouselMap, News, Vacancy, Patient, User, \
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
            print(child)
            type.append({
                "name": obj.get('department_type'),
                "children": child
            })
        response = {
            'result': "1",
            'data': type
        }
        print(response)
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
            'result': "1",
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
            'result': "1",
            'data': data
        }
        return JsonResponse(response)


class DoctorDetail(View):
    def get(self, request, doctor_id):
        try:
            doctor = Doctor.objects.get(doctor_id=doctor_id)
            vacancies = Vacancy.objects.filter(doctor_id_id=doctor_id)
            available = []
            for vacancy in vacancies:
                available.append(vacancy.start_time)
            data = {
                "id": doctor.doctor_id,
                "name": doctor.doctor_name,
                "department": doctor.department_id.department_name,
                'image': doctor.doctor_image.url if doctor.doctor_image else None,
                "introduction": doctor.doctor_introduction,
                "available": available
            }
            response = {
                "result": "1",
                "data": data
            }
            return JsonResponse(response)
        except Doctor.DoesNotExist:
            response = {
                "result": "0",
                "message": "医生不存在"
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
            'result': "1",
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
            'result': "1",
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
                available.append({"is_morning": True, "time": date, "num": morning_cnt})
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
    def get(self, request):
        try:
            data = []
            doctor_id = request.GET.get('doctor_id')
            date = request.GET.get('date')
            is_morning = int(request.GET.get('is_morning'))

            vacancies = Vacancy.objects.filter(start_time__contains=date, doctor_id=doctor_id)
            for vacancy in vacancies:
                print(type(vacancy.start_time.hour))
                if (vacancy.start_time.hour < 12 and is_morning == 1) or (
                        vacancy.start_time.hour > 12 and is_morning == 0):
                    info = {
                        "vacancy_id": vacancy.vacancy_id,
                        "start_time": vacancy.start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": vacancy.end_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "count": vacancy.vacancy_count,
                        "left": vacancy.vacancy_left
                    }
                    data.append(info)
            response = {
                "result": "1",
                "data": data
            }
            return JsonResponse(response)
        except:
            return JsonResponse({
                "result": "0"
            })


class PatientList(View):
    @method_decorator(logging_check)
    def get(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION')
            jwt_token = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms='HS256')
            user_id = User.objects.get(phone_number=jwt_token['username']).user_id
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
    def get(self, request, doctor_id):
        patient_id_list = Appointment.objects.filter(doctor_id=doctor_id).values('patient_id').distinct()
        data = []
        for patient in patient_id_list:
            patient_id = patient['patient_id']
            patient_info = Patient.objects.get(patient_id=patient_id)
            info = {
                "patient_id": patient_id,
                "patient_name": patient_info.patient_name,
            }
            data.append(info)
        response = {
            "result": "1",
            "data": data
        }
        return JsonResponse(response)


class LeaveList(View):
    def get(self, request, doctor_id):
        # try:
        data = []
        leaves = Leave.objects.filter(doctor_id=doctor_id)
        for leave in leaves:
            info = {
                "leave_id": leave.leave_id,
                "start_time": leave.start_time,
                "end_time": leave.end_time,
                "type": leave.type,
                "reason": leave.reseon,
                "leave_status": leave.leave_status
            }
            data.append(info)
        response = {
            "result": "1",
            "data": data
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
            user_id = User.objects.get(phone_number=jwt_token['username']).user_id
            data = []
            users = User.objects.filter(user_id=user_id).values('phone_number')
            for user in users:
                info = {
                    "user_id": user_id,
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
    characters = string.digits
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
        return JsonResponse(
            {"result": "1", 'reason': '验证码发送成功', "vertification_code": verification_code})


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
                return JsonResponse(response, status=401)


class LoginCode(View):
    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token is None:
            json_str = request.body
            json_obj = json.loads(json_str)
            phone_number = json_obj['phone_number']
            if User.objects.get(phone_number=phone_number) is None:
                return JsonResponse({"result": "0", "reason": "用户未注册"})
            code = json_obj['code']
            data_code = Code.objects.filter(phone_number=phone_number).first()
            if data_code is None:
                response = {
                    "result": "0",
                    "reason": "请先获取验证码"
                }
                return JsonResponse(response)
            else:
                if code == data_code.verification_code:
                    token = make_token(phone_number)
                    print(token)
                    Code.objects.filter(phone_number=phone_number).first().delete()
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
                return JsonResponse(response, status=401)


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
        user = User.objects.filter(phone_number=phone_number).first()
        if user is not None:
            return JsonResponse({'result': "0", 'reason': '手机号已经被注册'})
        if info is not None:
            info = Code.objects.get(phone_number=phone_number)
            end_time = info.expire_time
            if datetime.now() > end_time:
                return JsonResponse({'result': "0", 'reason': "验证码过期"})
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
                return JsonResponse({'result': "1", 'reason': '注册成功'})
            else:
                return JsonResponse({'result': "0", 'reason': "验证码错误"})
        else:
            return JsonResponse({'result': "0", 'reason': '未发送验证码'})


class PatientDetail(View):
    @method_decorator(logging_check)
    def get(self, request, patient_id):
        patient = Patient.objects.get(patient_id=patient_id)
        response = {"result": 1,
                    "data": [{
                        "id": patient.patient_id,
                        "name": patient.patient_name,
                        "gender": patient.patient_gender,
                        "absence": patient.absence,
                        "address": patient.address,
                        "age": patient.age
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
                return JsonResponse({"result": "1", "message": "预约成功！"})
        except:
            return JsonResponse({"result": "0", "message": "出错了..."})


class CancelAppointment(View):
    @method_decorator(logging_check)
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        appointment_id = json_obj['appointment_id']
        doctor_id = Appointment.objects.get(appointment_id=appointment_id).doctor_id_id
        start_time = Appointment.objects.get(appointment_id=appointment_id).appointment_time
        vacancy = Vacancy.objects.filter(doctor_id_id=doctor_id, start_time=start_time).first()
        try:
            vacancy.vacancy_left = vacancy.vacancy_left + 1
            appointment = Appointment.objects.get(appointment_id=appointment_id)
            Appointment.delete(appointment)
            vacancy.save()
            return JsonResponse({"result": "1", "message": "取消预约成功！"})
        except:
            return JsonResponse({"result": "0", "message": "出错啦！"})


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
            appointment.appointment_status = "arrival"
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
            return JsonResponse({"result": "1", "message": "开具处方成功！"})
        except:
            return JsonResponse({"result": "0", "message": "出错啦！"})


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
            return JsonResponse({"result": "1", "message": "请假申请成功！"})
        except:
            return JsonResponse({"result": "0", "message": "出错啦！"})

    def delete(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        leave_id = json_obj['leave_id']
        try:
            leave = Leave.objects.get(leave_id=leave_id)
            Leave.delete(leave)
            return JsonResponse({"result": "1", "message": "删除请假成功！"})
        except:
            return JsonResponse({"result": "0", "message": "出错啦！"})


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
        return JsonResponse({"result": "1", "message": "取消预约成功！"})


class PatientAppointment(View):
    # @method_decorator(logging_check)
    def get(self, request, patient_id):
        appointments = Appointment.objects.filter(patient_id_id=patient_id)
        print(appointments)
        data = []
        for appointment in appointments:
            doctor = Doctor.objects.get(doctor_id=appointment.doctor_id_id)
            department = Department.objects.get(department_id=doctor.department_id_id)
            appointment_time = appointment.appointment_time.strftime("%Y-%m-%d %H:%M")
            data.append({"appointment_id": appointment.appointment_id, "appointment_time": appointment_time,
                         "appointment_status": appointment.
                        appointment_status, "doctor_name": doctor.doctor_name, "department_name": department.
                        department_name})
        return JsonResponse({"result": "1", "data": data})


class GetMedicalRecord(View):
    def get(self, request, patient_id):
        medical_records = MedicalRecord.objects.filter(patient_id_id=patient_id)
        patient = Patient.objects.get(patient_id=patient_id)
        data = []
        for medical_record in medical_records:
            doctor = Doctor.objects.get(doctor_id=medical_record.doctor_id_id)
            print(doctor)
            result = {
                "medical_record_date": medical_record.medical_record_date,
                "department_name": Department.objects.get(department_id=doctor.department_id_id).department_name,
                "doctor_name": doctor.doctor_name,
                "symptom": medical_record.symptom,
                "advice": medical_record.advice,
                "prescription": medical_record.prescription,
                "result": medical_record.result
            }
            data.append(result)
        return JsonResponse({"result": "1", "data": data})


def calculate_age(id_card_number):
    birth_year = int(id_card_number[6:10])
    birth_month = int(id_card_number[10:12])
    birth_day = int(id_card_number[12:14])

    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month
    current_day = current_date.day

    age = current_year - birth_year

    # 检查是否已经过了生日
    if (current_month, current_day) < (birth_month, birth_day):
        age -= 1

    return age


def get_gender(id_card_number):
    gender_code = int(id_card_number[-2])
    if gender_code % 2 == 0:
        return "女性"
    else:
        return "男性"


class AddPatient(View):
    @method_decorator(logging_check)
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        token = request.META.get('HTTP_AUTHORIZATION')
        jwt_token = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms='HS256')
        user_id = User.objects.get(phone_number=jwt_token['username']).user_id
        user = User.objects.get(user_id=user_id)
        patient_name = json_obj['patient_name']
        patient_identification = json_obj['identification']
        keys = json_obj.keys()
        if 'phone_number' in keys:
            phone_number = json_obj['phone_number']
        else:
            phone_number = None
        if 'address' in keys:
            address = json_obj['address']
        else:
            address = None
        age = calculate_age(patient_identification)
        patient_gender = get_gender(patient_identification)
        try:
            patient = Patient.objects.filter(identification=patient_identification).first()
            if patient is None:
                patient = Patient(
                    identification=patient_identification,
                    phone_number=phone_number,
                    patient_gender=patient_gender,
                    address=address,
                    patient_name=patient_name,
                    age=age
                )
                patient.save()
                user.patient_set.add(patient)
                return JsonResponse({"result": "1", "message": "添加患者成功！"})
            else:
                patient_1 = user.patient_set.filter(patient_id=patient.patient_id).first()
                if patient_1 is None:
                    user.patient_set.add(patient)
                    return JsonResponse({"result": "1", "message": "添加患者成功！"})
                else:
                    return JsonResponse({"result": "0", "message": "患者已经存在！"})
        except:
            return JsonResponse({"result": "0", "message": "出错啦！"})



class DeletePatient(View):
    @method_decorator(logging_check)
    def delete(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        patient_id_list = json_obj['patient_ids']

        try:
            with transaction.atomic():
                for patient_id in patient_id_list:
                    try:
                        patient = Patient.objects.get(patient_id=patient_id)
                        token = request.META.get('HTTP_AUTHORIZATION')
                        jwt_token = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms='HS256')
                        user_id = User.objects.get(phone_number=jwt_token['username']).user_id
                        user = User.objects.get(user_id=user_id)
                        user.patient_set.remove(patient)
                    except Patient.DoesNotExist:
                        return JsonResponse({"result": "0", "message": f"患者ID {patient_id} 不存在！"})
        except:
            return JsonResponse({"result": "0", "message": "出错啦！"})

        return JsonResponse({"result": "1", "message": "删除患者成功！"})


class UpdatePatient(View):
    @method_decorator(logging_check)
    def put(self, request, patient_id):
        json_str = request.body
        json_obj = json.loads(json_str)
        patient_name = json_obj['patient_name']
        patient_identification = json_obj['patient_identification']
        phone_number = json_obj['phone_number']
        address = json_obj['address']
        try:
            patient = Patient.objects.get(patient_id=patient_id)
            patient.patient_name = patient_name
            patient.identification = patient_identification
            patient.phone_number = phone_number
            patient.address = address
            patient.save()
            return JsonResponse({"result": "1", "message": "更新患者信息成功！"})
        except:
            return JsonResponse({"result": "0", "message": "出错啦！"})
