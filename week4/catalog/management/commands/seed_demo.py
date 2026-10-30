
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from catalog.models import Course, Lesson, Assignment, Submission
from users.models import User


class Command(BaseCommand):
    help = "Membuat sample data Course, Lesson, Assignment, dan Submission"

    def handle(self, *args, **options):
        lecturer = User.objects.get(username="suprayogi")
        student = User.objects.get(username="Fauzan Arif")

        course, created = Course.objects.get_or_create(
            code="PSS01",
            defaults={
                "title": "Pemrograman Sisi Server",
                "description": "Belajar backend development dengan Django.",
                "lecturer": lecturer,
            },
        )

        lessons = [
            "Pengenalan Backend",
            "Pola Arsitektur Backend",
            "Containerisasi dengan Docker",
        ]

        for order, title in enumerate(lessons, start=1):
            Lesson.objects.get_or_create(
                course=course,
                order=order,
                defaults={"title": title, "content": title},
            )

        assignment1, _ = Assignment.objects.get_or_create(
            course=course,
            title="Tugas Django ORM",
            defaults={
                "description": "Implementasikan model dan relationship menggunakan Django ORM.",
                "deadline": timezone.now() + timedelta(days=7),
            },
        )

        assignment2, _ = Assignment.objects.get_or_create(
            course=course,
            title="Tugas REST API",
            defaults={
                "description": "Buat REST API sederhana menggunakan Django.",
                "deadline": timezone.now() + timedelta(days=14),
            },
        )

        Submission.objects.get_or_create(
            assignment=assignment1,
            student=student,
            defaults={
                "content": "Saya telah menyelesaikan implementasi Django ORM.",
                "grade": 87.5,
            },
        )

        Submission.objects.get_or_create(
            assignment=assignment2,
            student=student,
            defaults={
                "content": "Saya telah menyelesaikan REST API menggunakan Django.",
                "grade": 90.0,
            },
        )

        self.stdout.write(
            self.style.SUCCESS("Sample data berhasil dibuat.")
        )