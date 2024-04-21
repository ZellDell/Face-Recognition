from django.db import models

class Admin(models.Model):
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)

class YearLevel(models.Model):
    year = models.IntegerField()
    total_students = models.IntegerField()

class Students(models.Model):
    name = models.CharField(max_length=100)
    year_level = models.ForeignKey(YearLevel, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to='media/')
    face_image_path = models.CharField(max_length=255)
    # Add more fields as needed

class Attendance(models.Model):
    date = models.DateField()
    total_students_present = models.IntegerField()
    # Add more fields as needed

class AttendanceDetails(models.Model):
    student = models.ForeignKey(Students, on_delete=models.CASCADE)
    date = models.DateField()
    First_in = models.TimeField()
    Last_in = models.TimeField()
    # Add more fields as needed
