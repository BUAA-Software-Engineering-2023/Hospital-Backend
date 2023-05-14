import hashlib

from django.http import JsonResponse
from django.shortcuts import render
from app.models import Admin,Doctor,User,Schedule,Department,Vacancy,Appointment
from django.views import View
import json
# Create your views here.

class LoginView(View):
    def get(self,request):
        json_str = request.body
        json_obj = json.loads(json_str)
        user_name =json_obj['user_name']
        passwd = json_obj['passwd']

        data_passwd = Admin.objects.filter(user_name=user_name).first().password
        if data_passwd is None:
            response = {
                "result": "0",
                "reason": "admin not exist"
            }
            return JsonResponse(response)
        else:
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
    def post(self,request):
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
    def delete(self,request):
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

    def put(self,request):
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
    def get(self,request):
        try:
            data = []
            doctor_id_list = Doctor.objects.values('doctor_id').distinct()
            for doctor in doctor_id_list:
                doctor_id = doctor['doctor_id']
                day = []
                schedules = Schedule.objects.filter(doctor_id=doctor_id).values('schedule_ismorning',"schedule_day",'schedule_id')
                if schedules is not None:
                    for schedule in schedules:
                        day_data = {
                            "schedule":schedule['schedule_id'],
                            "ismorning":schedule['schedule_ismorning'],
                            "date":schedule['schedule_day']
                        }
                        day.append(day_data)

                doctors = Doctor.objects.get(doctor_id=doctor_id)
                info = {
                    "doctor_id":doctor_id,
                    "name": doctors.doctor_name,
                    "department": Department.objects.get(department_id=doctors.department_id_id).department_name,
                    "day":day
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

    def post(self,request):
        try:
            json_str = request.body
            json_obj = json.loads(json_str)
            doctor_id = json_obj['doctor_id']
            is_morning = json_obj['is_morning']
            date = json_obj['date']
            schedule = Schedule(
                schedule_day=date,
                schedule_ismorning = is_morning,
                doctor_id_id = doctor_id
            )
            schedule.save()
            response = {
                "result": "1"
            }
            return JsonResponse(response)
        except:
            response = {
                "result": "0"
            }
            return JsonResponse(response)
    def delete(self,request):
        # try:
            json_str = request.body
            json_obj = json.loads(json_str)
            schedule_id = json_obj['schedule_id']
            schedule = Schedule.objects.get(schedule_id=schedule_id)
            doctor_id = schedule.doctor_id
            is_morning = schedule.schedule_ismorning
            date = schedule.schedule_day

            vacancies = Vacancy.objects.filter(start_time__contains=date,doctor_id=doctor_id)

            for vacancy in vacancies:
                time=vacancy.start_time
                if time.hour>is_morning*12 and time.hour<is_morning*12+12:
                    appointments = Appointment.objects.filter(doctor_id=doctor_id,appointment_time=time)
                    for appointment in appointments:
                        Appointment.delete(appointment)
                    Vacancy.delete(vacancy)

            Schedule.delete(schedule)
            response = {
                "result": "1"
            }
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
