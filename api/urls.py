from django.urls import path
from accounts.views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    ActivateAccountView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)
from rest_framework_simplejwt.views import TokenRefreshView
from courses.views import (
    CourseListView,
    CourseDetailView,
    CourseCreateView,
    LessonListView,
    ModuleListView,
    ModuleDetailView,
    EnrollmentView,
    UserEnrollmentsView,
    EnrollmentCompleteView,
    CourseManageView,
    LessonDetailView,
    AssignmentCreateView,
    LessonAssignmentsView,
    LessonCompleteView,
    MentorCoursesView,
    TestDetailView,
    TestSubmitView,
    ForumThreadView,
    ForumCommentView,
    RatingView,
    ChatRoomView,
    ChatMessageView,
    CourseSearchView,
    RecommendedCoursesView,
)

app_name = 'api'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('activate/<uidb64>/<token>/', ActivateAccountView.as_view(), name='activate'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password-reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),

    # Courses
    path('courses/', CourseListView.as_view(), name='course-list'),
    path('courses/create/', CourseCreateView.as_view(), name='course-create'),
    path('courses/<int:pk>/', CourseDetailView.as_view(), name='course-detail'),
    path('courses/<int:pk>/manage/', CourseManageView.as_view(), name='course-manage'),
    path('courses/my/', MentorCoursesView.as_view(), name='mentor-courses'),
    path('courses/<int:course_id>/modules/', ModuleListView.as_view(), name='module-list'),
    path('modules/<int:pk>/', ModuleDetailView.as_view(), name='module-detail'),
    path('courses/<int:course_id>/lessons/', LessonListView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),
        path('lessons/<int:lesson_id>/complete/', LessonCompleteView.as_view(), name='lesson-complete'),

    # Enrollments
    path('enroll/', EnrollmentView.as_view(), name='enroll'),
    path('my-courses/', UserEnrollmentsView.as_view(), name='user-enrollments'),
    path('enrollments/<int:pk>/complete/', EnrollmentCompleteView.as_view(), name='enrollment-complete'),

    # Assignments
    path('lessons/<int:lesson_id>/assignments/', LessonAssignmentsView.as_view(), name='lesson-assignments'),
    path('assignments/submit/', AssignmentCreateView.as_view(), name='assignment-submit'),

    # Tests
    path('tests/<int:pk>/', TestDetailView.as_view(), name='test-detail'),
    path('tests/<int:test_id>/submit/', TestSubmitView.as_view(), name='test-submit'),

    # Forum
    path('courses/<int:course_id>/threads/', ForumThreadView.as_view(), name='forum-thread'),
    path('threads/<int:thread_id>/comment/', ForumCommentView.as_view(), name='forum-comment'),

    # Ratings
    path('ratings/', RatingView.as_view(), name='rating-create'),

    # Chat
    path('chats/', ChatRoomView.as_view(), name='chatrooms'),
    path('chats/<int:room_id>/messages/', ChatMessageView.as_view(), name='chat-messages'),
    
    # Search and recommendations
    path('search/', CourseSearchView.as_view(), name='course-search'),
    path('recommendations/', RecommendedCoursesView.as_view(), name='course-recommend'),

]
