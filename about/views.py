from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


@api_view['GET']
@csrf_exempt
def about():
    return Response({'message': 'Hello, world!'})
