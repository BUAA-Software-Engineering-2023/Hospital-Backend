from django.shortcuts import render
from django.views import View
from django.http import HttpResponse, JsonResponse
from .models import Department, Doctor, Notification,CarouselMap,News,Vacancy


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
    def get(self,request):
        data = []
        departmentId = request.GET.get('department')
        date = request.GET.get('date')
        doctor_id_list = Vacancy.objects.filter(start_time__contains=date).values('doctor_id').distinct()
        for doctor_id in doctor_id_list:
            doctor_id=doctor_id['doctor_id']
            doctor_info=Doctor.objects.get(doctor_id=doctor_id)
            vacancies = Vacancy.objects.filter(start_time__contains=date,doctor_id=doctor_id).values('vacancy_count','start_time')
            available = []
            for vacancy in vacancies:
                available.append({"time":vacancy['start_time'],"num":vacancy['vacancy_count']})
            # print()
            print(departmentId)
            data.append({
                "id": doctor_id,
                "name": doctor_info.doctor_name,
                "department":Department.objects.get(department_id=departmentId).department_name,
                "image":'',
                "introduction":doctor_info.doctor_introduction,
                "available|1-2":available
            })

        response = {
            "result":"1",
            "data":data,
        }
        return JsonResponse(response)


