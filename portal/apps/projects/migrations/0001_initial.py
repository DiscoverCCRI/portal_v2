# Generated by Django 4.0.6 on 2022-07-31 19:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AerpawProject',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('created_by', models.EmailField(max_length=254)),
                ('modified_by', models.EmailField(max_length=254)),
                ('description', models.TextField()),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_public', models.BooleanField(default=False)),
                ('name', models.CharField(max_length=255)),
                ('uuid', models.CharField(editable=False, max_length=255)),
                ('project_creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='project_creator', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'AERPAW Project',
            },
        ),
        migrations.CreateModel(
            name='UserProject',
            fields=[
                ('id', models.AutoField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('granted_date', models.DateTimeField(auto_now_add=True)),
                ('project_role', models.CharField(choices=[('project_member', 'Project Member'), ('project_owner', 'Project Owner')], default='project_member', max_length=255)),
                ('granted_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_granted_by', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.aerpawproject')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='aerpawproject',
            name='project_membership',
            field=models.ManyToManyField(related_name='project_membership', through='projects.UserProject', to=settings.AUTH_USER_MODEL),
        ),
    ]
