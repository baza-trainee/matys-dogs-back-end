# Generated by Django 4.2.8 on 2024-01-04 17:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dog_card', '0002_dogcardmodel_delete_dog_card_model'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dogcardmodel',
            old_name='decription',
            new_name='description',
        ),
    ]
