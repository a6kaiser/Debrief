# Generated by Django 5.0.1 on 2024-10-18 16:46

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("news", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Article",
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
                ("site", models.CharField(max_length=200)),
                ("category", models.CharField(max_length=100)),
                ("url", models.URLField(unique=True)),
                ("title", models.CharField(max_length=200)),
                ("published_time", models.DateTimeField()),
                ("modified_time", models.DateTimeField()),
                ("article_text", models.TextField()),
            ],
        ),
        migrations.RemoveField(model_name="newsarticle", name="outlet",),
        migrations.RemoveField(model_name="event", name="articles",),
        migrations.RemoveField(model_name="event", name="date",),
        migrations.RemoveField(model_name="event", name="description",),
        migrations.AddField(
            model_name="event",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name="newsoutlet",
            name="icon",
            field=models.ImageField(
                blank=True, null=True, upload_to="news_outlet_icons/"
            ),
        ),
        migrations.CreateModel(
            name="ArticleFact",
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
                ("content", models.TextField()),
                ("newsworthiness", models.FloatField()),
                (
                    "article",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="facts",
                        to="news.article",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Author",
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
                ("name", models.CharField(max_length=100)),
                ("bio", models.TextField(blank=True)),
                (
                    "profile_picture",
                    models.ImageField(
                        blank=True, null=True, upload_to="author_profiles/"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="article",
            name="author",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="articles",
                to="news.author",
            ),
        ),
        migrations.CreateModel(
            name="AuthorOutletAssociation",
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
                ("start_date", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                ("role", models.CharField(blank=True, max_length=100)),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="outlet_associations",
                        to="news.author",
                    ),
                ),
                (
                    "outlet",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="author_associations",
                        to="news.newsoutlet",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EventFact",
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
                ("content", models.TextField()),
                ("newsworthiness", models.FloatField()),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="facts",
                        to="news.event",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="EventFactSource",
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
                ("contribution_weight", models.FloatField(default=1.0)),
                (
                    "article_fact",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="news.articlefact",
                    ),
                ),
                (
                    "event_fact",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sources",
                        to="news.eventfact",
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(name="Fact",),
        migrations.DeleteModel(name="NewsArticle",),
    ]
