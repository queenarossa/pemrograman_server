
from django.test import TestCase
from django.db import IntegrityError, transaction

from catalog.models import Course, Lesson
from users.models import User


class CourseTestCase(TestCase):
    def setUp(self):
        self.lecturer = User.objects.create_user(
            username="testlecturer",
            password="test12345",
            role="LECTURER",
        )

    def test_course_created(self):
        course = Course.objects.create(
            code="TEST01",
            title="Test Course",
            lecturer=self.lecturer,
        )
        self.assertEqual(course.code, "TEST01")

    def test_course_code_unique(self):
        Course.objects.create(
            code="TEST01",
            title="Course Pertama",
            lecturer=self.lecturer,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Course.objects.create(
                    code="TEST01",
                    title="Course Kedua",
                    lecturer=self.lecturer,
                )

    def test_lesson_relationship(self):
        course = Course.objects.create(
            code="TEST02",
            title="Course Django",
            lecturer=self.lecturer,
        )

        lesson = Lesson.objects.create(
            course=course,
            title="Pengenalan Django",
            content="Materi pengenalan Django",
            order=1,
        )

        self.assertEqual(lesson.course, course)
        self.assertEqual(course.lessons.count(), 1)