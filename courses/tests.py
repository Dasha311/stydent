from django.urls import reverse
from rest_framework.test import APITestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.signals import post_save
from accounts.models import CustomUser
from courses.models import Course, Enrollment, create_course_content


class CourseAPITestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="mentor",
            email="mentor@example.com",
            password="pass",
            role="mentor",
        )
        self.client.force_authenticate(user=self.user)
        post_save.disconnect(create_course_content, sender=Course)

    def tearDown(self):
        post_save.connect(create_course_content, sender=Course)

    def test_create_course(self):
        url = reverse("api:course-create")
        from PIL import Image
        import io
        buf = io.BytesIO()
        Image.new("RGB", (1, 1)).save(buf, format="PNG")
        thumb = SimpleUploadedFile("thumb.png", buf.getvalue(), content_type="image/png")
        text = SimpleUploadedFile("file.txt", b"hello", content_type="text/plain")
        data = {
            "title": "Test Course",
            "description": "Desc",
            "category": "Test",
            "textFile": text,
            "thumbnail": thumb,
        }
        response = self.client.post(url, data, format="multipart")
        if response.status_code != 201:
            print("Creation errors:", response.data)
        self.assertEqual(response.status_code, 201)
        course = Course.objects.get(title="Test Course")
        self.assertEqual(course.description, "Desc")
        self.assertTrue(course.categories.filter(name="Test").exists())
        self.assertTrue(course.thumbnail.name)

        detail_url = reverse("api:course-detail", args=[course.id])
        detail_resp = self.client.get(detail_url)
        self.assertEqual(detail_resp.status_code, 200)
        self.assertIn("thumbnail", detail_resp.data)

    def test_delete_course(self):
        course = Course.objects.create(title="A", instructor=self.user, created_by=self.user)
        url = reverse("api:course-manage", args=[course.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Course.objects.filter(id=course.id).exists())


class EnrollmentAPITestCase(APITestCase):
    def setUp(self):
        post_save.disconnect(create_course_content, sender=Course)
        self.mentor = CustomUser.objects.create_user(
            username="mentor2",
            email="mentor2@example.com",
            password="pass",
            role="mentor",
        )
        self.student = CustomUser.objects.create_user(
            username="student",
            email="student@example.com",
            password="pass",
            role="student",
        )
        self.course = Course.objects.create(title="C", instructor=self.mentor, created_by=self.mentor)
        self.client.force_authenticate(user=self.student)

    def tearDown(self):
        post_save.connect(create_course_content, sender=Course)

    def test_unenroll(self):
        enroll_url = reverse("api:enroll")
        response = self.client.post(enroll_url, {"course_id": self.course.id}, format="json")
        self.assertEqual(response.status_code, 201)
        enrollment_id = response.data["id"]
        profile = self.student.userprofile
        self.assertTrue(profile.courses_enrolled.filter(id=self.course.id).exists())

        delete_url = reverse("api:enrollment-delete", args=[enrollment_id])
        resp = self.client.delete(delete_url)
        self.assertEqual(resp.status_code, 204)
        self.assertFalse(profile.courses_enrolled.filter(id=self.course.id).exists())
        self.assertFalse(Enrollment.objects.filter(id=enrollment_id).exists())