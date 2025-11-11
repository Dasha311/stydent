from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model

from courses.models import Course, Category

User = get_user_model()


# Главное меню

def main_menu(request):
    courses = Course.objects.order_by('created_at')[:3]
    return render(request, 'MainMenu.html', {'courses': courses})


# Вход в систему

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('main_menu')
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
            role=role,
        )
        login(request, user)
        return redirect('main_menu')

    return render(request, 'Register.html')


# Страница курсов каталога

def course_view(request):
    category_id = request.GET.get('category')
    courses = Course.objects.all()
    if category_id:
        courses = courses.filter(categories__id=category_id)
    categories = (
        Category.objects.filter(courses__isnull=False)
        .distinct()
        .order_by('name')
    )
    context = {
        'courses': courses,
        'categories': categories,
        'selected_category': int(category_id) if category_id else None,
    }
    return render(request, 'CourseView.html', context)


# Статические страницы

def about_view(request):
    return render(request, 'about.html')


def contact_view(request):
    return render(request, 'contact.html')


# Динамическая страница курса

def course_detail(request, course_id):
    """Dynamic course detail page rendered from localStorage data."""
    return render(request, 'course_detail.html', {'course_id': course_id})