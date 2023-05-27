import hashlib
import json
import os.path
from _decimal import Decimal
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
    Patient, News, Vacancy_setting
from tool.logging_dec import logging_check

import hashlib

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


class NewsManage(View):
    @method_decorator(logging_check)
    def post(self, request):
        json_str = request.body.decode('utf-8')
        json_obj = json.loads(json_str)
        # Extract the necessary fields from the JSON object
        news_title = json_obj.get('news_title', '')
        news_content = json_obj.get('news_content', '')
        news_image = json_obj.get('news_image', '')
        news_time = datetime.now().date()
        news_type = json_obj.get("news_type", "")
        # Create a new News object and save it
        news = News(
            news_title=news_title,
            news_content=news_content,
            type=news_type,
            news_date=news_time,
            image=news_image
        )
        news.save()
        return JsonResponse({"result": "1", "message": "新闻添加成功！"})

    @method_decorator(logging_check)
    def delete(self, request):
        json_str = request.body.decode('utf-8')
        json_obj = json.loads(json_str)
        news_id = json_obj.get('news_id')

        # Check if the news exists and delete it
        news = News.objects.filter(news_id=news_id).first()
        if news:
            news.delete()
            return JsonResponse({"result": "1", "message": "新闻删除成功！"})
        else:
            return JsonResponse({"result": "0", "message": "新闻不存在！"})


class UploadImage(View):
    # @method_decorator(logging_check)
    def post(self, request):
        image_file = request.FILES.get('image').open('r')
        md5 = hashlib.md5(image_file.read()).hexdigest()
        extra_name = image_file.name.split('.')[-1]
        file_name = md5 + '.' + extra_name
        if not os.path.exists(f'./media/{file_name}'):
            image_file.seek(0)
            with open(f'./media/{md5}.{extra_name}', 'wb') as f:
                f.write(image_file.read())
            return JsonResponse(
                {"result": "1", "errno": 0, "data": {"url": request.build_absolute_uri(f'/media/{file_name}')}})


class NotificationManage(View):
    @method_decorator(logging_check)
    def post(self, request):
        json_str = request.body.decode('utf-8')
        json_obj = json.loads(json_str)
        notification_image = json_obj['notification_image']
        notification_content = json_obj['notification_content']
        notification_title = json_obj['notification_title']
        notification_time = datetime.now().date()
        notification_type = json_obj['notification_type']
        notification = Notification(
            type=notification_type,
            notification_time=notification_time,
            title=notification_title,
            content=notification_content,
            image=notification_image
        )
        notification.save()
        return JsonResponse({"result": "1", "message": "通知发送成功！", "id": notification.notification_id})

    def delete(self, request):
        json_str = request.body.decode('utf-8')
        json_obj = json.loads(json_str)
        notification_id = json_obj['notification_id']
        notification = Notification.objects.filter(notification_id=notification_id).first()
        if notification:
            notification.delete()
            return JsonResponse({"result": "1", "message": "通知删除成功！"})
        else:
            return JsonResponse({"result": "0", "message": "通知不存在！"})


class DoctorImage(View):
    @method_decorator(logging_check)
    def post(self, request, doctor_id):
        doctor_image = request.FILES.get('doctor_image')
        doctor = Doctor.objects.get(doctor_id=doctor_id)
        doctor.doctor_image = doctor_image
        doctor.save()
        return JsonResponse({'result': "1", 'message': '医生头像上传成功！'})


class DoctorManagement(View):
    # @method_decorator(logging_check)
    def post(self, request):
        json_str = request.body.decode('utf-8')
        json_obj = json.loads(json_str)
        doctor_name = json_obj['doctor_name']
        doctor_introduction = json_obj['doctor_introduction']
        doctor_dp_id = json_obj['doctor_dp_id']
        doctor_phone = json_obj['doctor_phone']
        doctor_gender = json_obj['doctor_gender']
        info = Doctor.objects.filter(phone_number=doctor_phone).first()
        if info is None:
            doctor = Doctor.objects.create(
                phone_number=doctor_phone,
                doctor_gender=doctor_gender,
                doctor_name=doctor_name,
                department_id_id=doctor_dp_id,
                doctor_introduction=doctor_introduction,
                doctor_image=''
            )
            user = User(
                phone_number=doctor_phone,
                passwd=MD5(doctor_phone),
                type="doctor"
            )
            user.save()
            response = {
                "result": "1",
                "doctor_id": doctor.doctor_id
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
            info.save()
            response = {
                "result": "1",
            }
            return JsonResponse(response)


class ScheduleManage(View):
    # @method_decorator(logging_check)
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
                            "is_morning": schedule['schedule_is_morning'],
                            "date": schedule['schedule_day']
                        }
                        day.append(day_data)

                doctor = Doctor.objects.get(doctor_id=doctor_id)
                info = {
                    "doctor_id": doctor_id,
                    "name": doctor.doctor_name,
                    "department": Department.objects.get(department_id=doctor.department_id_id).department_name,
                    "day": day,
                    "image": request.build_absolute_uri(doctor.doctor_image.url) if doctor.doctor_image else None,
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
        json_str = request.body
        json_obj = json.loads(json_str)
        doctor_id = json_obj['doctor_id']
        is_mornings = json_obj['is_mornings']
        dates = json_obj['dates']
        schedules = Schedule.objects.filter(doctor_id_id=doctor_id)
        for schedule in schedules:
            schedule.delete()
        try:
            i = 0
            with transaction.atomic():
                for i in range(len(is_mornings)):
                    date = dates[i]
                    is_morning = is_mornings[i]
                    schedule = Schedule.objects.filter(schedule_day=date, schedule_is_morning=is_morning,
                                                       doctor_id_id=doctor_id).first()
                    if schedule is None:
                        schedule = Schedule(
                            schedule_day=date,
                            schedule_is_morning=is_morning,
                            doctor_id_id=doctor_id
                        )
                        schedule.save()
                # vacancy_check()
        except:
            return JsonResponse({"result": "0", "message": "排班设置失败！"})
        return JsonResponse({"result": "1", "message": "排班设置成功！"})

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
            if appointments:
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


class VacancySettingManage(View):
    def get(self, request):
        vacancy_settings = Vacancy_setting.objects.all()
        data = []
        for vacancy_setting in vacancy_settings:
            data.append({"vacancy_setting_id": vacancy_setting.id, "vacancy_cnt": vacancy_setting.vacancy_cnt,
                         "vacancy_time": vacancy_setting.vacancy_time, "vacancy_day": vacancy_setting.vacancy_day})
        return JsonResponse({"result": "1", "data": data})

    def put(self, request):
        json_str = request.body.decode('utf-8')
        json_obj = json.loads(json_str)
        vacancy_counts = json_obj['vacancy_counts']
        vacancy_day = json_obj['vacancy_day']
        tmp = 0
        for start_time in range(8, 12):
            vacancy_time = Decimal(str(start_time))
            vacancy_setting = Vacancy_setting.objects.filter(vacancy_time=vacancy_time, vacancy_day=vacancy_day).first()
            vacancy_setting.vacancy_cnt = vacancy_counts[tmp]
            vacancy_setting.save()
            tmp = tmp + 1
            vacancy_time = Decimal(str(start_time)) + Decimal('0.5')
            vacancy_setting = Vacancy_setting.objects.filter(vacancy_time=vacancy_time, vacancy_day=vacancy_day).first()
            vacancy_setting.vacancy_cnt = vacancy_counts[tmp]
            vacancy_setting.save()

        for start_time in range(14, 18):
            tmp = tmp + 1
            vacancy_time = Decimal(str(start_time))
            vacancy_setting = Vacancy_setting.objects.filter(vacancy_time=vacancy_time, vacancy_day=vacancy_day).first()
            vacancy_setting.vacancy_cnt = vacancy_counts[tmp]
            vacancy_setting.save()
            tmp = tmp + 1
            vacancy_time = Decimal(str(start_time)) + Decimal('0.5')
            vacancy_setting = Vacancy_setting.objects.filter(vacancy_time=vacancy_time, vacancy_day=vacancy_day).first()
            vacancy_setting.vacancy_cnt = vacancy_counts[tmp]
            vacancy_setting.save()
        return JsonResponse({"result": "1", "message": "修改放号成功！"})
