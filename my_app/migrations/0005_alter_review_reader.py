# Generated by Django 5.1.3 on 2024-12-02 19:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0004_alter_reader_user_signup_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='reader',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='my_app.reader'),
        ),
    ]
