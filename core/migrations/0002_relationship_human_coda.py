from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="relationship",
            name="human_coda",
            field=models.TextField(blank=True),
        ),
    ]
