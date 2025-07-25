from django.contrib import admin
from .models import (
    Course,
    Lesson,
    Module,
    Category,
    Enrollment,
    Assignment,
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

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1

class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline]
    list_display = ('title', 'instructor', 'duration', 'is_free', 'created_at')
    list_filter = ('is_free', 'created_at')
    search_fields = ('title', 'description', 'instructor__username')

admin.site.register(Course, CourseAdmin)
admin.site.register(Enrollment)
admin.site.register(Assignment)
admin.site.register(Module)
admin.site.register(Category)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(TestAttempt)
admin.site.register(QuestionAttempt)
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)
admin.site.register(ForumThread)
admin.site.register(ForumComment)
admin.site.register(Rating)