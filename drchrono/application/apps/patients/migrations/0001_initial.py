# Generated by Django 2.1.2 on 2018-11-04 07:37

from django.conf import settings
from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('first_name', models.CharField(max_length=250)),
                ('last_name', models.CharField(max_length=250)),
                ('birth_date', models.DateField(null=True)),
                ('phone_number', models.CharField(blank=True, max_length=250)),
                ('photo', models.CharField(null=True, max_length=500)),
                ('internal_id', models.CharField(max_length=100, unique=True)),
                ('internal_updated_at', models.CharField(max_length=100)),
                ('user', models.ManyToManyField(related_name='patients', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
