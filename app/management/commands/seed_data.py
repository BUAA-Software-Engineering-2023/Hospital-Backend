import random

from django.core.management.base import BaseCommand
from faker import Faker
from pymysql import IntegrityError

from app.models import Department, Doctor, User, Patient, MedicalRecord, Message, Appointment, Notification, Code, \
    Admin, Payment, Vacancy, Leave, Schedule

fake = Faker()


class Command(BaseCommand):
    help = 'Seed data for the application'

    def handle(self, *args, **options):
        self.seed_departments()
        self.seed_doctors()
        self.seed_users()
        self.seed_patients()
        self.seed_medical_records()
        self.seed_messages()
        self.seed_appointments()
        self.seed_notifications()
        self.seed_codes()
        self.seed_admins()
        self.seed_payments()
        self.seed_vacancies()
        self.seed_leaves()
        self.seed_schedules()

    def seed_departments(self):
        # Generate department data
        for _ in range(5):
            department = Department.objects.create(
                department_name=fake.word(),
                department_type=fake.word()
            )

    def seed_doctors(self):
        # Generate doctor data
        departments = Department.objects.all()
        for _ in range(10):
            doctor = Doctor.objects.create(
                department_id=departments[fake.random_int(0, len(departments) - 1)],
                phone_number=fake.phone_number(),
                doctor_name=fake.name(),
                doctor_gender=fake.random_element(['Male', 'Female']),
                doctor_image='',
                doctor_introduction=fake.paragraph()
            )

    def seed_users(self):
        # Generate user data
        for _ in range(10):
            user = User.objects.create(
                phone_number=fake.phone_number(),
                passwd=fake.password(),
                avatar=''
            )

    def seed_patients(self):
        # Generate patient data
        users = User.objects.all()
        for _ in range(10):
            patient = Patient.objects.create(
                patient_name=fake.name(),
                patient_gender=fake.random_element(['Male', 'Female']),
                identification=fake.random_number(digits=18),
                phone_number=fake.phone_number(),
                absence=fake.random_int(0, 10),
                address=fake.address()
            )
            patient.user_id.add(users[fake.random_int(0, len(users) - 1)])

    def seed_medical_records(self):
        # Generate medical record data
        doctor_list = Doctor.objects.all()
        doctor = random.choice(doctor_list)
        patient = random.choice(Patient.objects.all())
        department = doctor.department_id

        medical_record = MedicalRecord(
            doctor_id=doctor,
            patient_id=patient,
            department_id=department,
            symptom=fake.text(),
            prescription=fake.text(),
            result=fake.text(),
            advice=fake.text(),
            medical_record_date=fake.date()
        )
        medical_record.save()

    def seed_messages(self):
        # Generate message data
        users = User.objects.all()
        user = random.choice(users)
        for _ in range(10):
            message = Message(
                user_id=user,
                title=fake.sentence(),
                content=fake.text(),
                message_time=fake.date(),
                is_read=fake.boolean()
            )
            try:
                message.save()
            except IntegrityError:
                continue

    def seed_appointments(self):
        # Generate appointment data
        doctors = Doctor.objects.all()
        patients = Patient.objects.all()
        for _ in range(10):
            appointment = Appointment.objects.create(
                doctor_id=doctors[fake.random_int(0, len(doctors) - 1)],
                patient_id=patients[fake.random_int(0, len(patients) - 1)],
                appointment_time=fake.date_time(),
                appointment_status=fake.random_element(['Scheduled', 'Cancelled', 'Completed'])
            )

    def seed_notifications(self):
        # Generate notification data
        for _ in range(10):
            notification = Notification.objects.create(
                content=fake.text(max_nb_chars=255),
                title=fake.sentence(nb_words=4),
                notification_time=fake.date(),
                notification_link=fake.url()
            )

    # def seed_codes(self):
    #     # Generate code data
    #     for _ in range(10):
    #         code = Code.objects.create(
    #             phone_number=fake.random_number(digits=10),
    #             create_time=fake.date_time(),
    #             expire_time=fake.date_time()
    #         )

    def seed_admins(self):
        # Generate admin data
        for _ in range(10):
            admin = Admin.objects.create(
                username=fake.user_name(),
                password=fake.password()
            )

    def seed_payments(self):
        # Generate payment data
        appointments = Appointment.objects.all()
        for _ in range(10):
            payment = Payment.objects.create(
                amount=fake.random.uniform(10, 50),
                payment_status=fake.random_element(['Pending', 'Paid', 'Cancelled']),
                appointment_id=appointments[fake.random_int(0, len(appointments) - 1)]
            )

    def seed_vacancies(self):
        # Generate vacancy data
        doctors = Doctor.objects.all()
        for _ in range(10):
            vacancy = Vacancy.objects.create(
                vacancy_count=fake.random_int(1, 100),
                vacancy_left=fake.random_int(0, 100),
                start_time=fake.date_time(),
                end_time=fake.date_time()
            )
            vacancy.doctor_id.set(doctors)

    def seed_leaves(self):
        # Generate leave data
        doctors = Doctor.objects.all()
        for _ in range(10):
            leave = Leave.objects.create(
                doctor_id=doctors[fake.random_int(0, len(doctors) - 1)],
                start_time=fake.date_time(),
                end_time=fake.date_time(),
                type=fake.random_element(['Sick Leave', 'Annual Leave']),
                reseon=fake.sentence(),
                leave_status=fake.random_element(['Approved', 'Pending', 'Rejected'])
            )

    def seed_schedules(self):
        # Generate schedule data
        doctors = Doctor.objects.all()
        for _ in range(10):
            schedule = Schedule.objects.create(
                schedule_day=fake.date(),
                schedule_ismorning=fake.random_int(0, 1),
                doctor_id=doctors[fake.random_int(0, len(doctors) - 1)]
            )
