# Generated by Django 5.1.2 on 2024-11-29 02:15

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=512, unique=True)),
                ('description', models.TextField(blank=True)),
                ('artist', models.CharField(max_length=64)),
                ('price', models.DecimalField(decimal_places=2, max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(999.99)])),
                ('format', models.CharField(choices=[('DD', 'Digital Download'), ('CD', 'CD'), ('VL', 'Vinyl')], max_length=2)),
                ('release_date', models.DateField()),
                ('cover_image', models.ImageField(blank=True, default='covers/default.jpg', null=True, upload_to='')),
                ('slug', models.SlugField(editable=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='AlbumTracklistItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.PositiveIntegerField(blank=True, null=True)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='label_music_manager.album')),
            ],
        ),
        migrations.CreateModel(
            name='MusicManagerUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display_name', models.CharField(max_length=512)),
                ('user_type', models.CharField(choices=[('artist', 'Artist'), ('editor', 'Editor'), ('viewer', 'Viewer')], max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Song',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=512)),
                ('length', models.PositiveBigIntegerField(validators=[django.core.validators.MinValueValidator(10)])),
                ('albums', models.ManyToManyField(related_name='songs', through='label_music_manager.AlbumTracklistItem', to='label_music_manager.album')),
            ],
        ),
        migrations.AddField(
            model_name='albumtracklistitem',
            name='song',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='label_music_manager.song'),
        ),
        migrations.AlterUniqueTogether(
            name='albumtracklistitem',
            unique_together={('album', 'song')},
        ),
    ]