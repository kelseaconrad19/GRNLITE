# Generated by Django 5.1.3 on 2024-12-02 18:26

from django.utils.timezone import now
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('my_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='submitted_date',
            field=models.DateField(null=True),
        ),
        migrations.RenameField(
            model_name='author',
            old_name='submitted_date',
            new_name='date',
        ),
        migrations.RenameField(
            model_name='review',
            old_name='reader',
            new_name='reader_id',
        ),
        migrations.RenameField(
            model_name='review',
            old_name='comment',
            new_name='review',
        ),
        migrations.RemoveField(
            model_name='book',
            name='published_date',
        ),
        migrations.RemoveField(
            model_name='novel',
            name='published_date',
        ),
        migrations.RemoveField(
            model_name='reader',
            name='favorite_books',
        ),
        migrations.RemoveField(
            model_name='review',
            name='book',
        ),
        migrations.AddField(
            model_name='author',
            name='author_id',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='author',
            name='book_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='book',
            name='book_id',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='novel',
            name='novel_id',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='reader',
            name='previously_completed_reviews',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='reader',
            name='reader_id',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='reader',
            name='user_signup_date',
            field=models.DateTimeField(auto_now_add=True, default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='review',
            name='book_id',
            field=models.ForeignKey(default=now, on_delete=django.db.models.deletion.CASCADE, to='my_app.book'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='review',
            name='review_date',
            field=models.DateField(auto_now_add=True, default=now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='novel',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.book'),
        ),
        migrations.CreateModel(
            name='AuthorBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_id', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='my_app.author')),
                ('book_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.book')),
            ],
        ),
        migrations.CreateModel(
            name='BookNovel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.book')),
                ('novel_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.novel')),
            ],
        ),
        migrations.CreateModel(
            name='ReaderNovel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('novel_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.novel')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='my_app.reader')),
            ],
        ),
    ]