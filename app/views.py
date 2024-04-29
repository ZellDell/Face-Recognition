from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.models import AnonymousUser

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64

import cv2
import face_recognition
import numpy as np
import os

import json

from . import test

from keras.models import model_from_json

import time

from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password

from django.shortcuts import get_object_or_404

from .models import Accounts, Student, YearLevel, Subject, Schedule, Attendance, AttendanceDetails

from django.utils.text import slugify
from django.conf import settings
import shutil
from django.utils import timezone

from django.db import transaction

def home(request):  
   
    return render(request, 'app/index.html')


def students(request): 


    if request.method == 'POST':
        fullname = request.POST.get('fullname')
        yearlevel = request.POST.get('yearlevel')
        image = request.FILES.get('studentImage')
        action = request.POST.get('action')
        print("action", action)
        
        try:

            if action == 'create':
            

                if Student.objects.filter(Fullname=fullname, year_level__YearLevel=yearlevel).exists():
                    students = Student.objects.all()
                    return render(request, 'app/students.html', {'students': students, 'error_message': 'Student already exists'})

                year_level, _ = YearLevel.objects.get_or_create(YearLevel=yearlevel)
                

                yearlevel_directory = os.path.join(settings.MEDIA_ROOT, 'media/faces', year_level.YearLevel)
                
                if not os.path.exists(yearlevel_directory):
                    os.makedirs(yearlevel_directory)

                fullname_slug = slugify(fullname)

                name_directory = os.path.join(yearlevel_directory, fullname_slug)
                if not os.path.exists(name_directory):
                    os.makedirs(name_directory)


                image_path = os.path.join(name_directory, "1." + image.name.split('.')[-1]).replace("\\", "/")

                # Split the image_path by '/'
                split_path = image_path.split('/')

                # Remove the first element
                split_path.pop(0)

                # Join the remaining elements back into a string
                new_image_path = '/'.join(split_path)


                with open(image_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)

                student = Student.objects.create(
                        Fullname=fullname,
                        year_level=year_level,
                        Image_path=new_image_path
                    )
            else:
                studentID = request.POST.get('StudentID')

                student = Student.objects.get(pk=studentID)

                student.Fullname = fullname

                year_level, _ = YearLevel.objects.get_or_create(YearLevel=yearlevel)
                student.year_level = year_level

                yearlevel_directory = os.path.join(settings.MEDIA_ROOT, 'media/faces', year_level.YearLevel)




                    

                if image:

                    if not os.path.exists(yearlevel_directory):
                        os.makedirs(yearlevel_directory)

                    fullname_slug = slugify(fullname)

                    name_directory = os.path.join(yearlevel_directory, fullname_slug)

                    
                    if not os.path.exists(name_directory): 
                        os.makedirs(name_directory)

                    print("===========================================",name_directory)

                    # Save new image file
                    image_path = os.path.join(name_directory, "1." + image.name.split('.')[-1]).replace("\\", "/")

                    print(image_path)
                    # Split the image_path by '/'
                    split_path = image_path.split('/')

                    # Remove the first element
                    split_path.pop(0)

                    # Join the remaining elements back into a string
                    new_image_path = '/'.join(split_path)

                   # Save new image file
                    with open(image_path, 'wb+') as destination:
                        for chunk in image.chunks():
                            destination.write(chunk)


                    old_Image_path = student.Image_path.split('/')

                    old_Image_path.pop()

                    old_name_directory = '/'.join(old_Image_path)

                    delete_old_path = os.path.join(settings.MEDIA_ROOT, 'media', old_name_directory).replace("\\", "/")
                
                    if os.path.exists(delete_old_path):
                        shutil.rmtree(delete_old_path)

                    student.Image_path = new_image_path

                     # Remove old image file

                     
                    

                student.save()
            
            students = Student.objects.all()
            return render(request, 'app/student.html' , {'students': students})
        except Exception as e:
            print(e)
            return render(request, 'app/students.html', {'error_message': 'Error adding student'})
    
            


    if not isinstance(request.user, AnonymousUser):
        if request.user.UserType == 'Administrator':

            students = Student.objects.all()
            return render(request, 'app/students.html' , {'students': students})
        else:
            return redirect('home') 
        
    else:    
        return redirect('home') 
   
@csrf_exempt
def delete_student(request):
    try:

        if request.method == 'POST':
            
            data = json.loads(request.body.decode('utf-8'))
            student_id = data.get('student_id')
            
            # Retrieve student information from the database
            student = Student.objects.get(StudentID=student_id)
            # Split the Image_path by '/'
            path_elements = student.Image_path.split('/')
                
            # Remove the last element (filename)
            path_elements.pop()
                
            # Join the remaining elements back together with '/'
            directory_path = "media/" + '/'.join(path_elements)

            if os.path.exists(directory_path):
                shutil.rmtree(directory_path)

            
            student.delete()
            # Return success message or status code
            return JsonResponse({'message': 'Student deleted successfully'})
        else:
            return JsonResponse({'error': 'POST request required'})

    except Exception as e:
        print(e)

@csrf_exempt
def get_student_info(request):
    if request.method == 'POST':
        # Retrieve student ID from the request
        data = json.loads(request.body.decode('utf-8'))
       
        student_id = data.get('student_id')
        
        try:

            # Retrieve student information from the database
            student = Student.objects.get(StudentID=student_id)
            
            # Prepare data to send back as JSON response
            student_info = {
                'StudentID': student.StudentID,
                'fullname': student.Fullname,
                'yearlevel': student.year_level.YearLevel,
                'image_path': student.Image_path,
                # Add more fields as needed
            }
            
            # Return student information as JSON response
            return JsonResponse(student_info)
        
        except Student.DoesNotExist:
            # If student does not exist, return an error message
            return JsonResponse({'error': 'Student not found'}, status=404)
    
    else:
        # If request method is not POST, return an error message
        return JsonResponse({'error': 'POST request required'}, status=400)


# ================================================================

def professors(request): 

    if request.method == 'POST':
        Fullname = request.POST.get('fullname')
        Username = request.POST.get('username')
        Password = request.POST.get('password')

        action = request.POST.get('action')

        
        try:

            if action == 'create':
            

                if Accounts.objects.filter(Fullname=Fullname, Username=Username).exists():
                    accounts = Accounts.objects.filter(UserType='Professor')
                    return render(request, 'app/professor.html', {'accounts': accounts, 'error_message': 'Professor already exists'})

                hashed_password = make_password(Password)

                accs = Accounts.objects.create(
                        UserType='Professor',
                        Fullname=Fullname,
                        Username=Username,
                        Password=hashed_password
                    )
            else:
                AccountID = request.POST.get('AccountID')

                account = Accounts.objects.get(pk=AccountID)

                hashed_password = make_password(Password)

                account.Fullname = Fullname
                account.Username = Username
                account.Password = hashed_password

                account.save()
            
            accounts = Accounts.objects.filter(UserType='Professor')
            print("Check Accounts",accounts)
            return render(request, 'app/proessor.html' , {'accounts': accounts})
        except Exception as e:
            print(e)
            return render(request, 'app/professor.html', {'error_message': 'Error adding Professor'})


    if not isinstance(request.user, AnonymousUser):
        if request.user.UserType == 'Administrator':
            accounts = Accounts.objects.filter(UserType='Professor')
            return render(request, 'app/professor.html', {'accounts': accounts})
        else:
            return redirect('home') 
        
    else:    
        return redirect('home') 


@csrf_exempt
def delete_professor(request):
    try:

        if request.method == 'POST':
            data = json.loads(request.body.decode('utf-8'))
            account_id = data.get('AccountID')
            
            with transaction.atomic():
                # Retrieve professor's account
                account = Accounts.objects.get(AccountID=account_id)

                # Retrieve subjects associated with the professor's account
                subjects = Subject.objects.filter(Account=account)

                # Loop through each subject
                for subject in subjects:
                    # Retrieve schedules associated with the subject
                    schedules = Schedule.objects.filter(subject=subject)

                    # Delete schedules
                    schedules.delete()

                # Delete subjects
                subjects.delete()

                # Delete professor's account
                account.delete()
            # Return success message or status code
            return JsonResponse({'message': 'Student deleted successfully'})
        else:
            return JsonResponse({'error': 'POST request required'})

    except Exception as e:
        print(e)

# @csrf_exempt
# def get_professor_info(request):
    if request.method == 'POST':
        # Retrieve student ID from the request
        data = json.loads(request.body.decode('utf-8'))
       
        student_id = data.get('student_id')
        
        try:

            # Retrieve student information from the database
            student = Student.objects.get(StudentID=student_id)
            
            # Prepare data to send back as JSON response
            student_info = {
                'StudentID': student.StudentID,
                'fullname': student.Fullname,
                'yearlevel': student.year_level.YearLevel,
                'image_path': student.Image_path,
                # Add more fields as needed
            }
            
            # Return student information as JSON response
            return JsonResponse(student_info)
        
        except Student.DoesNotExist:
            # If student does not exist, return an error message
            return JsonResponse({'error': 'Student not found'}, status=404)
    
    else:
        # If request method is not POST, return an error message
        return JsonResponse({'error': 'POST request required'}, status=400)


def add_subject(request):
    if request.method == 'POST':
        account_id = request.POST.get('AccountID')  # Retrieve the AccountID from the form
        subject_name = request.POST.get('subjectName')
        weekday = request.POST.get('weekday')
        start_time = request.POST.get('startTime')
        end_time = request.POST.get('endTime')


        print(account_id, subject_name, weekday, start_time, end_time)
        # Retrieve the Account object
        account = get_object_or_404(Accounts, pk=account_id)

        # Create and save the Subject instance
        subject = Subject.objects.create(Account=account, SubjectName=subject_name)

        # Create and save the Schedule instance
        schedule = Schedule.objects.create(
            subject=subject,
            Weekday=weekday,
            Start_time=start_time,
            End_time=end_time
        )

        
        return redirect('professors')
    else:
        # Handle GET requests or other HTTP methods
        return render(request, 'professor.html', {'error': 'Method not allowed'})


# ================================================================================


def attendance(request):  
   

    
    if not isinstance(request.user, AnonymousUser):
        all_attendance_details = AttendanceDetails.objects.select_related(
            'attendance__schedule__subject',  
            'attendance__schedule__subject__Account',  
            'student__year_level'  
        ).all()


        return render(request, 'app/attendance.html', {'all_attendance_details': all_attendance_details})
        
    else:    
        return redirect('home') 
    


# Initialize lists to store images, encodings, and names
known_images = []
known_face_encodings = []
known_face_names = []
known_face_paths = []

# Path to the directory containing the student images
faces_directory = "media/faces"

if os.path.exists(faces_directory):
    for year_level in os.listdir(faces_directory):
        year_level_directory = os.path.join(faces_directory, year_level).replace("\\", "/")
        
        print(year_level_directory)
        # Iterate through the student directories within each year level
        for student_name in os.listdir(year_level_directory):
            student_directory = os.path.join(year_level_directory, student_name)
            
            # Initialize list to store student images
            student_images = []
            
            # Iterate through the images in the student directory
            for image_name in os.listdir(student_directory):
                image_path = os.path.join(student_directory, image_name)
                
                # Load the image and calculate its encoding
                image = face_recognition.load_image_file(image_path)
                face_encoding = face_recognition.face_encodings(image)[0]
                
                # Add the image and encoding to the student images list
                student_images.append((image, face_encoding))
            
            # If student has at least one image
            if student_images:
                # Calculate the average encoding for the student
                student_face_encoding = np.mean([enc for _, enc in student_images], axis=0)
                
                # Add the student's average encoding and name to the known lists
                known_images.extend([img for img, _ in student_images])
                known_face_encodings.append(student_face_encoding)
                known_face_names.append(student_name)
                known_face_paths.append(student_directory)

from datetime import datetime, timedelta

current_day = datetime.now().strftime('%A')

TodaySched = Schedule.objects.filter(Weekday=current_day)


def is_class_time(start_time, end_time):
    now = datetime.now().time()
    current_time = datetime.strptime(now.strftime("%H:%M"), "%H:%M").time()
    return start_time <= current_time <= end_time

def fetch_attendance(schedule):
    today = datetime.now().date()
    return Attendance.objects.filter(schedule=schedule, date=today)

def fetch_attendance_details(attendance):
    return AttendanceDetails.objects.filter(attendance=attendance)

def is_present(student_id, attendance_details):
    return any(detail.student_id == student_id for detail in attendance_details)

@csrf_exempt
def process_frame(request):

    for schedule in TodaySched:
        print(f"Subject: {schedule.subject.SubjectName}, Start Time: {schedule.Start_time}, End Time: {schedule.End_time}")
        if is_class_time(schedule.Start_time, schedule.End_time) is not True:
            break
            
            
    
        if request.method == 'POST':
            
            # Decode and process the received image data
            data = json.loads(request.body.decode('utf-8'))
            image = data.get('image_data')

            
    
            image_data = base64.b64decode(image.split(',')[1])

            # Convert the image data to a numpy array
            nparr = np.frombuffer(image_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Resize the frame to a 4:3 aspect ratio
            width = frame.shape[1]
            
            height = int(width * (4/3))

            resized_frame = cv2.resize(frame, (width, height))

            # Convert the frame to RGB (OpenCV uses BGR by default)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Perform face detection
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            # Initialize list to store recognized face names
            recognized_faces = []

            start_time = time.time()
            for face_encoding in face_encodings:
                # Compare the face encoding with known face encodings


                spoof = test.test(image=resized_frame, model_dir="app/resources/anti_spoof_models", device_id=0)
                isReal = spoof == 1
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

                best_match_index = np.argmin(face_distances)

                # If the smallest distance is less than a certain threshold, consider it a match
                if face_distances[best_match_index] < 0.6:
                    name = known_face_names[best_match_index]
                
                    path_to_image = known_face_paths[best_match_index]
                    print("Face recognized: {}".format(name))

                    fullname = name.replace('-', ' ')
                    student = Student.objects.filter(Fullname=fullname).first()
                    if student:
                        
                        current_date = timezone.now().date()
                     
                        attendance_exists = Attendance.objects.filter(schedule=schedule, date=current_date).exists()
                        if attendance_exists:
                           
                            is_present = AttendanceDetails.objects.filter(attendance__schedule=schedule, attendance__date=current_date, student=student).exists()
                        else:
                            is_present = False
                    else:
                        is_present = False
                else:
                    name = "Unknown"
                    print("Unknown face")

                


                    print(is_present_flag)
                recognized_faces.append({'name': name,  'image_path': path_to_image, 'isReal': bool(isReal), 'isPresent': bool(is_present), 'schedule': {'subject_name': schedule.subject.SubjectName if schedule else None, 'weekday': schedule.Weekday if schedule else None,'start_time' : schedule.Start_time.strftime('%H:%M') if schedule else None,'end_time': schedule.End_time.strftime('%H:%M') if schedule else None}})

                elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds

                print("Face recognition took {:.2f} ms".format(elapsed_time))
    

            # Send back the recognized faces to the client
            response_data = [{'top': top * 2, 'right': right * 2, 'bottom': bottom * 2, 'left': left * 2}
                            for (top, right, bottom, left) in face_locations]

            print(response_data)
            return JsonResponse({'recognized_faces': recognized_faces, 'response_data': response_data})

        else:
            return JsonResponse({'error': 'POST request required'})


def user_login(request):  # Renamed login to user_login
    if request.method == 'POST':
        print(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, Username=username, Password=password)
        if user is not None:
            auth_login(request, user)  # Changed login to auth_login
            return redirect('home')  # Redirect to the 'home' view (index.html)
        else:
            # Handle invalid login
            # You can render the login form again with an error message
            return render(request, 'app/login.html', {'error_message': 'Invalid username or password'})


    
    if not isinstance(request.user, AnonymousUser):
        return redirect('home')

    return render(request, 'app/login.html') 


def user_logout(request):
    logout(request)  # Call the logout function
    return redirect('home')



# def user_register(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         # Check if the username already exists
#         if Accounts.objects.filter(Username=username).exists():
#             return render(request, 'app/login.html', {'error_message': 'Username already exists'})

#         # Hash the password
#         hashed_password = make_password(password)
#         print("hashed_password", hashed_password)
#         # Create a new user object
#         new_user = Accounts(Username=username, Password=hashed_password)

#         # Save the user object to the database
#         new_user.save()

#         # Optionally, you can log in the user after registration
#         # auth_login(request, new_user)

#         # Redirect to the home page or any other appropriate page
#         return redirect('home')

#     return render(request, 'app/login.html')

@csrf_exempt
def check_attendance(request):
    if request.method == 'POST':
        try:
            # Decode the request body to extract the student's face information
            data = json.loads(request.body.decode('utf-8'))
            face = data.get('face', {})
            print("===========", face)

            # Get the current date and time
            current_datetime = timezone.now()

            # Extract the student's full name and replace whitespace with hyphens
            name = face.get('name', '').replace('-', ' ')

            # Extract the schedule information
            schedule_info = face.get('schedule', {})
            subject_name = schedule_info.get('subject_name', '')
            weekday = schedule_info.get('weekday', '')
            start_time = schedule_info.get('start_time', '')
            end_time = schedule_info.get('end_time', '')

            # Query the Student model to find a matching student
            try:
                student = Student.objects.get(Fullname=name)
            except Student.DoesNotExist:
                return JsonResponse({'error': f"No student found with name: {name}"})

            # Check if there is a schedule currently ongoing
            try:
                # Query the Schedule model to find the schedule with the provided information
                schedule = Schedule.objects.get(subject__SubjectName=subject_name, Weekday=weekday, Start_time=start_time, End_time=end_time)

            except Schedule.DoesNotExist:
                return JsonResponse({'error': "No matching schedule found"})

            # Get or create an attendance record for today's date and the schedule
            attendance, _ = Attendance.objects.get_or_create(schedule=schedule, date=current_datetime.date())

            # Check if AttendanceDetails already exists for this student and attendance record
            if not AttendanceDetails.objects.filter(attendance=attendance, student=student).exists():
                # Create AttendanceDetails record for the recognized face with the current time
                AttendanceDetails.objects.create(attendance=attendance, student=student, Time_In=current_datetime)

            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'POST request required'})