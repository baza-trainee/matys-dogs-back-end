# Generated by Django 4.2.8 on 2024-02-02 19:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backblaze', '0003_alter_filemodel_category'),
        ('main_page', '0004_alter_newsmodel_options_newsmodel_sub_text_en_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsmodel',
            name='photo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='backblaze.filemodel'),
        ),
        migrations.AlterField(
            model_name='newsmodel',
            name='sub_text',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='newsmodel',
            name='url',
            field=models.URLField(max_length=150),
        ),
    ]
