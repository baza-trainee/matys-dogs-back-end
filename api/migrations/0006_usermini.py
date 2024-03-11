# Generated by Django 4.2.8 on 2024-01-25 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserMini',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=100, unique=True)),
                ('password', models.CharField(max_length=150)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('is_aproved', models.BooleanField(default=False)),
            ],
        ),
    ]
