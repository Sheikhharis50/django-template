# Generated by Django 3.2.9 on 2022-06-04 14:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['-created_at'], 'verbose_name': 'User'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': 'User Profile'},
        ),
        migrations.AddField(
            model_name='user',
            name='is_email_verified',
            field=models.BooleanField(default=False, verbose_name='Email Verified'),
        ),
        migrations.AddField(
            model_name='user',
            name='is_hidden',
            field=models.BooleanField(default=False, verbose_name='Hidden'),
        ),
        migrations.AddField(
            model_name='user',
            name='refresh_token',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Refresh Token'),
        ),
        migrations.AddField(
            model_name='user',
            name='reset_token',
            field=models.TextField(blank=True, max_length=1000, null=True, verbose_name='Reset Token'),
        ),
        migrations.AddField(
            model_name='user',
            name='title',
            field=models.CharField(blank=True, default='', max_length=50, null=True, verbose_name='Title'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], max_length=100, null=True, verbose_name='Gender'),
        ),
        migrations.AlterField(
            model_name='user',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Created At'),
        ),
        migrations.AlterField(
            model_name='user',
            name='email',
            field=models.EmailField(max_length=255, unique=True, verbose_name='Email Address'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='First Name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Last Name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='Updated At'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True, verbose_name='Username'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='contact',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Contact No'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='dob',
            field=models.DateField(blank=True, null=True, verbose_name='Date of birth'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(db_column='user_id', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='website',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Website'),
        ),
    ]
