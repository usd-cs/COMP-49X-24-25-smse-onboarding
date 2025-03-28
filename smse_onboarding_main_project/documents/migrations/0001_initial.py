# Generated by Django 5.1.7 on 2025-03-19 04:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tasks', '0003_remove_otheremployee_associated_tasks_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FacultyDocument',
            fields=[
                ('document_id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='faculty_documents/')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('faculty', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='tasks.faculty')),
                ('uploaded_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
