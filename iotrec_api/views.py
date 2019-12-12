import datetime

from django.contrib import auth
from django.db.models import Case, When, Q, BooleanField, Avg, F, DateTimeField, Func, ExpressionWrapper, fields, \
    DurationField
from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import make_aware
from rest_framework.generics import get_object_or_404
from rest_framework.renderers import JSONRenderer
from rest_framework_jwt.views import ObtainJSONWebToken

import iotrec_api
from iotrec_api.models import Thing, Category, User, Recommendation, Feedback, Preference, Rating, Context, Stay, \
    IotRecSettings
from iotrec_api.permissions import IsSignupOrIsAuthenticated
from iotrec_api.serializers import ThingSerializer, CategorySerializer, CategoryFlatSerializer, \
    RecommendationSerializer, FeedbackSerializer, PreferenceSerializer, RatingSerializer, ContextSerializer, \
    StaySerializer
from rest_framework import generics, viewsets, mixins

from django.http import HttpResponseRedirect, JsonResponse
# from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView

from iotrec_api.utils import similarity_reference
from iotrec_api.utils.category import calc_items_in_cat_full, calc_items_in_cat_list
from iotrec_api.utils.context import get_time_of_day
from iotrec_api.utils.thing import get_crowdedness
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


# @api_view(['PATCH'])
# def update_current_user(request):


# class CurrentUserViewSet(viewsets.ViewSet):
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

'''
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
'''


class UserViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """
    User API endpoint.
    """
    # queryset = User.objects.all()
    serializer_class = UserSerializerWithToken
    permission_classes = (IsSignupOrIsAuthenticated,)

    def create(self, request, **kwargs):
        serializer = UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        queryset = User.objects.filter(id=self.request.user.id)
        #queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset


# class ThingListCreate(generics.ListCreateAPIView):
#    queryset = Thing.objects.all()
#    serializer_class = ThingSerializer

class ThingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows things to be viewed or edited.
    """
    queryset = Thing.objects.all()  # .order_by('-created_at')
    serializer_class = ThingSerializer

    '''
    @action(detail=True)
    def occupation(self, request, pk=None):
        # get the number of active stays
        active_stays = Stay.objects.filter(thing=pk, end__isnull=True).all().count()
        # put into dict
        data = {}
        data['occupation'] = active_stays
        return JsonResponse(data)
    '''

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        instance = serializer.instance
        #for cat in instance.categories.all():
        #    cat.save()
        calc_items_in_cat_list(instance.categories.all())

        #calc_items_in_cat_full()

        similarity_reference.calculate_similarity_references_per_thing(instance)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        categories_before = set(instance.categories.all())

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        categories_after = set(instance.categories.all())

        #for cat in (categories_before | categories_after):
        #    cat.save()
        calc_items_in_cat_list((categories_before | categories_after))

        similarity_reference.calculate_similarity_references_per_thing(instance)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        '''
        # get average stay time at this Thing
        past_stays = Stay.objects.annotate(
            is_ended=Case(
                When(
                    condition=Q(end__isnull=False),
                    then=True
                ),
                default=False,
                output_field=BooleanField()
            )
        ).filter(thing=instance, is_ended=True)

        past_stays = Stay.objects.filter(end__isnull=False).all()

        stay_time = ExpressionWrapper(F('end') - F('start'), output_field=DurationField())
        avg_stay_time = past_stays.annotate(
            stay_time=stay_time
        ).aggregate(
            avg_stay_time=Avg('stay_time')
        )['avg_stay_time']
        '''

        # check if there are any active Stays for the Thing that need to be ended
        stays = Stay.objects.filter(thing=instance, end=None).all()
        for stay in stays:
            # if the last checkin was more than 15 minutes ago, terminate the stay
            if (timezone.now() - stay.last_checkin).total_seconds() > 15 * 60:
                stay.end = stay.last_checkin
                stay.save()

        # check if there is an active Stay for the current User and Thing
        try:
            # if yes, update the last_checkin
            stay = Stay.objects.filter(thing=instance, user=request.user, end=None)[:1].get()
            stay.last_checkin = timezone.now()
            stay.save()
        except Stay.DoesNotExist:
            # if not, create a new Stay
            Stay.objects.create(thing=instance, user=request.user)

        serializer = self.get_serializer(instance)
        return_data = serializer.data
        return_data['occupation'] = stays.count()
        #print(return_data)
        return Response(return_data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(level=0)
    serializer_class = CategorySerializer


class CategoryFlatViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryFlatSerializer
    authentication_classes = []
    permission_classes = []


# class ThingCreateAPIView(generics.CreateAPIView):
#    serializer_class = ThingSerializer


# class ThingSingleAPIView(generics.RetrieveUpdateDestroyAPIView):
#    queryset = Thing.objects.all()
#    serializer_class = ThingSerializer


# class ThingListAPIView(generics.ListCreateAPIView):
#    queryset = Thing.objects.all()
#    serializer_class = ThingSerializer


class RecommendationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows recommendations to be viewed or edited.
    """
    # queryset = Recommendation.objects.all()
    serializer_class = RecommendationSerializer

    def get_queryset(self):
        queryset = Recommendation.objects.filter(user=self.request.user)
        #queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset

    def create(self, request, *args, **kwargs):
        print(request.data)
        
        settings = IotRecSettings.load()

        # if given experiment ID is 0, set it to none
        if request.data.get('experiment') is not None and request.data['experiment'] == 0:
            request.data['experiment'] = None
        elif request.data.get('experiment') is None:
            request.data['experiment'] = None

        # only get real crowdedness if we're not in evaluation mode
        # in evaluation mode, supply dummy data for crowdedness and time_of_day
        if settings.evaluation_mode is True:
            request.data['context']['crowdedness_raw'] = None
            request.data['context']['time_of_day_raw'] = "NOON"
        else:
            request.data['context']['crowdedness_raw'] = get_crowdedness(request.data['thing'])
            request.data['context']['time_of_day_raw'] = get_time_of_day(datetime.datetime.now().time())

        # convert empty context strings to None
        if request.data.get('context') is not None:
            if request.data['context'].get('weather_raw') is not None and request.data['context']['weather_raw'] == "":
                request.data['context']['weather_raw'] = None
            if request.data['context'].get('crowdedness_raw') is not None and request.data['context']['crowdedness_raw'] == "":
                request.data['context']['crowdedness_raw'] = None

        serializer = self.get_serializer(data={
            **request.data,
            "user": request.user.id
        })

        print(serializer.__dict__)

        try:
            if serializer.is_valid():
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except KeyError as e:
            print(e.__dict__)
            return Response("", status=status.HTTP_400_BAD_REQUEST)


class FeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows feedbacks to be viewed or edited.
    """
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        return Feedback.objects.filter(recommendation=self.kwargs['recommendation_pk'])

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data={
            **request.data,
            "recommendation": self.kwargs['recommendation_pk'],
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RatingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ratings to be viewed or edited.
    """
    serializer_class = RatingSerializer

    def get_queryset(self):
        return Rating.objects.filter(recommendation=self.kwargs['recommendation_pk'])

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data={
            **request.data,
            "recommendation": self.kwargs['recommendation_pk'],
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PreferenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows preferences to be viewed or edited.
    """
    serializer_class = PreferenceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={
            **request.data,
            "user": request.user.id,
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    '''
    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={
            **request.data,
            "category": request.data['id'],
            "user": request.user.id,
        })
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK, headers=headers)
    '''

    # def list(self, request, **kwargs):
    #    queryset = Preference.objects.filter(user=self.kwargs['user_pk'])
    #    serializer = PreferenceSerializer(queryset, many=True)
    #    return Response(serializer.data)

    def get_queryset(self):
        return Preference.objects.filter(user=self.kwargs['user_pk'])


'''
class ContextViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a recommendation's context to be viewed or edited.
    """
    serializer_class = ContextSerializer

    def get_queryset(self):
        return Context.objects.filter(recommendation=self.kwargs['recommendation_pk'])

    def create(self, request, *args, **kwargs):
        print(request.data)
        get_crowdedness(1)
        serializer = self.get_serializer(data={
            **request.data,
            "recommendation": self.kwargs['recommendation_pk'],
            #"crowdedness": get_crowdedness()
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
'''


class StayViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows a user's stays to be viewed or edited.
    """
    serializer_class = StaySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={
            **request.data,
            "user": request.user.id,
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)



