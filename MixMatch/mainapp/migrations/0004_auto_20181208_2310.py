# Generated by Django 2.1.4 on 2018-12-08 23:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0003_auto_20181208_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='dob',
            field=models.DateField(blank=True, verbose_name='Date of Birth'),
        ),
    ]