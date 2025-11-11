from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.main_menu, name='main_menu'),
    
    # Футер-страницы
    path('about/', views.about_view, name='about'),
    path('contacts/', views.contact_view, name='contacts'),

    # Страницы видео-курсов (уже работающие)
    path('course/video/', TemplateView.as_view(template_name='video_detail.html'), name='video_detail'),
    path('course/video2/', TemplateView.as_view(template_name='video_detail2.html'), name='video_detail2'),
    path('course/video3/', TemplateView.as_view(template_name='video_detail3.html'), name='video_detail3'),
    


]