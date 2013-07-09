"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase

from . import extractor

class ExtractorTest(TestCase):
    def test_get_pagemeta(self):
        url = 'http://blog.afaker.com/'
        meta = extractor.get_pagemeta(url)
        self.assertTrue(meta['title'] != None)

