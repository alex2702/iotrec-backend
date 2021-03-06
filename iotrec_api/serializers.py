from django.utils import timezone
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from evaluation.serializers import ExperimentSerializer
from iotrec_api.models import User, Thing, Category, Recommendation, Feedback, Preference, Rating, Stay, Context


class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    # preferences and experiments are part of user object, so the API has to (de)serialize them
    preferences = PreferenceSerializer(many=True)
    experiments = ExperimentSerializer(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'preferences', 'experiments')


class UserSerializerWithToken(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)
    preferences = PreferenceSerializer(many=True, required=False)
    experiments = ExperimentSerializer(many=True, required=False)

    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.save()

        preferences = validated_data.get('preferences', instance.preferences)

        for preference in preferences:
            category = preference.get('category', None)
            preference_id = category.text_id
            if preference_id:
                preference_item = Preference.objects.get(id=preference_id, user=instance)
                preference_item.updated_at = timezone.now()
                preference_item.value = preference.get('value', preference_item.value)
                preference_item.save()

        return instance

    class Meta:
        model = User
        fields = ('id', 'token', 'username', 'email', 'password', 'preferences', 'experiments')


class ThingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thing
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('text_id', 'name')

    def get_fields(self):
        fields = super(CategorySerializer, self).get_fields()
        fields['children'] = CategorySerializer(many=True)
        return fields


class CategoryFlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('text_id', 'name', 'parent', 'level')

    def to_representation(self, instance):
        string_fields = {'text_id', 'name', 'parent'}
        data = super().to_representation(instance)
        for field in string_fields:
            try:
                if not data[field]:
                    data[field] = ""
            except KeyError:
                pass
        return data


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = '__all__'


class StaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Stay
        fields = '__all__'


class ContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Context
        fields = '__all__'


class RecommendationSerializer(serializers.ModelSerializer):
    context = ContextSerializer(many=False)

    def create(self, validated_data):
        context_data = validated_data.pop('context')
        # create a context object from submitted raw fields
        context = Context.objects.create(
            weather_raw=context_data['weather_raw'],
            temperature_raw=context_data['temperature_raw'],
            length_of_trip_raw=context_data['length_of_trip_raw'],
            crowdedness_raw=context_data['crowdedness_raw'],
            time_of_day_raw=context_data['time_of_day_raw']
        )
        instance = self.Meta.model(**validated_data)
        instance.context = context
        instance.save()
        return instance

    class Meta:
        model = Recommendation
        fields = '__all__'


