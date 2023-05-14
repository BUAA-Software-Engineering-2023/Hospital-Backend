from datetime import datetime
import json

from django.shortcuts import render
from app.models import Department, Notification, Vacancy, Appointment, Doctor
from django.views import View

from django.http import HttpResponse, JsonResponse


# Create your views here.
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
        return JsonResponse({"result": 1, "message": "Notification created successfully"})


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
                        excess_appointments = updated_appointments.order_by('-appointment_id')[:excess_appointments_count]
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

        response = {"result": 1, "message": "successfully"}
        return JsonResponse(response)
