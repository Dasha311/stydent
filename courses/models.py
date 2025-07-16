from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from accounts.models import CustomUser, UserProfile
import datetime
from accounts.tasks import (
    send_new_message_email,
    send_module_reminder_email,
    send_new_course_invitation,
)
import os
from .utils import generate_course_topics


class Category(models.Model):
    """Simple tag for grouping courses."""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='courses_taught')
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='created_courses',
        null=True,
        blank=True,
    )
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    duration = models.DurationField(default=datetime.timedelta())     
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_free = models.BooleanField(default=False)
    categories = models.ManyToManyField('Category', related_name='courses', blank=True)
    videos = models.JSONField(default=list, blank=True)
    text_file = models.FileField(upload_to='course_files/', blank=True, null=True)
    assignment = models.TextField(blank=True)
    test_data = models.JSONField(blank=True, null=True)
    

    @property
    def average_rating(self):
        from django.db.models import Avg
        return self.rating_set.aggregate(avg=Avg("score")).get("avg") or 0    
    
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
        lessons_total = self.course.lessons.count()
        lessons_completed = LessonCompletion.objects.filter(
            student=self.student,
            lesson__course=self.course,
        ).count()

        assignments_passed = Assignment.objects.filter(
            lesson__course=self.course,
            student=self.student,
            grade__gte=50,
        ).count()

        test_required = 1 if Test.objects.filter(course=self.course).exists() else 0
        test_completed = 0
        if test_required:
            attempt = (
                TestAttempt.objects.filter(test__course=self.course, student=self.student)
                .order_by("-score")
                .first()
            )
            if attempt and attempt.score >= 50:
                test_completed = 1

        total_items = lessons_total + lessons_total + test_required
        completed_items = lessons_completed + assignments_passed + test_completed
        self.progress = int(100 * completed_items / total_items) if total_items else 0
        fields = ["progress"]
        if self.progress == 100 and not self.certificate_issued:
            self.certificate_issued = True
            fields.append("certificate_issued")
            profile, _ = UserProfile.objects.get_or_create(user=self.student)
            profile.courses_completed.add(self.course)
            from accounts.models import Badge
            badge, _ = Badge.objects.get_or_create(
                name="Course Completed",
                defaults={"description": "Completed a course"},
            )
            self.student.badges.add(badge)
            instructor = self.course.instructor
            instructor.level = instructor.level + 20
            instructor.save(update_fields=["level"])            
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
    student = instance.student
    student.xp += 10
    if student.xp >= 100:
        student.level += student.xp // 100
        student.xp = student.xp % 100
    student.save(update_fields=["xp", "level"])

class Assignment(models.Model):
    """Homework submitted by a student for a lesson."""

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="assignments")
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    file = models.FileField(upload_to="assignments/", blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    checked = models.BooleanField(default=False)
    passed = models.BooleanField(null=True, blank=True)
    grade = models.PositiveIntegerField(null=True, blank=True)

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

        if self.grade is not None:
            self.checked = True
            self.passed = self.grade >= 50

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
    SINGLE = "single"
    MULTIPLE = "multiple"
    TEXT = "text"
    QUESTION_TYPES = [
        (SINGLE, "Single Choice"),
        (MULTIPLE, "Multiple Choice"),
        (TEXT, "Text"),
    ]

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="questions")
    text = models.CharField(max_length=255)
    type = models.CharField(max_length=10, choices=QUESTION_TYPES, default=SINGLE)
    choices = models.JSONField(blank=True, null=True)
    correct_answer = models.JSONField()
    explanation = models.TextField(blank=True)

    def __str__(self):
        return self.text

class TestAttempt(models.Model):
    """Stores a student's attempt for a test."""

    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    score = models.FloatField(default=0)
    completed_at = models.DateTimeField(auto_now_add=True)


class QuestionAttempt(models.Model):
    """Stores answer for a single question inside a test attempt."""

    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name="question_attempts")
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.JSONField()
    is_correct = models.BooleanField()
    feedback = models.TextField(blank=True)


class ChatRoom(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="chatrooms",
        null=True,
        blank=True,
    )
    participants = models.ManyToManyField(CustomUser, related_name="chatrooms")
    created_at = models.DateTimeField(auto_now_add=True)


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=ChatMessage)
def notify_new_message(sender, instance, created, **kwargs):
    if not created:
        return
    participants = instance.room.participants.exclude(id=instance.sender_id)
    for user in participants:
        if user.email:
            send_new_message_email.delay(user.email, instance.sender.username, instance.text)


class ForumThread(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="threads")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ForumComment(models.Model):
    thread = models.ForeignKey(ForumThread, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Rating(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    mentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name="mentor_ratings")
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="given_ratings")
    score = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
                # DurationField expects a timedelta value
                duration=datetime.timedelta(),
            )
        for user in CustomUser.objects.filter(role='student'):
            if not user.email:
                continue
            try:
                send_new_course_invitation.delay(user.email, instance.title)
            except Exception:
                send_new_course_invitation(user.email, instance.title)


@receiver(post_save, sender=Assignment)
def handle_assignment_save(sender, instance, created, **kwargs):
    """Notify instructor on new submission and update progress after grading."""
    try:
        enrollment = Enrollment.objects.get(student=instance.student, course=instance.lesson.course)
    except Enrollment.DoesNotExist:
        enrollment = None

    if created:
        room = (
            ChatRoom.objects.filter(course=instance.lesson.course, participants=instance.student)
            .filter(participants=instance.lesson.course.instructor)
            .first()
        )
        if not room:
            room = ChatRoom.objects.create(course=instance.lesson.course)
            room.participants.add(instance.student, instance.lesson.course.instructor)
        ChatMessage.objects.create(
            room=room,
            sender=instance.student,
            text="Прикреплено новое задание.",
        )
    elif instance.grade is not None and enrollment:
        enrollment.update_progress()


@receiver(post_save, sender=TestAttempt)
def update_progress_from_test(sender, instance, created, **kwargs):
    if not created:
        return
    try:
        enrollment = Enrollment.objects.get(student=instance.student, course=instance.test.course)
    except Enrollment.DoesNotExist:
        return
    enrollment.update_progress()