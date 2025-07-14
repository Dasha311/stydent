from rest_framework import serializers
from .models import (
    Course,
    Lesson,
    Module,
    Category,
    Enrollment,
    Assignment,
    Test,
    Question,
    TestAttempt,
    QuestionAttempt,
    ChatRoom,
    ChatMessage,
    ForumThread,
    ForumComment,
    Rating,
    LessonCompletion,
)
from accounts.serializers import UserSerializer

class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    duration = serializers.DurationField(required=False)
    thumbnail = serializers.ImageField(required=False, allow_null=True)
    textFile = serializers.FileField(source="text_file", required=False, allow_null=True)
    test = serializers.JSONField(source="test_data", required=False, allow_null=True)

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'instructor',
            'created_by',
            'thumbnail',
            'duration',
            'created_at',
            'updated_at',
            'price',
            'is_free',
            'categories',
            'videos',
            'textFile',
            'assignment',
            'test',
            'average_rating',
        ]
        read_only_fields = ['average_rating']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = '__all__'


class LessonCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonCompletion
        fields = '__all__'

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'

class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), source="course", write_only=True
    )
    
    class Meta:
        model = Enrollment
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Test
        fields = '__all__'


class AssignmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = '__all__'


class QuestionAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionAttempt
        fields = '__all__'


class TestAttemptSerializer(serializers.ModelSerializer):
    question_attempts = QuestionAttemptSerializer(many=True, read_only=True)

    class Meta:
        model = TestAttempt
        fields = '__all__'


class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = ChatMessage
        fields = '__all__'


class ChatRoomSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = ChatMessageSerializer(many=True, read_only=True)
    course = CourseSerializer(read_only=True)    

    class Meta:
        model = ChatRoom
        fields = '__all__'


class ForumCommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ForumComment
        fields = '__all__'

    def get_replies(self, obj):
        return ForumCommentSerializer(obj.replies.all(), many=True).data


class ForumThreadSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments = ForumCommentSerializer(many=True, read_only=True)

    class Meta:
        model = ForumThread
        fields = '__all__'


class RatingSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    mentor = UserSerializer(read_only=True)

    class Meta:
        model = Rating
        fields = '__all__'