# Generated by Django 5.1.4 on 2024-12-22 23:13

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FeedbackQuestion",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("developmental", "Developmental Edits"),
                            ("line_editing", "Line Editing"),
                            ("copy_editing", "Copy Editing"),
                        ],
                        help_text="Category of the feedback question",
                        max_length=20,
                    ),
                ),
                (
                    "question_text",
                    models.TextField(help_text="The text of the feedback question"),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Whether this question is currently in use",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(help_text="Name of the genre", max_length=100),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, help_text="Description of the genre", null=True
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Keyword",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Keyword for tagging manuscripts", max_length=100
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[("genre", "Genre"), ("theme", "Theme")],
                        help_text="Category of the keyword",
                        max_length=20,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Resource",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(help_text="Title of the resource", max_length=150),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, help_text="Description of the resource", null=True
                    ),
                ),
                (
                    "file_path",
                    models.FileField(
                        help_text="Path to the uploaded resource file",
                        upload_to="resources/",
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        blank=True,
                        help_text="Category of the resource (e.g., 'Templates', 'Guides')",
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "tags",
                    models.TextField(
                        blank=True,
                        help_text="Comma-separated tags for search and categorization",
                        null=True,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Timestamp when the resource was uploaded",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Timestamp when the resource was last updated",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AuthorSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "feedback_preferences",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Customizable preferences for the type of feedback the author wants",
                    ),
                ),
                (
                    "notification_preferences",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Notification settings for the author",
                    ),
                ),
                (
                    "profile_visibility",
                    models.BooleanField(
                        default=True,
                        help_text="Whether the author's profile is public or private",
                    ),
                ),
                (
                    "auto_submit_feedback",
                    models.BooleanField(
                        default=False,
                        help_text="Automatically submit feedback requests when manuscripts are uploaded",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="Timestamp of when the settings were created",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Timestamp of when the settings were last updated",
                    ),
                ),
                (
                    "author",
                    models.OneToOneField(
                        help_text="The author this settings configuration belongs to",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="settings",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BetaReader",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "experience",
                    models.TextField(
                        blank=True,
                        help_text="Summary of the beta reader's experience",
                        null=True,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When the beta reader profile was created",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="When the beta reader profile was last updated",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        help_text="The user who is a beta reader",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="beta_reader_profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "genres",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Genres the beta reader is interested in",
                        related_name="beta_readers",
                        to="my_app.genre",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Manuscript",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("title", models.CharField(max_length=200)),
                ("file_path", models.URLField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "Draft"),
                            ("submitted", "Submitted"),
                            ("in_review", "In Review"),
                            ("completed", "Completed"),
                        ],
                        default="draft",
                        help_text="Status of the manuscript",
                        max_length=30,
                    ),
                ),
                (
                    "nda_required",
                    models.BooleanField(
                        default=False,
                        help_text="Indicates if an NDA is required for this manuscript",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        help_text="The author of the manuscript",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="manuscripts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "keywords",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Keywords associated with the manuscript",
                        related_name="manuscripts",
                        to="my_app.keyword",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="FeedbackResponse",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "answer_text",
                    models.TextField(
                        blank=True,
                        help_text="The beta reader's answer to the question",
                        null=True,
                    ),
                ),
                (
                    "review_date",
                    models.DateTimeField(
                        auto_now_add=True, help_text="When the feedback was submitted"
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        help_text="The specific feedback question being answered",
                        on_delete=django.db.models.deletion.CASCADE,
                        to="my_app.feedbackquestion",
                    ),
                ),
                (
                    "reader",
                    models.ForeignKey(
                        help_text="The beta reader providing the feedback",
                        limit_choices_to={"groups__name": "beta_reader"},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feedback_given",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "manuscript",
                    models.ForeignKey(
                        help_text="The manuscript this feedback is for",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feedback_responses",
                        to="my_app.manuscript",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="BetaReaderApplication",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "reader_rating",
                    models.IntegerField(
                        blank=True,
                        help_text="Optional rating given to the beta reader for their application",
                        null=True,
                    ),
                ),
                (
                    "attachment",
                    models.FileField(
                        blank=True,
                        help_text="Optional attachment for the beta reader's application",
                        null=True,
                        upload_to="beta_reader_applications/",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("applied", "Applied"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        default="applied",
                        help_text="Status of the application",
                        max_length=10,
                    ),
                ),
                (
                    "application_date",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When the application was submitted",
                    ),
                ),
                (
                    "review_date",
                    models.DateTimeField(
                        blank=True,
                        help_text="When the application was reviewed by the author",
                        null=True,
                    ),
                ),
                (
                    "cover_letter",
                    models.TextField(
                        blank=True,
                        help_text="Optional message from the beta reader to the author",
                        null=True,
                    ),
                ),
                (
                    "beta_reader",
                    models.ForeignKey(
                        help_text="The beta reader submitting the application",
                        limit_choices_to={"groups__name": "beta_reader"},
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "manuscript",
                    models.ForeignKey(
                        help_text="The manuscript this application is for",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applications",
                        to="my_app.manuscript",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ManuscriptFeedbackPreference",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "manuscript",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="feedback_preferences",
                        to="my_app.manuscript",
                    ),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="manuscript_preferences",
                        to="my_app.feedbackquestion",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ManuscriptKeywords",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "keyword",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="my_app.keyword"
                    ),
                ),
                (
                    "manuscript",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="my_app.manuscript",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("message", models.TextField(help_text="Message of the notification")),
                (
                    "status",
                    models.CharField(
                        choices=[("read", "Read"), ("not_read", "Not Read")],
                        default="not_read",
                        help_text="Read status of the notification",
                        max_length=20,
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Timestamp when the notification was sent",
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Timestamp when the notification was read",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="The user receiving the notification",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notifications",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("author", "Author"),
                            ("beta_reader", "Beta Reader"),
                            ("editor", "Editor"),
                        ],
                        default="author",
                        help_text="Role of the user",
                        max_length=20,
                    ),
                ),
                (
                    "profile_img",
                    models.ImageField(
                        blank=True,
                        help_text="User's profile picture",
                        null=True,
                        upload_to="profile_images/",
                    ),
                ),
                (
                    "bio",
                    models.TextField(
                        blank=True, help_text="Short biography for the user", null=True
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, help_text="When the user account was created"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="When the user account was last updated",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        help_text="User who owns the profile",
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ResourceInteraction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "interaction_type",
                    models.CharField(
                        choices=[("download", "Download"), ("favorite", "Favorite")],
                        help_text="Type of user interaction",
                        max_length=50,
                    ),
                ),
                (
                    "timestamp",
                    models.DateTimeField(
                        auto_now_add=True, help_text="Timestamp of the interaction"
                    ),
                ),
                (
                    "resource",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="interactions",
                        to="my_app.resource",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        help_text="The user interacting with the resource",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="resource_interactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
