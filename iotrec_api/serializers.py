from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from iotrec_api.models import User, Thing, Category, Recommendation, Feedback, Preference


# from django.contrib.auth.models import User

'''
class PreferenceRelatedField(serializers.RelatedField):
    def to_representation(self, obj):
        return {
            'id': obj.pk,
            'category': obj.category,
            'value': obj.value,
        }
'''


class PreferenceSerializer(serializers.ModelSerializer):
    #user = serializers.IntegerField(read_only=True)
    #user = UserSerializer()
    #user = UserSerializer(source='user', read_only=True)

    #def create(self, validated_data):
    #    validated_data['user'] = User.objects.get('user')
    #    return Preference.objects.create(**validated_data)

    class Meta:
        model = Preference
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    preferences = PreferenceSerializer(many=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'preferences')

    #def update(self, instance, validated_data):
    #    instance.email = validated_data.get('email', instance.email)
    #    instance.preferences = validated_data.get('preferences', instance.preferences)


class UserSerializerWithToken(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)
    preferences = PreferenceSerializer(many=True, required=False)

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

    class Meta:
        model = User
        fields = ('token', 'username', 'email', 'password', 'preferences')


"""
class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'
"""


class ThingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thing
        # fields = ('title', 'description', 'image')
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    #children = CategorySerializer(many=True)

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


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = '__all__'


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'





