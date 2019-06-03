from django.shortcuts import render

from iotrec_api.models import Thing
from iotrec_api.serializers import ThingSerializer
from rest_framework import generics, viewsets

from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, UserSerializerWithToken


@api_view(['GET'])
def current_user(request):
    """
    Determine the current user by their token, and return their data
    """

    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserList(APIView):
    """
    Create a new user. It's called 'UserList' because normally we'd have a get
    method here too, for retrieving a list of all User objects.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#class ThingListCreate(generics.ListCreateAPIView):
#    queryset = Thing.objects.all()
#    serializer_class = ThingSerializer

class ThingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows things to be viewed or edited.
    """
    queryset = Thing.objects.all()#.order_by('-created_at')
    serializer_class = ThingSerializer