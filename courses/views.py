from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg
from accounts.permissions import IsMentor, IsStudent
from accounts.models import CustomUser
from .models import (
    Course,
    Lesson,
    Module,
    Category,
    Enrollment,
    Assignment,
    LessonCompletion,
    Test,
    Question,
    TestAttempt,
    QuestionAttempt,
    ChatRoom,
    ChatMessage,
    ForumThread,
    ForumComment,
    Rating,
)
from .serializers import (
    CourseSerializer,
    LessonSerializer,
    ModuleSerializer,
    CategorySerializer,
    EnrollmentSerializer,
    AssignmentSerializer,
    LessonCompletionSerializer,
    TestSerializer,
    QuestionSerializer,
    TestAttemptSerializer,
    QuestionAttemptSerializer,
    ChatRoomSerializer,
    ChatMessageSerializer,
    ForumThreadSerializer,
    ForumCommentSerializer,
    RatingSerializer,
)
from django_filters.rest_framework import DjangoFilterBackend


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ["title", "description"]
    filterset_fields = ["is_free", "instructor", "categories"]


class CourseCreateView(generics.CreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsMentor]

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user, created_by=self.request.user)


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

class ModuleListView(generics.ListAPIView):
    serializer_class = ModuleSerializer

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        return Module.objects.filter(course_id=course_id).order_by("order")


class ModuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsMentor]

    def update(self, request, *args, **kwargs):
        module = self.get_object()
        if module.course.instructor != request.user:
            raise permissions.PermissionDenied("Not allowed")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        module = self.get_object()
        if module.course.instructor != request.user:
            raise permissions.PermissionDenied("Not allowed")
        return super().destroy(request, *args, **kwargs)


class CourseManageView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsMentor]

    def perform_update(self, serializer):
        course = self.get_object()
        if course.instructor != self.request.user:
            raise permissions.PermissionDenied("Not allowed")
        serializer.save(instructor=self.request.user)

    def destroy(self, request, *args, **kwargs):
        course = self.get_object()
        if course.instructor != request.user:
            raise permissions.PermissionDenied("Not allowed")
        return super().destroy(request, *args, **kwargs)


class LessonListView(generics.ListAPIView):
    serializer_class = LessonSerializer

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        return Lesson.objects.filter(course_id=course_id).order_by("order")


class LessonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsMentor]

    def update(self, request, *args, **kwargs):
        lesson = self.get_object()
        if lesson.course.instructor != request.user:
            raise permissions.PermissionDenied("Not allowed")
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        lesson = self.get_object()
        if lesson.course.instructor != request.user:
            raise permissions.PermissionDenied("Not allowed")
        return super().destroy(request, *args, **kwargs)


class EnrollmentView(generics.CreateAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class EnrollmentCompleteView(generics.UpdateAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def perform_update(self, serializer):
        grade = self.request.data.get("grade")
        serializer.save(completed=True, grade=grade)

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)


class UserEnrollmentsView(generics.ListAPIView):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)


class MentorCoursesView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsMentor]

    def get_queryset(self):
        return Course.objects.filter(instructor=self.request.user)


class AssignmentCreateView(generics.CreateAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class LessonAssignmentsView(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        lesson_id = self.kwargs["lesson_id"]
        return Assignment.objects.filter(lesson_id=lesson_id)


class LessonCompleteView(generics.CreateAPIView):
    serializer_class = LessonCompletionSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def perform_create(self, serializer):
        lesson = get_object_or_404(Lesson, pk=self.kwargs["lesson_id"])
        serializer.save(student=self.request.user, lesson=lesson)


class TestDetailView(generics.RetrieveAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer
    permission_classes = [permissions.IsAuthenticated]


class TestSubmitView(generics.CreateAPIView):
    serializer_class = TestAttemptSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def create(self, request, *args, **kwargs):
        test = get_object_or_404(Test, pk=self.kwargs["test_id"])
        answers = request.data.get("answers", {})
        attempt = TestAttempt.objects.create(test=test, student=request.user)
        correct = 0
        for q in test.questions.all():
            ans = answers.get(str(q.id))
            is_correct = False
            if q.type == Question.SINGLE:
                is_correct = ans == q.correct_answer
            elif q.type == Question.MULTIPLE:
                is_correct = set(ans or []) == set(q.correct_answer)
            else:
                is_correct = str(ans).strip().lower() == str(q.correct_answer).strip().lower()
            if is_correct:
                correct += 1
            QuestionAttempt.objects.create(
                attempt=attempt,
                question=q,
                answer=ans,
                is_correct=is_correct,
                feedback=q.explanation if not is_correct else "",
            )
        attempt.score = 100 * correct / max(1, test.questions.count())
        attempt.save()
        serializer = self.get_serializer(attempt)
        return Response(serializer.data)


class ForumThreadView(generics.ListCreateAPIView):
    serializer_class = ForumThreadSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs["course_id"]
        return ForumThread.objects.filter(course_id=course_id)

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.kwargs["course_id"])
        serializer.save(author=self.request.user, course=course)


class ForumCommentView(generics.CreateAPIView):
    serializer_class = ForumCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        thread = get_object_or_404(ForumThread, pk=self.kwargs["thread_id"])
        parent_id = self.request.data.get("parent")
        parent = None
        if parent_id:
            parent = get_object_or_404(ForumComment, pk=parent_id)
        serializer.save(author=self.request.user, thread=thread, parent=parent)


class RatingView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def perform_create(self, serializer):
        course_id = self.request.data.get("course")
        mentor_id = self.request.data.get("mentor")
        course = Course.objects.filter(id=course_id).first() if course_id else None
        mentor = CustomUser.objects.filter(id=mentor_id).first() if mentor_id else None
        serializer.save(student=self.request.user, course=course, mentor=mentor)


class ChatRoomView(generics.ListCreateAPIView):
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        room = serializer.save()
        room.participants.add(self.request.user)


class ChatMessageView(generics.ListCreateAPIView):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        room = get_object_or_404(ChatRoom, pk=self.kwargs["room_id"], participants=self.request.user)
        return room.messages.all()

    def perform_create(self, serializer):
        room = get_object_or_404(ChatRoom, pk=self.kwargs["room_id"], participants=self.request.user)
        serializer.save(room=room, sender=self.request.user)


class CourseSearchView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        query = self.request.query_params.get("q", "")
        return Course.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))


class RecommendedCoursesView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        completed = user.userprofile.courses_completed.all()
        categories = Category.objects.filter(courses__in=completed).distinct()
        qs = Course.objects.filter(categories__in=categories).exclude(enrollments__student=user).distinct()
        qs = qs.annotate(avg_rating=Avg("rating__score")).order_by("-avg_rating")
        return qs[:10]