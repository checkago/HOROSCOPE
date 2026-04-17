from django.db import models


class Profile(models.Model):
    KIND_SIGN = "sign"
    KIND_CUSP = "cusp"
    KIND_CHOICES = (
        (KIND_SIGN, "Знак"),
        (KIND_CUSP, "Куспид"),
    )

    GENDER_MALE = "male"
    GENDER_FEMALE = "female"
    GENDER_CHOICES = (
        (GENDER_MALE, "Мужчина"),
        (GENDER_FEMALE, "Женщина"),
    )

    code = models.CharField(max_length=2, unique=True)
    name = models.CharField(max_length=120)
    display_name = models.CharField(max_length=140)
    kind = models.CharField(max_length=16, choices=KIND_CHOICES)
    gender = models.CharField(max_length=16, choices=GENDER_CHOICES)
    source_file = models.CharField(max_length=255)
    characteristic_markdown = models.TextField()

    class Meta:
        ordering = ("code",)

    def __str__(self) -> str:
        return f"{self.display_name}"


class Relationship(models.Model):
    source = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="outgoing_relations")
    target = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="incoming_relations")
    heading = models.CharField(max_length=160)

    interaction_type = models.TextField(blank=True)
    bound_state = models.TextField(blank=True)
    why = models.TextField(blank=True)
    quantum_dynamics = models.TextField(blank=True)
    intimacy = models.TextField(blank=True)
    synthesis = models.TextField(blank=True)
    vulnerabilities = models.TextField(blank=True)
    result_line = models.TextField(blank=True)
    enriched_text = models.TextField(blank=True)

    class Meta:
        ordering = ("source__code", "target__code")
        unique_together = ("source", "target")

    def __str__(self) -> str:
        return f"{self.source} -> {self.target}"
