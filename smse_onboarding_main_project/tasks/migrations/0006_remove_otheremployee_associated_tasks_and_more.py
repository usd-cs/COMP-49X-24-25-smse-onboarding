# Generated by Django 5.1.3 on 2025-02-21 08:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0005_merge_20250219_2352'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='otheremployee',
            name='associated_tasks',
        ),
        migrations.AddField(
            model_name='otheremployee',
            name='associated_tasks',
            field=models.ManyToManyField(blank=True, to='tasks.task'),
        ),
    ]
