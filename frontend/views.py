from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError
from django.db.models import Avg, Q

from courses.models import Course, Enrollment

User = get_user_model()


# Главное меню
def main_menu(request):
    if request.user.is_authenticated:
        if request.user.role == 'teacher':
            return redirect('teacher_dashboard')
        elif request.user.role == 'student':
            return redirect('student_dashboard')
    return render(request, 'MainMenu.html')


# Вход в систему
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if user.role:
                if user.role == 'teacher':
                    return redirect('teacher_dashboard')
                else:
                    return redirect('student_dashboard')
            return redirect('select_role')
        else:
            return render(request, 'Login.html', {'error': 'Неверный логин или пароль'})

    return render(request, 'Login.html')


# Регистрация пользователя
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role')

        if password1 != password2:
            return render(request, 'Register.html', {'error': 'Пароли не совпадают'})

        if User.objects.filter(username=username).exists():
            return render(request, 'Register.html', {'error': 'Имя пользователя уже занято'})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            role=role
        )
        login(request, user)
        # Перенаправляем сразу на дашборд в зависимости от роли
        if role == 'teacher':
            return redirect('teacher_dashboard')
        return redirect('student_dashboard')

    return render(request, 'Register.html')


# Страница курса
def course_view(request):
    return render(request, 'CourseView.html')  # исправлено название шаблона


# Статические страницы футера
def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    return render(request, 'contact.html')

def terms_view(request):
    return render(request, 'terms.html')


# Страница выбора роли
def select_role(request):
    if request.method == 'POST':
        role = request.POST.get('role')
        if role in ['student', 'teacher']:
            request.user.role = role
            request.user.save()
            if role == 'student':
                return redirect('student_dashboard')
            else:
                return redirect('teacher_dashboard')
    return render(request, 'select_role.html')


@login_required
def student_dashboard(request):
    if request.user.role == 'teacher':
        return redirect('teacher_dashboard')
    return render(request, 'student_dashboard.html')


@login_required
def teacher_dashboard(request):
    if request.user.role == 'student':
        return redirect('student_dashboard')
    active_courses = Course.objects.filter(instructor=request.user).count()
    student_count = (
        User.objects.filter(
            enrollments__course__instructor=request.user,
            role='student',
        )
        .distinct()
        .count()
    )
    context = {
        'active_courses': active_courses,
        'student_count': student_count,
    }
    return render(request, 'teacher_dashboard.html', context)


def tutors_view(request):
    """Display the tutors catalog with search and sorting options."""
    q = request.GET.get('q', '')
    sort = request.GET.get('sort', 'name')

    teachers = User.objects.filter(role='teacher')

    if q:
        teachers = teachers.filter(
            Q(username__icontains=q)
            | Q(first_name__icontains=q)
            | Q(last_name__icontains=q)
        )

    teachers = teachers.annotate(avg_rating=Avg('mentor_ratings__score'))

    if sort == 'rating':
        teachers = teachers.order_by('-avg_rating', 'username')
    else:
        teachers = teachers.order_by('username')

    return render(
        request,
        'tutors.html',
        {
            'teachers': teachers,
            'q': q,
            'sort': sort,
        },
    )


def teacher_profile_view(request, teacher_id):
    """Public profile page of a teacher."""
    teacher = get_object_or_404(User, id=teacher_id, role='teacher')
    courses = teacher.courses_taught.all()
    avg_rating = teacher.mentor_ratings.aggregate(avg=Avg('score'))['avg']
    return render(
        request,
        'teacher_profile.html',
        {
            'teacher': teacher,
            'courses': courses,
            'avg_rating': avg_rating,
        },
    )


def course_detail(request, course_id):
    """Dynamic course detail page rendered from localStorage data."""
    return render(request, 'course_detail.html', {'course_id': course_id})


@login_required
def profile(request):
    """Unified profile page for both students and teachers."""
    return render(request, 'profile.html')



@login_required
def delete_account(request):
    """Delete the current user account after password confirmation."""
    if request.method == 'POST':
        password = request.POST.get('password')
        password = request.POST.get('password')
        if request.user.check_password(password):
            try:
                request.user.delete()
                logout(request)
            except OperationalError:
                return render(
                    request,
                    'delete_account.html',
                    {'error': 'Ошибка базы данных. Попробуйте позже.'},
                )
            return redirect('main_menu')
        return render(request, 'delete_account.html', {
            'error': 'Неверный пароль'
        })
    return render(request, 'delete_account.html')


def messages_view(request):
    """Simple chat page from profile."""
    return render(request, 'message.html')
