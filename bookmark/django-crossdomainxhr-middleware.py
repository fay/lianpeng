import re

from django.utils.text import compress_string
from django.utils.cache import patch_vary_headers

from django import http

try:
    from django.conf import settings
    XS_SHARING_ALLOWED_ORIGINS = settings.XS_SHARING_ALLOWED_ORIGINS
    XS_SHARING_ALLOWED_METHODS = settings.XS_SHARING_ALLOWED_METHODS
    XS_SHARING_ALLOWED_HEADERS = settings.XS_SHARING_ALLOWED_HEADERS
except:
    XS_SHARING_ALLOWED_ORIGINS = '*'
    XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']


class XsSharing(object):
    """
        This middleware allows cross-domain XHR using the html5
        postMessage API.

        Access-Control-Allow-Origin: http://foo.example
        Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE
    """
    def is_safe(self, request):
        origin = request.META.get('HTTP_ORIGIN')
        is_safe = False
        if origin:
            if origin.split('//')[1] == 'bookmarklet.sinaapp.com' or \
               origin == 'chrome-extension://bdomhbcbkbldbnechblaaaopghdmdcej':
                is_safe = True
        return is_safe, origin

    def process_request(self, request):

        is_safe, origin = self.is_safe(request)
        if is_safe:
            request._dont_enforce_csrf_checks = True

        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = http.HttpResponse()
            if is_safe:
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Methods'] = ",".join(
                    XS_SHARING_ALLOWED_METHODS)
                response['Access-Control-Allow-Headers'] = ",".join(
                    XS_SHARING_ALLOWED_HEADERS)
                response['Access-Control-Allow-Credentials'] = 'true'
            return response

        return None

    def process_response(self, request, response):
        # Avoid unnecessary work
        if response.has_header('Access-Control-Allow-Origin'):
            return response

        is_safe, origin = self.is_safe(request)
        if is_safe:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = ",".join(
                XS_SHARING_ALLOWED_METHODS)
            response['Access-Control-Allow-Credentials'] = 'true'

        return response
