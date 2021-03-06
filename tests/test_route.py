import re
import unittest
from unittest import mock

import itty3


class TestRoute(unittest.TestCase):
    def setUp(self):
        self.mock_index_view = mock.Mock()
        self.mock_simple_view = mock.Mock()
        self.mock_complex_view = mock.Mock()
        self.mock_static_view = mock.Mock()

        self.route_1 = itty3.Route("GET", "/", self.mock_index_view)
        self.route_2 = itty3.Route("GET", "/greet/", self.mock_simple_view)
        self.route_3 = itty3.Route(
            "GET", "/greet/<str:name>/<int:variant>/", self.mock_complex_view
        )
        self.route_4 = itty3.Route(
            "POST", "/greet/<str:name>/<int:variant>/", self.mock_complex_view
        )
        self.route_5 = itty3.Route(
            "GET", "/static/<any:asset_path>", self.mock_static_view
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
            re.compile("^/greet/(?P<name>[^/]+)/(?P<variant>[\\d]+)/$"),
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
            re.compile("^/greet/(?P<name>[^/]+)/(?P<variant>[\\d]+)/$"),
        )
        self.assertEqual(
            self.route_4._type_conversions, {"name": "str", "variant": "int"}
        )

    def test_get_re_for_type(self):
        self.assertEqual(
            self.route_1.get_re_for_type("str"), r"(?P<{var_name}>[^/]+)"
        )
        self.assertEqual(
            self.route_1.get_re_for_type("int"), r"(?P<{var_name}>[\d]+)"
        )
        self.assertEqual(
            self.route_1.get_re_for_type("float"),
            r"(?P<{var_name}>[\d]+.[\d]+)",
        )
        self.assertEqual(
            self.route_1.get_re_for_type("uuid"),
            "(?P<{{var_name}}>{})".format(itty3.UUID_PATTERN),
        )
        self.assertEqual(
            self.route_1.get_re_for_type("slug"),
            r"(?P<{var_name}>[\w\d._-]+)",
        )
        self.assertEqual(
            self.route_1.get_re_for_type("any"), r"(?P<{var_name}>.+)",
        )

    def test_create_re(self):
        regex, tc = self.route_1.create_re(self.complex_uri)
        raw_re = "^/app/(?P<app_id>[A-Fa-f0-9]{8}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}-[A-Fa-f0-9]{12})/(?P<title>[\\w\\d._-]+)/version/(?P<major_version>[\\d]+)/(?P<release>[^/]+)/$"
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

    def test_create_re_any(self):
        regex, tc = self.route_1.create_re("/static/<any:asset_path>")
        raw_re = "^/static/(?P<asset_path>.+)$"
        self.assertEqual(regex, re.compile(raw_re))
        self.assertEqual(
            tc, {"asset_path": "any"},
        )

    def test_can_handle(self):
        self.assertTrue(self.route_1.can_handle("GET", "/"))
        self.assertTrue(self.route_2.can_handle("GET", "/greet/"))
        self.assertTrue(self.route_3.can_handle("GET", "/greet/Daniel/3/"))
        self.assertTrue(self.route_4.can_handle("POST", "/greet/Daniel/3/"))
        self.assertTrue(
            self.route_5.can_handle("GET", "/static/css/default.css")
        )

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
            "app_id": "5fdd79e5-c417-42d7-8235-e7b6c6e10c06",
            "title": "content_dinos",
            "major_version": "2",
            "release": "test",
        }
        matches = route.convert_types(matches)
        self.assertEqual(
            matches,
            {
                "app_id": "5fdd79e5-c417-42d7-8235-e7b6c6e10c06",
                "title": "content_dinos",
                "major_version": 2,
                "release": "test",
            },
        )

    def test_convert_types_float(self):
        route = itty3.Route(
            "GET", "/charge/<float:money>/", self.mock_complex_view
        )

        matches = {
            "money": "22.95",
        }
        matches = route.convert_types(matches)
        self.assertEqual(
            matches, {"money": 22.95},
        )

    def test_convert_types_extra_matches(self):
        route = itty3.Route(
            "GET", "/charge/<float:money>/", self.mock_complex_view
        )

        matches = {
            "money": "22.95",
            # This shouldn't really happen in practice, but...
            "hello": "world",
        }
        matches = route.convert_types(matches)
        self.assertEqual(
            matches, {"money": 22.95, "hello": "world"},
        )

    def test_extract_kwargs(self):
        uri = "/app/5fdd79e5-c417-42d7-8235-e7b6c6e10c06/content_dinos/version/2/test/"
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
                "app_id": "5fdd79e5-c417-42d7-8235-e7b6c6e10c06",
                "title": "content_dinos",
                "major_version": 2,
                "release": "test",
            },
        )

    def test_extract_kwargs_no_variables(self):
        uri = "/app/"
        route = itty3.Route(
            "GET", "/app/<uuid:app_id>/", self.mock_complex_view
        )

        # Sanity check.
        self.assertEqual(route._type_conversions, {"app_id": "uuid"})

        self.assertEqual(route.extract_kwargs(uri), {})

    def test_extract_kwargs_any(self):
        uri = "/static/css/default.css"
        self.assertEqual(
            self.route_5.extract_kwargs(uri),
            {"asset_path": "css/default.css"},
        )
