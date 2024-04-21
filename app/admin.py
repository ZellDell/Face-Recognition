from django.contrib import admin
from .models import Admin, YearLevel, Students, Attendance, AttendanceDetails
# Register your models here.


admin.site.register(Admin)

admin.site.register(YearLevel)
admin.site.register(Students)
admin.site.register(Attendance)
admin.site.register(AttendanceDetails)