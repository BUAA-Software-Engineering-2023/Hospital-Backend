import hashlib
import json
from datetime import datetime, timedelta
import time

import jwt
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View

from app.models import Department, Notification, Vacancy, Appointment, Doctor, Leave, Admin, User, Schedule, Message, \
    Patient
from tool.logging_dec import logging_check

AppointmentStatus = ["待就医", "待就医", "已就医", "失约"]


# Create your views here.
def make_token(username, expire=3600 * 24):
    key = settings.JWT_TOKEN_KEY
    now_t = time.time()
    payload_data = {'username': username, 'exp': now_t + expire}
    return jwt.encode(payload_data, key, algorithm='HS256')


class LoginView(View):
    def post(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token is None:
            json_str = request.body
            json_obj = json.loads(json_str)
            user_name = json_obj['username']
            passwd = json_obj['password']
            admin = Admin.objects.filter(username=user_name).first()
            if admin is None:
                response = {
                    "result": "0",
                    "message": "管理员不存在！"
                }
                return JsonResponse(response)
            else:
                data_passwd = Admin.objects.filter(username=user_name).first().password
                token = make_token(user_name)
                if passwd == data_passwd:
                    response = {
                        "result": "1",
                        "data": {"token": token},
                        "message": "登录成功！"
                    }
                    return JsonResponse(response)
                else:
                    response = {
                        "result": "0",
                        "message": "密码错误！"
                    }
                    return JsonResponse(response)
        else:
            try:
                jwt_token = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms='HS256')
                response = {
                    "result": "0",
                    "message": "已登录，请勿重复登录"
                }
                return JsonResponse(response)
            except:
                response = {
                    "result": "0",
                    "message": "登录状态异常"
                }
                return JsonResponse(response, status=401)


class DoctorManagement(View):
    @method_decorator(logging_check)
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        doctor_name = json_obj['doctor_name']
        doctor_introduction = json_obj['doctor_introduction']
        doctor_dp_id = json_obj['doctor_dp_id']
        doctor_phone = json_obj['doctor_phone']
        doctor_gender = json_obj['doctor_gender']
        doctor_image = request.FILES['image']
        info = Doctor.objects.filter(phone_number=doctor_phone).first()
        if info is None:
            Doctor.objects.create(
                phone_number=doctor_phone,
                doctor_gender=doctor_gender,
                doctor_name=doctor_name,
                department_id_id=doctor_dp_id,
                doctor_introduction=doctor_introduction,
                doctor_image=doctor_image
            )
            user = User(
                phone_number=doctor_phone,
                passwd=MD5(doctor_phone),
                type="doctor"
            )
            user.save()
            response = {
                "result": "1",
            }
            return JsonResponse(response)
        else:
            response = {
                "result": "0",
                "message": "医生已存在！"
            }
            return JsonResponse(response)

    def delete(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        doctor_ids = json_obj['doctor_ids']
        try:
            with transaction.atomic():
                for doctor_id in doctor_ids:
                    try:
                        doctor = Doctor.objects.get(doctor_id=doctor_id)
                        doctor.delete()
                    except Doctor.DoesNotExist:
                        return JsonResponse({"result": "0", "message": f"医生ID {doctor_id} 不存在！"})
        except:
            return JsonResponse({"result": "0", "message": "出错啦！"})
        return JsonResponse({"result": "1", "message": "删除医生成功！"})

    def put(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        doctor_id = json_obj['doctor_id']
        doctor_name = json_obj['doctor_name']
        doctor_introduction = json_obj['doctor_introduction']
        doctor_dp_id = json_obj['doctor_dp_id']
        doctor_phone = json_obj['doctor_phone']
        doctor_gender = json_obj['doctor_gender']
        doctor_image = request.FILES['doctor_image']
        info = Doctor.objects.filter(doctor_id=doctor_id).first()
        if info is None:
            response = {
                "result": "0",
                "message": "医生未找到！"
            }
            return JsonResponse(response)
        else:
            info.doctor_name = doctor_name
            info.doctor_introduction = doctor_introduction
            info.department_id_id = doctor_dp_id
            info.doctor_phone = doctor_phone
            info.doctor_gender = doctor_gender
            info.doctor_image = doctor_image
            info.save()
            response = {
                "result": "1",
            }
            return JsonResponse(response)


class ScheduleManage(View):
    @method_decorator(logging_check)
    def get(self, request):
        try:
            data = []
            doctor_id_list = Doctor.objects.values('doctor_id').distinct()
            for doctor in doctor_id_list:
                doctor_id = doctor['doctor_id']
                day = []
                schedules = Schedule.objects.filter(doctor_id=doctor_id).values('schedule_is_morning', "schedule_day",
                                                                                'schedule_id')
                if schedules is not None:
                    for schedule in schedules:
                        day_data = {
                            "schedule": schedule['schedule_id'],
                            "ismorning": schedule['schedule_ismorning'],
                            "date": schedule['schedule_day']
                        }
                        day.append(day_data)

                doctors = Doctor.objects.get(doctor_id=doctor_id)
                info = {
                    "doctor_id": doctor_id,
                    "name": doctors.doctor_name,
                    "department": Department.objects.get(department_id=doctors.department_id_id).department_name,
                    "day": day
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

    def post(self, request):
        try:
            json_str = request.body
            json_obj = json.loads(json_str)
            doctor_id = json_obj['doctor_id']
            is_morning = json_obj['is_morning']
            date = json_obj['date']
            schedule = Schedule(
                schedule_day=date,
                schedule_ismorning=is_morning,
                doctor_id_id=doctor_id
            )
            schedule.save()
            response = {
                "result": "1"
            }
            vacancy_check()
            return JsonResponse(response)
        except:
            response = {
                "result": "0"
            }
            return JsonResponse(response)

    def delete(self, request):
        # try:
        json_str = request.body
        json_obj = json.loads(json_str)
        schedule_ids = json_obj['schedule_ids']
        try:
            with transaction.atomic():
                for schedule_id in schedule_ids:
                    schedule = Schedule.objects.get(schedule_id=schedule_id)
                    doctor_id = schedule.doctor_id
                    is_morning = schedule.schedule_is_morning
                    date = schedule.schedule_day
                    vacancies = Vacancy.objects.filter(start_time__contains=date, doctor_id=doctor_id)
                    for vacancy in vacancies:
                        start_time = vacancy.start_time
                        if is_morning * 12 < start_time.hour < is_morning * 12 + 12:
                            appointments = Appointment.objects.filter(doctor_id=doctor_id, appointment_time=start_time)
                            for appointment in appointments:
                                Appointment.delete(appointment)
                            Vacancy.delete(vacancy)
                    Schedule.delete(schedule)
                vacancy_check()
        except:
            return JsonResponse({"result": "0"})
        response = {"result": "1"}
        return JsonResponse(response)
    # except:
    #     response = {
    #         "result": "0"
    #     }
    #     return JsonResponse(response)


def MD5(password):
    m = hashlib.md5()
    m.update(password.encode())
    md5_pwd = m.hexdigest()
    return md5_pwd


class DepartmentManage(View):
    @method_decorator(logging_check)
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        department_name = json_obj['department_name']
        department_type = json_obj['department_type']
        department_introduction = json_obj['department_introduction']
        department = Department.objects.filter(department_name=department_name).first()
        if department is None:
            department = Department(
                department_name=department_name,
                department_type=department_type,
                department_introduction=department_introduction
            )
            department.save()
            return JsonResponse({"result": "1", "message": "部门添加成功"})
        else:
            return JsonResponse({"result": "0", "message": "部门已存在"})

    def delete(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        department_names = json_obj['department_names']
        try:
            with transaction.atomic():
                for department_name in department_names:
                    department = Department.objects.filter(department_name=department_name).first()
                    if department:
                        department.delete()
                    else:
                        return JsonResponse({"result": "0", "message": "未找到该部门！"})
        except:
            return JsonResponse({"result": "0", "message": "出错啦！"})

        return JsonResponse({"result": "1", "message": "删除部门成功！"})

    def put(self, request):
        json_str = request.body.decode('utf-8')
        json_obj = json.loads(json_str)
        department_name = json_obj['department_name']
        department_type = json_obj['department_type']
        department_introduction = json_obj['department_introduction']
        department = Department.objects.filter(department_name=department_name).first()
        if department:
            department.department_type = department_type
            department.department_introduction = department_introduction
            department.save()
            return JsonResponse({"result": "1", "message": "部门信息更新成功！"})
        else:
            return JsonResponse({"result": "0", "message": "部门未找到！"})


class NotificationManage(View):
    @method_decorator(logging_check)
    def post(self, request):
        json_str = request.body.decode('utf-8')
        json_obj = json.loads(json_str)
        notification_title = json_obj['title']
        notification_content = json_obj['content']
        notification_link = json_obj['notification_link']
        notification = Notification(
            title=notification_title,
            content=notification_content,
            notification_time=datetime.now().date(),
            notification_link=notification_link
        )
        notification.save()
        return JsonResponse({"result": "1", "message": "通知成功发送"})


class VacancyManage(View):
    @method_decorator(logging_check)
    def post(self, request):
        json_str = request.body.decode('utf-8')
        json_obj = json.loads(json_str)
        start_time = json_obj['start_time']
        vacancy_count = json_obj['vacancy_count']
        updated_vacancies = Vacancy.objects.filter(start_time=start_time)
        tmp = updated_vacancies.first().vacancy_count - vacancy_count
        doctor_ids = Appointment.objects.filter(appointment_time=start_time).values('doctor_id').distinct()
        for updated_vacancy in updated_vacancies:
            if updated_vacancy.vacancy_left - tmp < 0:
                for doctor_id in doctor_ids:
                    doctor_id = doctor_id['doctor_id']
                    updated_appointments = Appointment.objects.filter(appointment_time=start_time, doctor_id=doctor_id)
                    excess_appointments_count = updated_appointments.count() - vacancy_count
                    if excess_appointments_count > 0:
                        # 删除多出的预约记录
                        excess_appointments = updated_appointments.order_by('-appointment_id')[
                                              :excess_appointments_count]
                        for appointment in excess_appointments:
                            appointment.delete()
                        # 更新对应的预约数量
                        updated_vacancy.vacancy_left = 0
                    else:
                        updated_vacancy.vacancy_left = updated_vacancy.vacancy_left - tmp
                updated_vacancy.vacancy_count = vacancy_count
                updated_vacancy.save()
            else:
                updated_vacancy.vacancy_left = updated_vacancy.vacancy_left - tmp
                updated_vacancy.vacancy_count = vacancy_count
                updated_vacancy.save()

        response = {"result": "1", "message": "放号数量修改成功"}
        return JsonResponse(response)


class LeaveList(View):
    def get(self, request):
        leaves = Leave.objects.exclude(leave_status='已通过')
        data = []
        for leave in leaves:
            doctor_name = Doctor.objects.get(doctor_id=leave.doctor_id_id).doctor_name
            data.append({
                "doctor_name": doctor_name,
                "start_time": leave.start_time,
                "end_time": leave.end_time,
                "type": leave.type,
                "reason": leave.reseon
            })
        return JsonResponse({"result": "1", "data": data})


class ProcessLeave(View):
    @method_decorator(logging_check)
    def post(self, request, leave_status):
        json_str = request.body.decode('utf-8')
        json_obj = json.loads(json_str)
        leave_id = json_obj['leave_id']
        leave = Leave.objects.get(leave_id=leave_id)
        doctor_id = leave.doctor_id_id
        leave.leave_status = leave_status
        if leave_status == "已通过":
            schedules = Schedule.objects.filter(doctor_id_id=leave.doctor_id_id)
            for schedule in schedules:
                if (leave.start_time.weekday() + 1) > schedule.schedule_day or schedule.schedule_day > (
                        leave.end_time.weekday() + 1) \
                        or (
                        schedule.schedule_day == leave.start_time.weekday() and leave.start_time.hour > 12
                        and schedule.schedule_is_morning == 1) \
                        or (
                        schedule.schedule_day == leave.end_time.weekday() and leave.end_time.hour < 12
                        and schedule.schedule_is_morning == 0):
                    continue
                else:
                    date = schedule.schedule_day
                    current_date = datetime.now().date()
                    next_week = current_date + timedelta(days=7)
                    vacancies = Vacancy.objects.filter(
                        Q(start_time__week_day=date) &
                        Q(doctor_id=leave.doctor_id) &
                        Q(start_time__date__range=[current_date, next_week])
                    )
                    for vacancy in vacancies:
                        start_time = vacancy.start_time
                        is_morning = schedule.schedule_is_morning
                        if is_morning * 12 < start_time.hour < is_morning * 12 + 12:
                            appointments = Appointment.objects.filter(doctor_id=leave.doctor_id,
                                                                      appointment_time=start_time)
                            for appointment in appointments:
                                patient_id = appointment.patient_id_id
                                patient = Patient.objects.get(patient_id=patient_id)
                                users = patient.user_id.all()
                                doctor_name = Doctor.objects.get(doctor_id=doctor_id).doctor_name
                                for user in users:
                                    message = Message(
                                        title="您的预约已取消",
                                        content=f"很抱歉，由于{doctor_name}医生的原因，{patient.patient_name}的预约已取消。",
                                        message_time=datetime.now(),
                                        is_read=0,
                                        user_id_id=user.user_id
                                    )
                                    message.save()
                                appointment.appointment_status = 3
                                appointment.save()
                            Vacancy.delete(vacancy)
        else:
            phone_number = Doctor.objects.get(doctor_id=doctor_id).phone_number
            user = User.objects.filter(phone_number=phone_number).first()
            message = Message(
                title=f"您的请假未批准",
                content="",
                message_time=datetime.now(),
                is_read=0,
                user_id=user
            )
            message.save()
        return JsonResponse({"result": "1"})


class DoctorImage(View):
    @method_decorator(logging_check)
    def post(self, request, doctor_id):
        doctor = Doctor.objects.get(doctor_id=doctor_id)


def vacancy_check():
    vacancies = Vacancy.objects.filter(start_time__gt=datetime.now())
    for vacancy in vacancies:
        doctor_id = vacancy.doctor_id.doctor_id
        weekday = vacancy.start_time.weekday() + 1
        if vacancy.start_time.hour < 12:
            is_morning = 1
        else:
            is_morning = 0
        # print(is_morning)
        schedules = Schedule.objects.filter(schedule_day=weekday, doctor_id=doctor_id, schedule_is_morning=is_morning)
        if schedules.first():
            continue
        else:
            start_time = vacancy.start_time
            appointments = Appointment.objects.filter(doctor_id_id=doctor_id, appointment_time=start_time)
            for appointment in appointments:
                patient_id = appointment.patient_id_id
                patient = Patient.objects.get(patient_id=patient_id)
                users = patient.user_id.all()
                for user in users:
                    message = Message(
                        title="您的预约已取消",
                        content=f"很抱歉，由于特殊原因，{patient.patient_name}的预约已取消。",
                        message_time=datetime.now(),
                        is_read=0,
                        user_id_id=user.user_id
                    )
                    message.save()
                appointment.appointment_status = 3
                appointment.save()
            vacancy.delete()
    return JsonResponse({"result": "1"})
