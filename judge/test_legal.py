from django.test import TestCase
from django.urls import reverse


class LegalPagesTest(TestCase):
    def test_pages_in_every_language(self):
        for page in ('tos', 'privacy'):
            for lang, marker in (('ru', 'Редакция от'), ('ky', 'Редакциясы'), ('en', 'Last updated'),
                                 ('de', 'Last updated')):
                response = self.client.get(reverse(page), HTTP_ACCEPT_LANGUAGE=lang)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, marker)

    def test_footer_links_resolve(self):
        self.assertEqual(reverse('tos'), '/tos/')
        self.assertEqual(reverse('privacy'), '/privacy/')
