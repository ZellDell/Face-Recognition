from django.db import models

class Accounts(models.Model):
    AccountID = models.AutoField(primary_key=True)
    UserType = models.CharField(max_length=50)
    Fullname = models.CharField(max_length=100)
    Username = models.CharField(max_length=50, unique=True)
    Password = models.CharField(max_length=100)
    last_login = models.DateTimeField(auto_now=True)
    # Add more fields as needed

class Subject(models.Model):
    SubjectID = models.AutoField(primary_key=True)
    SubjectName = models.CharField(max_length=100, default='Default Subject Name')  # Define a default value
    Account = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    # Add more fields as needed

class Schedule(models.Model):
    ScheduleID = models.AutoField(primary_key=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    Weekday = models.CharField(max_length=10)
    Start_time = models.TimeField()
    End_time = models.TimeField()

class YearLevel(models.Model):
    YearLevelID = models.AutoField(primary_key=True)
    YearLevel = models.CharField(max_length=50)

class Student(models.Model):
    StudentID = models.AutoField(primary_key=True)
    Fullname = models.CharField(max_length=100)
    year_level = models.ForeignKey(YearLevel, on_delete=models.CASCADE)
    Image_path = models.CharField(max_length=255)
    # Add more fields as needed

class Attendance(models.Model):
    AttendanceID = models.AutoField(primary_key=True)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    date = models.DateField()

class AttendanceDetails(models.Model):
    AttendanceDetailsID = models.AutoField(primary_key=True)
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    Time_In = models.DateTimeField(auto_now_add=True)
    # Add more fields as needed