import datetime
from django.utils import timezone
from iotrec_api.models import Thing, Category, User, Recommendation, Feedback, Preference, Rating, Stay, IotRecSettings
from iotrec_api.permissions import IsSignupOrIsAuthenticated
from iotrec_api.serializers import ThingSerializer, CategorySerializer, CategoryFlatSerializer, \
    RecommendationSerializer, FeedbackSerializer, PreferenceSerializer, RatingSerializer, StaySerializer
from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from iotrec_api.utils import similarity_reference
from iotrec_api.utils.category import calc_items_in_cat_list
from iotrec_api.utils.context import get_time_of_day
from iotrec_api.utils.thing import get_crowdedness
from .serializers import UserSerializer, UserSerializerWithToken


@api_view(['GET', 'PATCH'])
def current_user(request):
    """
    Determine the current user by their token, and return their data
    """

    # a GET request indicates that the user profile was requested
    if request.method == 'GET':
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    # a PATCH request indicates that he user was modified
    elif request.method == 'PATCH':
        serializer = UserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    """
    User API endpoint.
    """
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
        return queryset


class ThingViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows things to be viewed or edited.
    """
    queryset = Thing.objects.all()
    serializer_class = ThingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # calculate similarity references and the number of items in the categories involved
        instance = serializer.instance
        calc_items_in_cat_list(instance.categories.all())
        similarity_reference.calculate_similarity_references_per_thing(instance)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # calculate similarity references and the number of items in the categories involved
        categories_before = set(instance.categories.all())

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        categories_after = set(instance.categories.all())
        calc_items_in_cat_list((categories_before | categories_after))

        similarity_reference.calculate_similarity_references_per_thing(instance)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # get Thing of this request
        instance = self.get_object()

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

        # add an occupation field with the current stay count to the API response
        serializer = self.get_serializer(instance)
        return_data = serializer.data
        return_data['occupation'] = stays.count()
        return Response(return_data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(level=0)
    serializer_class = CategorySerializer


class CategoryFlatViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryFlatSerializer
    # make this endpoint open to the public
    authentication_classes = []
    permission_classes = []


class RecommendationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows recommendations to be viewed or edited.
    """
    serializer_class = RecommendationSerializer

    def get_queryset(self):
        queryset = Recommendation.objects.filter(user=self.request.user)
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

    def get_queryset(self):
        return Preference.objects.filter(user=self.kwargs['user_pk'])


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



