# Generated by Django 5.1.3 on 2025-03-03 01:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Faculty",
            fields=[
                ("faculty_id", models.AutoField(primary_key=True, serialize=False)),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("job_role", models.CharField(max_length=255)),
                ("engineering_dept", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=255, unique=True)),
                ("phone", models.CharField(max_length=10)),
                ("zoom_phone", models.CharField(blank=True, max_length=10, null=True)),
                ("office_room", models.CharField(max_length=20)),
                ("hire_date", models.DateTimeField()),
                ("mailing_list_status", models.BooleanField(default=False)),
                ("bio", models.TextField(blank=True)),
                ("completed_onboarding", models.BooleanField(default=False)),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="faculty_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FacultyDocument",
            fields=[
                ("document_id", models.AutoField(primary_key=True, serialize=False)),
                ("file_path", models.CharField(max_length=255)),
                (
                    "faculty",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tasks.faculty"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Task",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.TextField()),
                ("description", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("completed", models.BooleanField(default=False)),
                ("deadline", models.DateTimeField()),
                (
                    "assigned_to",
                    models.ManyToManyField(
                        blank=True, related_name="tasks", to="tasks.faculty"
                    ),
                ),
                (
                    "completed_by",
                    models.ManyToManyField(
                        blank=True, related_name="completed_tasks", to="tasks.faculty"
                    ),
                ),
                (
                    "prerequisite_task",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="tasks.task",
                    ),
                ),
            ],
            options={
                "ordering": ["created_at"],
            },
        ),
        migrations.CreateModel(
            name="OtherEmployee",
            fields=[
                (
                    "other_employee_id",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("job_role", models.CharField(max_length=255)),
                ("other_employee_dept", models.CharField(max_length=255)),
                ("email", models.EmailField(max_length=255)),
                ("phone", models.CharField(max_length=10)),
                ("office_room", models.CharField(max_length=20)),
                (
                    "associated_tasks",
                    models.ManyToManyField(blank=True, to="tasks.task"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TaskProgress",
            fields=[
                ("progress_id", models.AutoField(primary_key=True, serialize=False)),
                ("progress_status", models.CharField(max_length=255)),
                (
                    "faculty",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tasks.faculty"
                    ),
                ),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tasks.task"
                    ),
                ),
            ],
        ),
    ]
