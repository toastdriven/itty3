import re
import unittest
from unittest import mock

import itty3


class TestRoute(unittest.TestCase):
    def setUp(self):
        self.mock_index_view = mock.Mock()
        self.mock_simple_view = mock.Mock()
        self.mock_complex_view = mock.Mock()

        self.route_1 = itty3.Route("GET", "/", self.mock_index_view)
        self.route_2 = itty3.Route("GET", "/greet/", self.mock_simple_view)
        self.route_3 = itty3.Route(
            "GET", "/greet/<str:name>/<int:variant>/", self.mock_complex_view
        )
        self.route_4 = itty3.Route(
            "POST", "/greet/<str:name>/<int:variant>/", self.mock_complex_view
        )

        self.complex_uri = (
            "/app/<uuid:app_id>/<slug:title>/version/"
            "<int:major_version>/<str:release>/"
        )

    def test_attributes_index(self):
        self.assertEqual(self.route_1.method, "GET")
        self.assertEqual(self.route_1.path, "/")
        self.assertEqual(self.route_1.func, self.mock_index_view)
        self.assertEqual(self.route_1._regex, re.compile("^/$"))
        self.assertEqual(self.route_1._type_conversions, {})

    def test_attributes_simple(self):
        self.assertEqual(self.route_2.method, "GET")
        self.assertEqual(self.route_2.path, "/greet/")
        self.assertEqual(self.route_2.func, self.mock_simple_view)
        self.assertEqual(self.route_2._regex, re.compile("^/greet/$"))
        self.assertEqual(self.route_2._type_conversions, {})

    def test_attributes_complex_get(self):
        self.assertEqual(self.route_3.method, "GET")
        self.assertEqual(
            self.route_3.path, "/greet/<str:name>/<int:variant>/"
        )
        self.assertEqual(self.route_3.func, self.mock_complex_view)
        self.assertEqual(
            self.route_3._regex,
            re.compile(
                "^/greet/(?P<name>[\\w\\d._-]+)/(?P<variant>[\\w\\d._-]+)/$"
            ),
        )
        self.assertEqual(
            self.route_3._type_conversions, {"name": "str", "variant": "int"}
        )

    def test_attributes_complex_post(self):
        self.assertEqual(self.route_4.method, "POST")
        self.assertEqual(
            self.route_4.path, "/greet/<str:name>/<int:variant>/"
        )
        self.assertEqual(self.route_4.func, self.mock_complex_view)
        self.assertEqual(
            self.route_4._regex,
            re.compile(
                "^/greet/(?P<name>[\\w\\d._-]+)/(?P<variant>[\\w\\d._-]+)/$"
            ),
        )
        self.assertEqual(
            self.route_4._type_conversions, {"name": "str", "variant": "int"}
        )

    def test_create_re(self):
        regex, tc = self.route_1.create_re(self.complex_uri)
        raw_re = (
            "^"
            "/app/(?P<app_id>[\\w\\d._-]+)/"
            "(?P<title>[\\w\\d._-]+)/"
            "version/"
            "(?P<major_version>[\\w\\d._-]+)/"
            "(?P<release>[\\w\\d._-]+)/"
            "$"
        )
        self.assertEqual(regex, re.compile(raw_re))
        self.assertEqual(
            tc,
            {
                "app_id": "uuid",
                "title": "slug",
                "major_version": "int",
                "release": "str",
            },
        )

    def test_can_handle(self):
        self.assertTrue(self.route_1.can_handle("GET", "/"))
        self.assertTrue(self.route_2.can_handle("GET", "/greet/"))
        self.assertTrue(self.route_3.can_handle("GET", "/greet/Daniel/3/"))
        self.assertTrue(self.route_4.can_handle("POST", "/greet/Daniel/3/"))

    def test_cant_handle(self):
        self.assertFalse(self.route_1.can_handle("POST", "/"))
        self.assertFalse(self.route_1.can_handle("GET", "/oof/"))

    def test_convert_types(self):
        route = itty3.Route("GET", self.complex_uri, self.mock_complex_view)

        # Sanity check.
        self.assertEqual(
            route._type_conversions,
            {
                "app_id": "uuid",
                "title": "slug",
                "major_version": "int",
                "release": "str",
            },
        )

        matches = {
            "app_id": "abc-123-not-uuid",
            "title": "content_dinos",
            "major_version": "2",
            "release": "test",
        }
        route.convert_types(matches)
        self.assertEqual(
            matches,
            {
                "app_id": "abc-123-not-uuid",
                "title": "content_dinos",
                "major_version": 2,
                "release": "test",
            },
        )

    def test_extract_kwargs(self):
        uri = "/app/abc-123-not-uuid/content_dinos/version/2/test/"
        route = itty3.Route("GET", self.complex_uri, self.mock_complex_view)

        # Sanity check.
        self.assertEqual(
            route._type_conversions,
            {
                "app_id": "uuid",
                "title": "slug",
                "major_version": "int",
                "release": "str",
            },
        )

        self.assertEqual(
            route.extract_kwargs(uri),
            {
                "app_id": "abc-123-not-uuid",
                "title": "content_dinos",
                "major_version": 2,
                "release": "test",
            },
        )
