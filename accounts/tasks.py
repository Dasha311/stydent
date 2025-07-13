from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse


@shared_task
def send_email(subject, message, recipient_list):
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=True)


@shared_task
def send_verification_code_email(email, code):
    subject = 'Email Verification'
    link = f"{settings.DEFAULT_DOMAIN}{reverse('api:verify-code')}?email={email}&code={code}"
    message = f'Your verification code is {code}.\nActivate your account: {link}'
    send_email(subject, message, [email])


@shared_task
def send_new_message_email(email, sender_name, text):
    subject = 'Новое сообщение от наставника'
    message = f'{sender_name}: {text}'
    send_email(subject, message, [email])


@shared_task
def send_module_reminder_email(email, course_title):
    subject = 'Напоминание о незавершенном модуле'
    message = f'Вы забыли закончить модуль в курсе "{course_title}"'
    send_email(subject, message, [email])


@shared_task
def send_new_course_invitation(email, course_title):
    subject = 'Новый курс для вас'
    message = f'Приглашаем пройти курс "{course_title}"'
    send_email(subject, message, [email])


@shared_task
def send_module_reminders():
    from courses.models import Enrollment
    from django.utils import timezone
    from datetime import timedelta

    threshold = timezone.now() - timedelta(days=7)
    enrollments = Enrollment.objects.filter(progress__lt=100)
    for enrollment in enrollments:
        if enrollment.student.email and enrollment.course.created_at < threshold:
            send_module_reminder_email.delay(enrollment.student.email, enrollment.course.title)