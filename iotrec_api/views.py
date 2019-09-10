from django.contrib import auth
from django.shortcuts import render
from rest_framework.generics import get_object_or_404
from rest_framework_jwt.views import ObtainJSONWebToken

import iotrec_api
from iotrec_api.models import Thing, Category, User
from iotrec_api.serializers import ThingSerializer, CategorySerializer, CategoryFlatSerializer
from rest_framework import generics, viewsets

from django.http import HttpResponseRedirect
#from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, UserSerializerWithToken


@api_view(['GET', 'PATCH'])
def current_user(request):
    """
    Determine the current user by their token, and return their data
    """

    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    elif request.method == 'PATCH':
        serializer = UserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



#@api_view(['PATCH'])
#def update_current_user(request):


#class CurrentUserViewSet(viewsets.ViewSet):
#    #queryset = User.objects.all()
#    #serializer_class = UserSerializer
#
#    @staticmethod
#    def retrieve(self, request):
#        #queryset = User.objects.all()
#        #user = get_object_or_404(queryset, pk=pk)
#        #serializer = UserSerializer(user)
#        serializer = UserSerializer(request.user)
#        return Response(serializer.data)
#
#    @staticmethod
#    def update(self, request, pk=None):
#        queryset = User.objects.all()
#        user = get_object_or_404(queryset, pk=pk)
#        serializer = UserSerializer(user)
#        #serializer = UserSerializer(request.user)
#        if serializer.is_valid():
#            serializer.save()
#            return Response(serializer.data, status=status.HTTP_200_OK)
#        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserApiView(APIView):
    """
    API View for Users.
    GET method does not exist.
    POST method allows creating a new User.
    """

    permission_classes = (permissions.AllowAny,)

    @staticmethod
    def post(request, format=None):
        serializer = UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # class VenueViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Venues to be viewed or edited.
    """
    # queryset = Venue.objects.all()#.order_by('-created_at')
    # serializer_class = VenueSerializer


# class ThingListCreate(generics.ListCreateAPIView):
#    queryset = Thing.objects.all()
#    serializer_class = ThingSerializer

class ThingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows things to be viewed or edited.
    """
    queryset = Thing.objects.all()  # .order_by('-created_at')
    serializer_class = ThingSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(level=0)
    serializer_class = CategorySerializer


class CategoryFlatViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryFlatSerializer