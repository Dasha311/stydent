# Generated by Django 5.2.4 on 2025-07-13 17:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0003_alter_course_description_alter_course_duration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='duration',
            field=models.DurationField(),
        ),
        migrations.AlterField(
            model_name='course',
            name='thumbnail',
            field=models.ImageField(default='', upload_to='course_thumbnails/'),
            preserve_default=False,
        ),
    ]
