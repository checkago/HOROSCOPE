from django.test import Client, TestCase


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
