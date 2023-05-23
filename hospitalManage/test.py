from app.models import Department, Notification, Vacancy, Appointment, Doctor, Leave, Admin, User, Schedule

print("hello")
admin = Admin(
    username="wunanli",
    password="123456"
)
admin.save()
with open("/Users/wuxinyu/Documents/Github/Hospital-Backend/hospitalManage/file.txt", "w") as f:
    f.write("hello")
    f.close()
