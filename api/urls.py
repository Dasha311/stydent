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
    EnrollmentView,
    UserEnrollmentsView,
    EnrollmentCompleteView,
    CourseManageView,
    LessonDetailView,
    AssignmentCreateView,
    LessonAssignmentsView,
    TeacherCoursesView,
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
    path('courses/my/', TeacherCoursesView.as_view(), name='teacher-courses'),
    path('courses/<int:course_id>/lessons/', LessonListView.as_view(), name='lesson-list'),
    path('lessons/<int:pk>/', LessonDetailView.as_view(), name='lesson-detail'),

    # Enrollments
    path('enroll/', EnrollmentView.as_view(), name='enroll'),
    path('my-courses/', UserEnrollmentsView.as_view(), name='user-enrollments'),
    path('enrollments/<int:pk>/complete/', EnrollmentCompleteView.as_view(), name='enrollment-complete'),

    # Assignments
    path('lessons/<int:lesson_id>/assignments/', LessonAssignmentsView.as_view(), name='lesson-assignments'),
    path('assignments/submit/', AssignmentCreateView.as_view(), name='assignment-submit'),

]
