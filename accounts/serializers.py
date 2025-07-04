from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import CustomUser, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'password',
            'first_name', 'last_name', 'role',
            'profile_picture', 'bio'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'profile_picture': {'required': False, 'allow_null': True},
            'bio': {'required': False}
        }

    def create(self, validated_data):
        return CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role'),
            profile_picture=validated_data.get('profile_picture'),
            bio=validated_data.get('bio', '')
        )

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect credentials")


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    profile_picture = serializers.ImageField(write_only=True, required=False, allow_null=True)
    bio = serializers.CharField(write_only=True, required=False, allow_blank=True)
    courses_enrolled = serializers.SerializerMethodField()
    courses_completed = serializers.SerializerMethodField()
    courses_taught = serializers.SerializerMethodField()

    
    class Meta:
        model = UserProfile
        fields = [
            'user', 'profile_picture', 'bio',
            'courses_enrolled', 'courses_completed',
            'courses_taught'
        ]

    def get_courses_enrolled(self, obj):
        from courses.serializers import CourseSerializer
        return CourseSerializer(obj.courses_enrolled.all(), many=True).data

    def get_courses_completed(self, obj):
        from courses.serializers import CourseSerializer
        return CourseSerializer(obj.courses_completed.all(), many=True).data

    def get_courses_taught(self, obj):
        from courses.serializers import CourseSerializer
        return CourseSerializer(obj.user.courses_taught.all(), many=True).data

    def update(self, instance, validated_data):
        profile_picture = validated_data.pop('profile_picture', None)
        bio = validated_data.pop('bio', None)
        user = instance.user
        if profile_picture is not None:
            user.profile_picture = profile_picture
        if bio is not None:
            user.bio = bio
        user.save()
        return super().update(instance, validated_data)