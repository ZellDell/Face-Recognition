from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login

# Create your views here.
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64

import cv2
import face_recognition
import numpy as np
import os

import json
from django.http import JsonResponse


def home(request):  
   
    return render(request, 'app/index.html')



# Initialize lists to store images, encodings, and names
known_images = []
known_face_encodings = []
known_face_names = []
known_face_paths = []

# Path to the directory containing the student images
faces_directory = "media/faces"

# Iterate through the year level directories
for year_level in os.listdir(faces_directory):
    year_level_directory = os.path.join(faces_directory, year_level)
    
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





@csrf_exempt
def process_frame(request):
  
    if request.method == 'POST':
        
        # Decode and process the received image data
        data = json.loads(request.body.decode('utf-8'))
        image = data.get('image_data')
   
        image_data = base64.b64decode(image.split(',')[1])

        # Convert the image data to a numpy array
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Convert the frame to RGB (OpenCV uses BGR by default)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Perform face detection
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        if len(face_locations) == 0:
            print("No face detected")
        else:
            print("Face detected")

        # Initialize list to store recognized face names
        recognized_faces = []

        for face_encoding in face_encodings:
            # Compare the face encoding with known face encodings
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

            best_match_index = np.argmin(face_distances)
    
            # If the smallest distance is less than a certain threshold, consider it a match
            if face_distances[best_match_index] < 0.6:
                name = known_face_names[best_match_index]
                # year_level = os.path.basename(os.path.dirname(os.path.dirname(known_images[best_match_index])))
                path_to_image = known_face_paths[best_match_index]
                print("Face recognized: {}".format(name))
            else:
                name = "Unknown"
                print("Unknown face")

            recognized_faces.append({'name': name,  'image_path': path_to_image})
            

        # Send back the recognized faces to the client
        response_data = [{'top': top * 2, 'right': right * 2, 'bottom': bottom * 2, 'left': left * 2}
                         for (top, right, bottom, left) in face_locations]

        print(response_data)
        return JsonResponse({'recognized_faces': recognized_faces, 'response_data': response_data})

    else:
        return JsonResponse({'error': 'POST request required'})

def user_login(request):  # Renamed login to user_login
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Changed login to auth_login
            return redirect('home')  # Redirect to the 'home' view (index.html)
        else:
            # Handle invalid login
            # You can render the login form again with an error message
            return render(request, 'app/login.html', {'error_message': 'Invalid username or password'})

    return render(request, 'app/login.html') 