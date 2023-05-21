import hashlib
import json
from datetime import datetime

from django.http import JsonResponse, HttpRequest
from django.views import View

from app.models import Department, Notification, Vacancy, Appointment, Doctor, Leave, Admin, User, Schedule, Message, \
    Patient


# Create your views here.

class LoginView(View):
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        user_name = json_obj['username']
        passwd = json_obj['password']
        admin = Admin.objects.filter(username=user_name).first()
        if admin is None:
            response = {
                "result": "0",
                "reason": "admin not exist"
            }
            return JsonResponse(response)
        else:
            data_passwd = Admin.objects.filter(user_name=user_name).first().password
            if MD5(passwd) == data_passwd:
                response = {
                    "result": "1",
                    "reason": "success"
                }
                return JsonResponse(response)
            else:
                response = {
                    "result": "0",
                    "reason": "password wrong"
                }
                return JsonResponse(response)


class DoctorManagement(View):
    def post(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        doctor_name = json_obj['doctor_name']
        doctor_introduction = json_obj['doctor_introduction']
        doctor_dp_id = json_obj['doctor_dp_id']
        doctor_phone = json_obj['doctor_phone']
        doctor_gender = json_obj['doctor_gender']
        info = Doctor.objects.filter(phone_number=doctor_phone).first()
        if info is None:
            Doctor.objects.create(
                phone_number=doctor_phone,
                doctor_gender=doctor_gender,
                doctor_name=doctor_name,
                department_id_id=doctor_dp_id,
                doctor_introduction=doctor_introduction
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
                "reason": "phone number exists"
            }
            return JsonResponse(response)

    def delete(self, request):
        json_str = request.body
        json_obj = json.loads(json_str)
        doctor_id = json_obj['doctor_id']
        info = Doctor.objects.filter(doctor_id=doctor_id).first()
        if info is None:
            response = {
                "result": "0",
                "reason": "doctor not found"
            }
            return JsonResponse(response)
        else:
            Doctor.delete(info)
            response = {
                "result": "1",
            }
            return JsonResponse(response)

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
                "reason": "doctor not found"
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
    def get(self, request):
        try:
            data = []
            doctor_id_list = Doctor.objects.values('doctor_id').distinct()
            for doctor in doctor_id_list:
                doctor_id = doctor['doctor_id']
                day = []
                schedules = Schedule.objects.filter(doctor_id=doctor_id).values('schedule_ismorning', "schedule_day",
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
        schedule_id = json_obj['schedule_id']
        schedule = Schedule.objects.get(schedule_id=schedule_id)
        doctor_id = schedule.doctor_id
        is_morning = schedule.schedule_is_morning
        date = schedule.schedule_day

        vacancies = Vacancy.objects.filter(start_time__contains=date, doctor_id=doctor_id)

        for vacancy in vacancies:
            time = vacancy.start_time
            if is_morning * 12 < time.hour < is_morning * 12 + 12:
                appointments = Appointment.objects.filter(doctor_id=doctor_id, appointment_time=time)
                for appointment in appointments:
                    Appointment.delete(appointment)
                Vacancy.delete(vacancy)

        Schedule.delete(schedule)
        response = {
            "result": "1"
        }
        vacancy_check()
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
            return JsonResponse({"result": 1, "message": "department added successfully"})
        else:
            return JsonResponse({"result": 0, "message": "department already existed"})

    def delete(self, request):
        json_str = request.body.decode('utf-8')
        json_obj = json.loads(json_str)
        department_name = json_obj['department_name']
        department = Department.objects.filter(department_name=department_name).first()
        if department:
            department.delete()
            return JsonResponse({"result": 1, "message": "Department deleted successfully"})
        else:
            return JsonResponse({"result": 0, "message": "Department not found"})

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
            return JsonResponse({"result": 1, "message": "Department updated successfully"})
        else:
            return JsonResponse({"result": 0, "message": "Department not found"})


class NotificationManage(View):
    def post(self, request):
        json_str = request.body.decode('utf-8')
        json_obj = json.loads(json_str)
        notification_title = json_obj['title']
        notification_content = json_obj['content']
        notification_link = json_obj['notification_link']
        notification = Notification(
            title=notification_title,
            content=notification_content,
            notification_time=datetime.now(),
            notification_link=notification_link
        )
        notification.save()
        return JsonResponse({"result": 1, "message": "通知成功发送"})


class VacancyManage(View):
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

        response = {"result": 1, "message": "放号数量修改"}
        return JsonResponse(response)


class LeaveList(View):
    def get(self, request):
        leaves = Leave.objects.exclude(leave_status='Approved')
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
    def post(self, request, leave_status):
        json_str = request.body.decode('utf-8')
        json_obj = json.loads(json_str)
        leave_id = json_obj['leave_id']
        leave = Leave.objects.get(leave_id=leave_id)
        leave.leave_status = leave_status
        if leave_status == "Approved":
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
                    # todo
                    request = HttpRequest()
                    request.method = 'POST'  # 设置请求方法为 POST
                    date = schedule.schedule_day
                    vacancies = Vacancy.objects.filter(start_time__contains=date, doctor_id=leave.doctor_id)
                    for vacancy in vacancies:
                        time = vacancy.start_time
                        is_morning = schedule.schedule_is_morning
                        if is_morning * 12 < time.hour < is_morning * 12 + 12:
                            appointments = Appointment.objects.filter(doctor_id=leave.doctor_id, appointment_time=time)
                            for appointment in appointments:
                                Appointment.delete(appointment)
                            Vacancy.delete(vacancy)
                    request.body = f'{{"schedule_id": {schedule.schedule_id}}}'  # 设置请求的 body 数据
                    schedule_manage = ScheduleManage()
                    schedule_manage.delete(request)
        leave.save()
        return JsonResponse({"result": "1"})


def vacancy_check():
    vacancies = Vacancy.objects.all()
    print(vacancies)
    for vacancy in vacancies:
        doctor_id = vacancy.doctor_id.doctor_id
        print(doctor_id)
        weekday = vacancy.start_time.weekday() + 1
        print(weekday)
        if vacancy.start_time.hour < 12:
            is_morning = 1
        else:
            is_morning = 0
        print(is_morning)
        schedules = Schedule.objects.filter(schedule_day=weekday, doctor_id=doctor_id, schedule_is_morning=is_morning)
        if schedules.first():
            continue
        else:
            start_time = vacancy.start_time
            appointments = Appointment.objects.filter(doctor_id_id=doctor_id, appointment_time=start_time)
            for appointment in appointments:
                patient_id = appointment.patient_id_id
                patient = Patient.objects.get(patient_id=patient_id)
                print(patient)
                users = patient.user_id.all()
                print(users)
                for user in users:
                    message = Message(
                        title="Your appointment has canceled",
                        content=f"很抱歉，由于医生的原因，{patient.patient_name}的预约已取消。",
                        message_time=datetime.now(),
                        is_read=0,
                        user_id_id=user.user_id
                    )
                    message.save()
                print(appointment)
                appointment.appointment_status = "Cancelled"
                appointment.save()
            vacancy.delete()
    return JsonResponse({"result": "1"})
