from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from .models import Department
# Create your views here.

class DepartmentList(View):
    def get(self,request):
        type = []
        data = Department.objects.values('department_type').distinct()
        for obj in data:
            child = []
            b = Department.objects.filter(department_type=obj.get('department_type')).values('department_name','department_id')
            for c in b:
                child.append({
                    "id": c.get('department_id'),
                    "name":c.get('department_name')
                })
            print()
            type.append({
                            "name": obj.get('department_type'),
                            "children": child
                                     })
        print(type)
        return HttpResponse(200)
