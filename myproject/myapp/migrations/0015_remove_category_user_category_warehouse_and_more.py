# Generated by Django 5.0.6 on 2024-06-21 06:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("myapp", "0014_remove_category_warehouse_category_user_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="category",
            name="user",
        ),
        migrations.AddField(
            model_name="category",
            name="warehouse",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="myapp.warehouse",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="warehouse",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="users",
                to="myapp.warehouse",
            ),
        ),
        migrations.AlterField(
            model_name="warehouse",
            name="manager",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="managed_warehouse",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
