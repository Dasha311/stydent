from rest_framework import serializers
from .models import CustomUser, UserProfile
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    badges = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name'
    )
        
    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'password',
            'first_name', 'last_name', 'role',
            'profile_picture', 'bio',
            'level', 'xp', 'badges'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'profile_picture': {'required': False, 'allow_null': True},
            'bio': {'required': False}
        }

    def validate_password(self, value):
        import re
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long.')
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError('Password must contain at least one uppercase letter.')
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError('Password must contain at least one digit.')
        if not any(not c.isalnum() for c in value):
            raise serializers.ValidationError('Password must contain at least one special character.')
        try:
            value.encode('ascii')
        except UnicodeEncodeError:
            raise serializers.ValidationError('Password must contain only Latin characters.')
        return value

    def create(self, validated_data):
        return CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=validated_data.get('role'),
            profile_picture=validated_data.get('profile_picture'),
            bio=validated_data.get('bio', ''),
            is_active=validated_data.get('is_active', True),
            verification_code=validated_data.get('verification_code', '')
        )

class LoginSerializer(TokenObtainPairSerializer):
    username_field = CustomUser.USERNAME_FIELD


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    username = serializers.CharField(source='user.username', required=False)
    profile_picture = serializers.ImageField(write_only=True, required=False, allow_null=True)
    bio = serializers.CharField(write_only=True, required=False, allow_blank=True)
    courses_enrolled = serializers.SerializerMethodField()
    courses_completed = serializers.SerializerMethodField()
    courses_taught = serializers.SerializerMethodField()
    course_progress = serializers.SerializerMethodField()
    level = serializers.IntegerField(source='user.level', read_only=True)
    xp = serializers.IntegerField(source='user.xp', read_only=True)
    badges = serializers.SlugRelatedField(
        source='user.badges', many=True, read_only=True, slug_field='name'
    )
    certificates = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'user',
            'username',
            'profile_picture',
            'bio',
            'courses_enrolled',
            'courses_completed',
            'courses_taught',
            'course_progress',
            'certificates',
            'level',
            'xp',
            'badges',
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

    def get_course_progress(self, obj):
        progress = {}
        for enrollment in obj.user.enrollments.select_related('course'):
            progress[enrollment.course.id] = enrollment.progress
        return progress
    
    def get_certificates(self, obj):
        return [
            {
                'course_id': e.course.id,
                'course_title': e.course.title,
            }
            for e in obj.user.enrollments.filter(certificate_issued=True)
        ]

    def update(self, instance, validated_data):
        profile_picture = validated_data.pop('profile_picture', None)
        bio = validated_data.pop('bio', None)
        username = validated_data.pop('username', None)
        user = instance.user
        if profile_picture is not None:
            user.profile_picture = profile_picture
        if bio is not None:
            user.bio = bio
        if username is not None:
            user.username = username
        user.save()
        return super().update(instance, validated_data)