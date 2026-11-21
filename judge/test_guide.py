import os

from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class GuidePageTest(TestCase):
    def test_page_in_every_language(self):
        for lang, marker in (('ru', 'Руководство пользователя'), ('ky', 'Колдонуучунун колдонмосу'),
                             ('en', 'User guide'), ('de', 'User guide')):
            response = self.client.get(reverse('guide'), HTTP_ACCEPT_LANGUAGE=lang)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, marker)

    def test_screenshots_exist(self):
        response = self.client.get(reverse('guide'))
        text = response.content.decode()
        names = {part.split('.jpg')[0] for part in text.split('guide/shots/')[1:]}
        self.assertTrue(names)
        for name in names:
            path = os.path.join(settings.BASE_DIR, 'resources', 'guide', 'shots', name + '.jpg')
            self.assertTrue(os.path.isfile(path), name)
