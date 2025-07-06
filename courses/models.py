from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser
import os
from .utils import generate_course_topics

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
    
    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
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

    class Meta:
        unique_together = ("student", "course")
    
    def __str__(self):
        return f"{self.student.username if self.student else 'Unknown student'} enrolled in {self.course.title}"

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
