# Generated by Django 3.0.2 on 2020-02-20 14:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('references', '0002_referencefield_referencetype'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf', models.FileField(upload_to='papers')),
                ('reference', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='references.Reference')),
            ],
        ),
    ]
