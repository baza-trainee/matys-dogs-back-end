from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.http import HttpResponse
from django.core.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from . import models
import json
import re
import os
# Create your views here.


def home(request):
    return HttpResponse(os.environ.get('DOCUMENTETION'))


@csrf_exempt
@api_view(['POST'])
def register(request):
    if request.method == 'POST':
        # get the data from the request
        data = json.loads(request.body)
        # check if the password is valid
        password_regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).{8,}$'
        if not re.match(password_regex, data['password']):
            return Response({'error': 'password does not meet the requirements'}, status=400)
        # check if the user is already exist
        old_user = models.UserModel.objects.filter(email=data['email'])
        if old_user:
            return Response({'error': 'the user is already exist'}, status=400)
        # hash the password
        passwordHash = make_password(data['password'], salt=None)
        # create a new user
        new_user = models.UserModel.objects.create(
            email=data['email'], passwordHash=passwordHash)
        new_user.save()
        return Response({'massage': 'the user is created', 'email': data['email'], 'password': passwordHash}, status=status.HTTP_201_CREATED)


@csrf_exempt
@api_view(['POST'])
def login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        # get the user from the database
        user = models.UserModel.objects.filter(email=data['email']).first()
        # check if the user is exist
        if not user:
            return Response({'error': 'the user is not exist'}, status=400)
        # check if the password is correct
        if not check_password(data['password'], user.passwordHash):
            return Response({'error': 'the password is incorrect'}, status=400)
        return Response({'massage': 'the user is logged in'}, status=status.HTTP_200_OK)
