from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.main_menu, name='main_menu'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('select-role/', views.select_role, name='select_role'),
    path('course/', views.course_view, name='course_view'),

    # Футер-страницы
    path('about/', views.about_view, name='about'),
    path('contacts/', views.contact_view, name='contacts'),
    path('terms/', views.terms_view, name='terms'),

    # Страница видео-курса
    path('course/video/', TemplateView.as_view(template_name='video_detail.html'), name='video_detail'),
    path('course/video2/', TemplateView.as_view(template_name='video_detail2.html'), name='video_detail2'),
    path('course/video3/', TemplateView.as_view(template_name='video_detail3.html'), name='video_detail3'),
]

