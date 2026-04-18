from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_relationship_human_coda"),
    ]

    operations = [
        migrations.CreateModel(
            name="Article",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(max_length=140, unique=True)),
                ("title", models.CharField(max_length=220)),
                ("summary", models.TextField(blank=True)),
                ("body_markdown", models.TextField()),
                ("sort_order", models.PositiveSmallIntegerField(db_index=True, default=0)),
            ],
            options={
                "ordering": ("sort_order", "slug"),
            },
        ),
    ]
