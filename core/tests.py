from django.test import Client, TestCase

from core.models import Profile
from core.url_slugs import profile_public_slug


class ProfileSlugTest(TestCase):
    def test_profile_public_slug_from_source_file_stem(self) -> None:
        p = Profile(source_file="01_Овен_Мужчина.md")
        self.assertEqual(profile_public_slug(p), "oven-muzhchina")


class SmokeUrlsTest(TestCase):
    """Базовые проверки маршрутов и отсутствия 500 на главных страницах."""

    def setUp(self) -> None:
        self.client = Client()

    def test_index_ok(self) -> None:
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)

    def test_about_ok(self) -> None:
        r = self.client.get("/o-podkhode/")
        self.assertEqual(r.status_code, 200)

    def test_article_list_ok(self) -> None:
        r = self.client.get("/stati/")
        self.assertEqual(r.status_code, 200)

    def test_api_options_characteristic_ok(self) -> None:
        r = self.client.get("/api/options/", {"mode": "characteristic"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("items", r.json())

    def test_api_options_bad_mode(self) -> None:
        r = self.client.get("/api/options/", {"mode": "invalid"})
        self.assertEqual(r.status_code, 400)

    def test_api_options_includes_slug(self) -> None:
        Profile.objects.create(
            code="98",
            name="SlugTest",
            display_name="Slug Test",
            kind=Profile.KIND_SIGN,
            gender=Profile.GENDER_MALE,
            source_file="98_Slug_Test.md",
            characteristic_markdown="body",
        )
        r = self.client.get("/api/options/", {"mode": "characteristic"})
        self.assertEqual(r.status_code, 200)
        items = r.json()["items"]
        self.assertTrue(any("slug" in it for it in items))
        row = next(it for it in items if it["slug"] == "slug-test")
        self.assertEqual(row["label"], "Slug Test")

    def test_legacy_profile_id_redirects_to_slug_url(self) -> None:
        p = Profile.objects.create(
            code="97",
            name="Redir",
            display_name="Redir Test",
            kind=Profile.KIND_SIGN,
            gender=Profile.GENDER_MALE,
            source_file="97_Redir_Test.md",
            characteristic_markdown="x",
        )
        r = self.client.get("/", {"mode": "characteristic", "profile_id": str(p.pk)}, follow=False)
        self.assertEqual(r.status_code, 301)
        loc = r["Location"]
        self.assertIn("profile=redir-test", loc.lower())
