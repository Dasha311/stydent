from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from frontend import views as frontend_views


urlpatterns = [
    path('admin/', admin.site.urls),

    # Страницы сайта (frontend)
    path('', frontend_views.main_menu, name='main_menu'),
    path('login/', frontend_views.login_view, name='login'),
    path('register/', frontend_views.register, name='register'),
    path('logout/', auth_views.LogoutView.as_view(next_page='main_menu'), name='logout'),
    path('delete-account/', frontend_views.delete_account, name='delete_account'),
    path('select-role/', frontend_views.select_role, name='select_role'),
    path('student/dashboard/', frontend_views.student_dashboard, name='student_dashboard'),
    path('teacher/dashboard/', frontend_views.teacher_dashboard, name='teacher_dashboard'),
    path('tutors/', frontend_views.tutors_view, name='tutors'),
    path('tutors/<int:teacher_id>/', frontend_views.teacher_profile_view, name='teacher_profile'),
    path('course/', frontend_views.course_view, name='course_view'),
    path('profile/', frontend_views.profile, name='profile'),
    path('messages/', frontend_views.messages_view, name='messages'),
    path('about/', frontend_views.about_view, name='about'),
    path('contacts/', frontend_views.contact_view, name='contacts'),
    path('terms/', frontend_views.terms_view, name='terms'),
    path('course/<int:course_id>/', frontend_views.course_detail, name='course_detail'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Видео-страницы
    path('course/video/', TemplateView.as_view(template_name='video_detail.html'), name='video_detail'),
    path('course/video2/', TemplateView.as_view(template_name='video_detail2.html'), name='video_detail2'),
    path('course/video3/', TemplateView.as_view(template_name='video_detail3.html'), name='video_detail3'),

    # API
    path('api/', include('api.urls', namespace='api')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])