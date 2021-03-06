# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orgs", "0016_taskstate_is_disabled"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("msgs", "0044_auto_20160517_1505"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReplyExport",
            fields=[
                ("id", models.AutoField(verbose_name="ID", serialize=False, auto_created=True, primary_key=True)),
                ("search", models.TextField()),
                ("filename", models.CharField(max_length=512)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="replyexports", to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT
                    ),
                ),
                (
                    "org",
                    models.ForeignKey(
                        related_name="replyexports",
                        verbose_name="Organization",
                        to="orgs.Org",
                        on_delete=models.PROTECT,
                    ),
                ),
            ],
            options={"abstract": False},
        )
    ]
