import importlib

from django.test import SimpleTestCase
from django.test.utils import override_settings


class MediaRoutingTests(SimpleTestCase):
    @override_settings(DEBUG=False, USE_CLOUDINARY=False)
    def test_media_urls_are_available_when_debug_is_off_and_local_storage_is_used(self):
        import eBhatat_Tender.urls as urls_module

        reloaded_urls = importlib.reload(urls_module)

        self.assertTrue(
            any("media" in str(pattern.pattern) for pattern in reloaded_urls.urlpatterns),
            "Media URLs should be registered when local filesystem storage is used.",
        )
