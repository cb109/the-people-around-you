# Generated by Django 4.1.2 on 2023-02-21 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_person_merge_first_and_last_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='date_of_death',
            field=models.DateField(blank=True, default=None, null=True),
        ),
    ]