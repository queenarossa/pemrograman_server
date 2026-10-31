# Simple LMS — Pemrograman Sisi Server (Minggu 4–5)

Backend sederhana untuk Learning Management System menggunakan **Django**, **PostgreSQL 17**, dan **Docker Compose**.

Entitas utama: `User` (role ADMIN / LECTURER / STUDENT), `Course`, `Lesson`, `Enrollment`, `Assignment`, `Submission`.

## Struktur project

```
week4/
├── manage.py
├── config/          # settings, urls, wsgi/asgi
├── users/           # Custom User (AbstractUser + role)
├── catalog/         # Course, Lesson, Enrollment, Assignment, Submission
│   └── management/commands/   # seed_demo, generate_performance_data, generate_relationship_data
├── benchmark_w5.py  # benchmark BEFORE/AFTER (Minggu 5)
├── requirements.txt
├── Dockerfile
├── compose.yaml
└── .env.example
```

## Prasyarat

- Docker Desktop (Docker Compose)
- Git

Python, Django, dan PostgreSQL **tidak perlu** diinstal di komputer; semuanya berjalan di container.

## Cara menjalankan

Semua perintah dijalankan dari folder `week4`.

**1. Buat file `.env`** (file ini tidak ikut di repository):

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # Linux / macOS
```

**2. Build dan jalankan container:**

```bash
docker compose up -d --build
docker compose ps
```

**3. Terapkan migrasi** (file migrasi sudah ada di repository):

```bash
docker compose exec app python manage.py migrate
docker compose exec app python manage.py check
```

**4. Buat superuser** (Django Admin):

```bash
docker compose exec app python manage.py createsuperuser
```

**5. Buat user dasar dan set role admin** (dibutuhkan oleh `seed_demo`):

```bash
docker compose exec app python manage.py shell
```

```python
from users.models import User
User.objects.filter(username="admin").update(role="ADMIN")   # ganti jika username superuser berbeda
User.objects.create_user(username="suprayogi", email="suprayogi@gmail.com", password="12345", role="LECTURER")
User.objects.create_user(username="fauzan", email="fauzan@gmail.com", password="12345", role="STUDENT")
exit()
```

**6. Isi data contoh** (idempotent, aman dijalankan berulang):

```bash
docker compose exec app python manage.py seed_demo
```

**7. Buka Django Admin:** <http://localhost:8000/admin/>

## Dataset performa (Minggu 5)

Membuat 10.000 Course dan data relasi (aman dijalankan berulang, tidak membuat duplikat).
Syarat: sudah ada user ber-role LECTURER (langkah 5).

```bash
docker compose exec app python manage.py generate_performance_data
docker compose exec app python manage.py generate_relationship_data
```

## Benchmark BEFORE vs AFTER

```bash
docker compose exec app python manage.py shell -c "exec(open('benchmark_w5.py').read())"
```

Skrip membandingkan jumlah query dan waktu untuk N+1 (`select_related`, `prefetch_related`), `exists()`, `count()`, `values()`, dan `annotate()`.

Untuk `EXPLAIN` pada index `(is_active, title)`:

```bash
docker compose exec db psql -U lms_user -d lms_db -c "ANALYZE catalog_course;"
docker compose exec app python manage.py shell -c "from catalog.models import Course; print(Course.objects.filter(is_active=True, title='Performance Course 5001').explain(analyze=True))"
```

## Menjalankan test

```bash
docker compose exec app python manage.py test catalog
```

## Reset database

```bash
docker compose down -v      # menghapus container dan volume database
```

Setelah itu ulangi dari langkah 2.

## Catatan

- File `.env` berisi kredensial development lokal dan **tidak boleh di-commit**. Gunakan `.env.example` sebagai template.
- Halaman `/` belum memiliki view; fokus Minggu 4–5 adalah model, ORM, dan optimasi query. Data diperiksa melalui Django Admin dan Django Shell.