from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser, UserProfile
import os
from .utils import generate_course_topics


class Category(models.Model):
    """Simple tag for grouping courses."""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='courses_taught')
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='created_courses',
        null=True,
        blank=True,
    )
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    duration = models.DurationField()  # in minutes
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_free = models.BooleanField(default=False)
    categories = models.ManyToManyField('Category', related_name='courses', blank=True)
    
    def __str__(self):
        return self.title

class Module(models.Model):
    """A module groups lessons inside a course."""

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    prerequisites = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='unlocks')

    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        return f"{self.course.title} - {self.title}"    

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons', null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    duration = models.DurationField()  # in minutes
    order = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class Enrollment(models.Model):
    """Represents a student's participation in a course."""

    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="enrollments",
        null=True,
        blank=True,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    progress = models.PositiveIntegerField(default=0)
    grade = models.PositiveIntegerField(null=True, blank=True)
    certificate_issued = models.BooleanField(default=False)

    class Meta:
        unique_together = ("student", "course")

    def __str__(self):
        return f"{self.student.username if self.student else 'Unknown student'} enrolled in {self.course.title}"

    def update_progress(self):
        total = self.course.lessons.count()
        completed = LessonCompletion.objects.filter(
            student=self.student,
            lesson__course=self.course,
        ).count()
        self.progress = int(100 * completed / total) if total else 0
        fields = ["progress"]
        if self.progress == 100 and not self.certificate_issued:
            self.certificate_issued = True
            fields.append("certificate_issued")
            profile, _ = UserProfile.objects.get_or_create(user=self.student)
            profile.courses_completed.add(self.course)
        self.save(update_fields=fields)


class LessonCompletion(models.Model):
    """Marks a lesson as completed by a student."""

    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("lesson", "student")


@receiver(post_save, sender=LessonCompletion)
def update_enrollment_progress(sender, instance, created, **kwargs):
    if not created:
        return
    try:
        enrollment = Enrollment.objects.get(student=instance.student, course=instance.lesson.course)
    except Enrollment.DoesNotExist:
        return
    enrollment.update_progress()

class Assignment(models.Model):
    """Homework submitted by a student for a lesson."""

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="assignments")
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    file = models.FileField(upload_to="assignments/", blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False)
    passed = models.BooleanField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # If a file was uploaded and text is empty, try to extract text from the file
        if self.file and not self.text:
            ext = os.path.splitext(self.file.name)[1].lower()
            try:
                if ext == ".docx":
                    from docx import Document

                    doc = Document(self.file)
                    self.text = "\n".join(p.text for p in doc.paragraphs)
                elif ext in {".txt"}:
                    self.text = self.file.read().decode("utf-8")
            except Exception:
                pass
            finally:
                if hasattr(self.file, "seek"):
                    self.file.seek(0)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Assignment for {self.lesson} by {self.student}"

class Test(models.Model):
    """A simple test associated with a course."""

    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name="test")
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title

class Question(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=255)
    correct_answer = models.CharField(max_length=255)

    def __str__(self):
        return self.text

@receiver(post_save, sender=Course)
def create_course_content(sender, instance, created, **kwargs):
    """Create default lessons and a test when a course is created."""
    if created:
        Test.objects.create(course=instance, title=f"Test for {instance.title}")
        topics = generate_course_topics(instance.title)
        for i, topic in enumerate(topics, 1):
            Lesson.objects.create(
                course=instance,
                title=topic,
                order=i,
                duration=0,
            )
