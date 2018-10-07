# Generated by Django 2.0.7 on 2018-10-07 01:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('secret_store', '0004_auto_20180729_2136'),
    ]

    operations = [
        migrations.CreateModel(
            name='RecoveredTextSecret',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('release_date', models.DateField(blank=True)),
                ('date_created', models.DateField(auto_now_add=True)),
                ('text_secret', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='secret_store.TextSecret')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]