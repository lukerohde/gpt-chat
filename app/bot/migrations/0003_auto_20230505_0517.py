# Generated by Django 3.1.14 on 2023-05-05 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_auto_20230429_0357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bot',
            name='openai_api_key',
            field=models.CharField(default='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', max_length=100),
        ),
    ]
