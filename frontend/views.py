from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

User = get_user_model()


# Главное меню
def main_menu(request):
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

        if password1 != password2:
            return render(request, 'Register.html', {'error': 'Пароли не совпадают'})

        if User.objects.filter(username=username).exists():
            return render(request, 'Register.html', {'error': 'Имя пользователя уже занято'})

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        return redirect('select_role')

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


def student_dashboard(request):
    return render(request, 'student_dashboard.html')


def teacher_dashboard(request):
    return render(request, 'teacher_dashboard.html')


def tutors_view(request):
    """Display the tutors catalog for students."""
    return render(request, 'tutors.html')


def course_detail(request, course_id):
    """Dynamic course detail page rendered from localStorage data."""
    return render(request, 'course_detail.html', {'course_id': course_id})


