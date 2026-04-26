from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_article"),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyForecast",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("forecast_date", models.DateField(db_index=True)),
                ("content_markdown", models.TextField()),
                ("generated_at", models.DateTimeField(auto_now=True)),
                (
                    "profile",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="daily_forecasts",
                        to="core.profile",
                    ),
                ),
            ],
            options={
                "ordering": ("-forecast_date", "profile__code"),
                "unique_together": {("profile", "forecast_date")},
            },
        ),
    ]
