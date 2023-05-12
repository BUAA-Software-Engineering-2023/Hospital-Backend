from django.db import models
import random
from faker import Faker

class Department(models.Model):
    department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=20, blank=False)
    department_type = models.CharField(max_length=20, blank=False)


class Doctor(models.Model):
    doctor_id = models.AutoField(primary_key=True)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=200, blank=False)
    doctor_name = models.CharField(max_length=200, blank=False)
    doctor_gender = models.CharField(max_length=200)
    doctor_image = models.ImageField(default='')
    doctor_introduction = models.CharField(max_length=200)


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    phone_number = models.CharField(max_length=200, blank=False)
    passwd = models.CharField(max_length=20)
    avatar = models.ImageField(default='')


class Patient(models.Model):
    patient_id = models.AutoField(primary_key=True)
    user_id = models.ManyToManyField(User)
    patient_name = models.CharField(max_length=200, blank=False)
    patient_gender = models.CharField(max_length=200)
    identification = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=200, blank=False)
    absence = models.IntegerField(default=0)
    address = models.CharField(max_length=200)


class MedicalRecord(models.Model):
    medical_record_id = models.AutoField(primary_key=True)
    doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE)
    department_id = models.ForeignKey(Department, on_delete=models.CASCADE)
    symptom = models.CharField(max_length=200)
    prescription = models.CharField(max_length=200)
    result = models.CharField(max_length=200)
    advice = models.CharField(max_length=200)


class Message(models.Model):
    message_id = models.AutoField(primary_key=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.CharField(max_length=200)
    message_time = models.DateField(blank=False)
    is_read = models.BooleanField()


class Appointment(models.Model):
    appointment_id = models.AutoField(primary_key=True)
    doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient_id = models.ForeignKey(Patient, on_delete=models.CASCADE)
    appointment_time = models.DateTimeField()
    appointment_status = models.CharField(max_length=200)


class Notification(models.Model):
    notification_id = models.BigAutoField(primary_key=True)
    content = models.CharField(max_length=255)
    title = models.CharField(max_length=200)
    notification_time = models.DateField()
    notification_link = models.CharField(max_length=255)

class Code(models.Model):
    phone_number = models.BigIntegerField(primary_key=True)
    create_time = models.DateTimeField()
    expire_time = models.DateTimeField()


class Admin(models.Model):
    notification_id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)


class Payment(models.Model):
    payment_id = models.BigAutoField(primary_key=True)
    amount = models.FloatField()
    payment_status = models.CharField(max_length=200)
    appointment_id = models.ForeignKey(Appointment, on_delete=models.CASCADE)


class Vacancy(models.Model):
    vacancy_id = models.BigAutoField(primary_key=True)
    doctor_id = models.ManyToManyField(Doctor)
    vacancy_count = models.IntegerField(default=100)
    vacancy_left = models.IntegerField(default=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()


class Leave(models.Model):
    leave_id = models.BigAutoField(primary_key=True)
    doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    type = models.CharField(max_length=200)
    reseon = models.CharField(max_length=255)
    leave_status = models.CharField(max_length=100)


class Schedule(models.Model):
    schedule_id = models.BigAutoField(primary_key=True)
    schedule_day = models.DateField()
    schedule_ismorning = models.IntegerField(default=0)
    doctor_id = models.ForeignKey(Doctor, on_delete=models.CASCADE)

class CarouselMap(models.Model):
    carouselmap_id = models.AutoField(primary_key=True)
    carouselmap_img = models.ImageField()
    carouselmap_link = models.CharField(max_length=100)