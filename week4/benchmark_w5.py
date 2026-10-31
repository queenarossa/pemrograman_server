"""
Benchmark Minggu 5 (BEFORE vs AFTER) untuk Simple LMS.

Jalankan dari folder yang berisi manage.py:

    docker compose exec app python manage.py shell -c "exec(open('benchmark_w5.py').read())"

Setiap skenario dijalankan 1x pemanasan, lalu 5x pengukuran.
Waktu yang dilaporkan adalah median dari 5x pengukuran.
Angka yang tampil adalah hasil di komputermu sendiri.
"""
import statistics
import time

from django.db import connection
from django.db.models import Count
from django.test.utils import CaptureQueriesContext

from catalog.models import Assignment, Course, Enrollment, Lesson, Submission
from users.models import User


def measure(fn, repeat=5):
    fn()  # pemanasan (cache koneksi/plan), tidak dihitung
    times = []
    queries = 0
    for _ in range(repeat):
        with CaptureQueriesContext(connection) as ctx:
            start = time.perf_counter()
            fn()
            times.append(time.perf_counter() - start)
        queries = len(ctx.captured_queries)
    return queries, statistics.median(times)


perf = Course.objects.filter(code__startswith="PERF").order_by("code")


# --- Course + Lecturer (N+1 ForeignKey) ---------------------------------
def lecturer_before():
    return [(c.title, c.lecturer.username) for c in perf[:100]]


def lecturer_after():
    return [(c.title, c.lecturer.username)
            for c in perf.select_related("lecturer")[:100]]


# --- Course + Lesson (N+1 reverse FK) -----------------------------------
def lesson_before():
    for c in perf[:50]:
        [lesson.title for lesson in c.lessons.all()]


def lesson_after():
    for c in perf.prefetch_related("lessons")[:50]:
        [lesson.title for lesson in c.lessons.all()]


# --- Teknik lain (Lab D) ------------------------------------------------
course1 = Course.objects.get(code="PERF00001")


def enrolled_list():       # ambil semua objek lalu cek isinya
    return len(list(Enrollment.objects.filter(course=course1))) > 0


def enrolled_exists():     # hanya tanya ada/tidak
    return Enrollment.objects.filter(course=course1).exists()


def count_python():        # ambil semua objek, hitung di Python
    return len(list(Course.objects.filter(code__startswith="PERF")))


def count_db():            # database yang menghitung
    return Course.objects.filter(code__startswith="PERF").count()


def full_objects():        # semua kolom
    return list(perf[:1000])


def only_columns():        # hanya 2 kolom
    return list(perf.values("code", "title")[:1000])


def enrollments_loop():    # N+1: hitung enrollment per course di loop
    return [(c.code, c.enrollments.count()) for c in perf[:100]]


def enrollments_annotate():  # 1 query dengan annotate
    return [(c.code, c.n) for c in perf.annotate(n=Count("enrollments"))[:100]]


scenarios = [
    ("Course + Lecturer (100)", "BEFORE: query biasa", lecturer_before,
     "AFTER : select_related()", lecturer_after),
    ("Course + Lesson (50)", "BEFORE: query biasa", lesson_before,
     "AFTER : prefetch_related()", lesson_after),
    ("Cek ada enrollment", "BEFORE: list() semua objek", enrolled_list,
     "AFTER : exists()", enrolled_exists),
    ("Hitung Course PERF", "BEFORE: len(list(...))", count_python,
     "AFTER : count()", count_db),
    ("Ambil 1000 Course", "BEFORE: semua kolom", full_objects,
     "AFTER : values('code','title')", only_columns),
    ("Enrollment per Course (100)", "BEFORE: count() di loop", enrollments_loop,
     "AFTER : annotate(Count)", enrollments_annotate),
]

print("=" * 72)
print("DATA PENGUJIAN")
print("=" * 72)
print("User       :", User.objects.count(),
      "(lecturer:", User.objects.filter(role="LECTURER").count(),
      "| student:", User.objects.filter(role="STUDENT").count(), ")")
print("Course     :", Course.objects.count())
print("Lesson     :", Lesson.objects.count())
print("Enrollment :", Enrollment.objects.count())
print("Assignment :", Assignment.objects.count())
print("Submission :", Submission.objects.count())

print()
print("=" * 72)
print("HASIL BENCHMARK")
print("=" * 72)
for name, label_b, fn_b, label_a, fn_a in scenarios:
    qb, tb = measure(fn_b)
    qa, ta = measure(fn_a)
    gain = (tb - ta) / tb * 100 if tb else 0
    print(f"\n{name}")
    print(f"  {label_b:<30} {qb:>4} query  {tb * 1000:8.2f} ms")
    print(f"  {label_a:<30} {qa:>4} query  {ta * 1000:8.2f} ms")
    print(f"  Improvement waktu: {gain:.1f}%")