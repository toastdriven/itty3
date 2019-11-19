import io
import unittest
from unittest import mock

import itty3


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = itty3.App()

        def mock_index(req):
            return self.app.render(req, "Hello")

        def mock_simple(req):
            return self.app.render(req, "Hello")

        def mock_complex(req, app_id):
            if req.method == itty3.POST:
                return self.app.render(req, "Handled {}".format(app_id))

            return self.app.render(req, "Saw {}".format(app_id))

        self.mock_index_view = mock.Mock()
        self.mock_index_view.side_effect = mock_index

        self.mock_simple_view = mock.Mock()
        self.mock_simple_view.side_effect = mock_simple

        self.mock_complex_view = mock.Mock()
        self.mock_complex_view.side_effect = mock_complex

        self.mock_environ = {
            "HTTP_CONTENT-TYPE": "application/json",
            "HTTP_ACCEPT": "application/json",
            "REQUEST_METHOD": "GET",
            "wsgi.input": io.StringIO('{"hello": "world"}'),
            "wsgi.url_scheme": "http",
            "HTTP_HOST": "example.com",
            "SERVER_PORT": "80",
            "PATH_INFO": "/",
        }

    def test_attributes(self):
        self.assertEqual(self.app._routes, [])
        self.assertEqual(self.app.debug, False)

    def test_add_route(self):
        self.assertEqual(len(self.app._routes), 0)

        self.app.add_route("GET", "/", self.mock_index_view)
        self.assertEqual(len(self.app._routes), 1)
        self.assertEqual(self.app._routes[0].method, "GET")
        self.assertEqual(self.app._routes[0].path, "/")

        self.app.add_route("GET", "/test/", self.mock_index_view)
        self.assertEqual(len(self.app._routes), 2)
        self.assertEqual(self.app._routes[1].method, "GET")
        self.assertEqual(self.app._routes[1].path, "/test/")

    def test_find_route(self):
        self.app.add_route("GET", "/", self.mock_index_view)
        self.app.add_route("GET", "/test/", self.mock_index_view)
        self.app.add_route("GET", "/app/<uuid:app_id>/", self.mock_index_view)
        self.assertEqual(len(self.app._routes), 3)

        self.assertEqual(self.app.find_route("GET", "/"), 0)
        self.assertEqual(self.app.find_route("GET", "/test/"), 1)
        self.assertEqual(self.app.find_route("GET", "/app/<uuid:app_id>/"), 2)

        with self.assertRaises(itty3.RouteNotFound):
            self.app.find_route("PATCH", "/nope/")

    def test_remove_route(self):
        self.app.add_route("GET", "/", self.mock_index_view)
        self.app.add_route("GET", "/test/", self.mock_index_view)
        self.app.add_route("GET", "/app/<uuid:app_id>/", self.mock_index_view)
        self.assertEqual(len(self.app._routes), 3)

        self.app.remove_route("GET", "/test/")
        self.assertEqual(len(self.app._routes), 2)

        self.app.remove_route("PATCH", "/nope/")
        self.assertEqual(len(self.app._routes), 2)

    def test_render(self):
        req = itty3.HttpRequest("/greet/?name=Daniel", "GET")
        resp = self.app.render(req, "Hello, Daniel!", content_type=itty3.HTML)
        self.assertEqual(resp.body, "Hello, Daniel!")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, itty3.HTML)
        self.assertEqual(resp.headers, {"Content-Type": "text/html"})

    def test_render_json(self):
        req = itty3.HttpRequest("/greet/?name=Daniel", "GET")
        resp = self.app.render_json(req, {"greeting": "Hello, Daniel!"})
        self.assertEqual(resp.body, '{"greeting": "Hello, Daniel!"}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, itty3.JSON)
        self.assertEqual(resp.headers, {"Content-Type": "application/json"})

    def test_error_404(self):
        req = itty3.HttpRequest("/greet/?name=Daniel", "GET")
        resp = self.app.error_404(req)
        self.assertEqual(resp.body, "Not Found")
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.content_type, itty3.HTML)
        self.assertEqual(resp.headers, {"Content-Type": "text/html"})

    def test_error_500(self):
        req = itty3.HttpRequest("/greet/?name=Daniel", "GET")
        resp = self.app.error_500(req)
        self.assertEqual(resp.body, "Internal Error")
        self.assertEqual(resp.status_code, 500)
        self.assertEqual(resp.content_type, itty3.HTML)
        self.assertEqual(resp.headers, {"Content-Type": "text/html"})

    def test_redirect(self):
        req = itty3.HttpRequest("/greet/?name=Daniel", "GET")
        resp = self.app.redirect(req, "/why/hello/there/Daniel/")
        self.assertEqual(resp.body, "")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.content_type, itty3.PLAIN)
        self.assertEqual(
            resp.headers,
            {
                "Content-Type": "text/plain",
                "Location": "/why/hello/there/Daniel/",
            },
        )

    def test_redirect_permanent(self):
        req = itty3.HttpRequest("/greet/?name=Daniel", "GET")
        resp = self.app.redirect(
            req, "/why/hello/there/Daniel/", permanent=True
        )
        self.assertEqual(resp.body, "")
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp.content_type, itty3.PLAIN)
        self.assertEqual(
            resp.headers,
            {
                "Content-Type": "text/plain",
                "Location": "/why/hello/there/Daniel/",
            },
        )

    def setup_working_app(self):
        self.app.add_route("GET", "/", self.mock_index_view)
        self.app.add_route("GET", "/test/", self.mock_simple_view)
        self.app.add_route(
            "GET", "/app/<uuid:app_id>/", self.mock_complex_view
        )
        self.app.add_route(
            "POST", "/app/<uuid:app_id>/", self.mock_complex_view
        )

    def test___call__(self):
        self.setup_working_app()

        self.mock_environ["wsgi.input"] = io.StringIO()
        mock_sr = mock.Mock()

        # We've already got an instance, so this is actually hitting
        # `App.__call__`.
        # This is for integrating with other WSGI servers.
        resp = self.app(self.mock_environ, mock_sr)
        self.assertEqual(resp, [b"Hello"])
        mock_sr.assert_called_once_with(
            "200 OK", [("Content-Type", "text/html")]
        )
        self.mock_index_view.assert_called_once_with(mock.ANY)

    def test_process_request_index(self):
        self.setup_working_app()

        self.mock_environ["wsgi.input"] = io.StringIO()
        mock_sr = mock.Mock()

        resp = self.app.process_request(self.mock_environ, mock_sr)
        self.assertEqual(resp, [b"Hello"])
        mock_sr.assert_called_once_with(
            "200 OK", [("Content-Type", "text/html")]
        )
        self.mock_index_view.assert_called_once_with(mock.ANY)

    def test_process_request_simple(self):
        self.setup_working_app()

        self.mock_environ["wsgi.input"] = io.StringIO()
        self.mock_environ["PATH_INFO"] = "/test/"
        mock_sr = mock.Mock()

        resp = self.app.process_request(self.mock_environ, mock_sr)
        self.assertEqual(resp, [b"Hello"])
        mock_sr.assert_called_once_with(
            "200 OK", [("Content-Type", "text/html")]
        )
        self.mock_simple_view.assert_called_once_with(mock.ANY)

    def test_process_request_complex_get(self):
        self.setup_working_app()

        self.mock_environ["wsgi.input"] = io.StringIO()
        self.mock_environ["REQUEST_METHOD"] = "GET"
        self.mock_environ[
            "PATH_INFO"
        ] = "/app/5fdd79e5-c417-42d7-8235-e7b6c6e10c06/"
        mock_sr = mock.Mock()

        resp = self.app.process_request(self.mock_environ, mock_sr)
        self.assertEqual(resp, [b"Saw 5fdd79e5-c417-42d7-8235-e7b6c6e10c06"])
        mock_sr.assert_called_once_with(
            "200 OK", [("Content-Type", "text/html")]
        )
        req_seen = self.mock_complex_view.call_args[0][0]
        self.assertEqual(req_seen.method, "GET")

    def test_process_request_complex_post(self):
        self.setup_working_app()

        self.mock_environ["wsgi.input"] = io.StringIO()
        self.mock_environ["REQUEST_METHOD"] = "POST"
        self.mock_environ[
            "PATH_INFO"
        ] = "/app/5fdd79e5-c417-42d7-8235-e7b6c6e10c06/"
        mock_sr = mock.Mock()

        resp = self.app.process_request(self.mock_environ, mock_sr)
        self.assertEqual(
            resp, [b"Handled 5fdd79e5-c417-42d7-8235-e7b6c6e10c06"]
        )
        mock_sr.assert_called_once_with(
            "200 OK", [("Content-Type", "text/html")]
        )
        req_seen = self.mock_complex_view.call_args[0][0]
        app_id = self.mock_complex_view.call_args[1].get("app_id")
        self.assertEqual(req_seen.method, "POST")
        self.assertEqual(app_id, "5fdd79e5-c417-42d7-8235-e7b6c6e10c06")

    def test_process_request_not_found(self):
        self.setup_working_app()

        self.mock_environ["wsgi.input"] = io.StringIO()
        self.mock_environ["REQUEST_METHOD"] = "GET"
        self.mock_environ["PATH_INFO"] = "/nope/nope/nope/"
        mock_sr = mock.Mock()

        resp = self.app.process_request(self.mock_environ, mock_sr)
        self.assertEqual(resp, [b"Not Found"])
        mock_sr.assert_called_once_with(
            "404 Not Found", [("Content-Type", "text/html")]
        )
        self.mock_index_view.assert_not_called()
        self.mock_simple_view.assert_not_called()
        self.mock_complex_view.assert_not_called()

    def test_process_request_app_error(self):
        self.setup_working_app()

        self.mock_environ["wsgi.input"] = io.StringIO()
        self.mock_environ["REQUEST_METHOD"] = "GET"
        self.mock_environ["PATH_INFO"] = "/"
        mock_sr = mock.Mock()

        # Introduce an application error!
        def broke_af(req):
            raise IndexError("You messed up!")

        self.mock_index_view.side_effect = broke_af

        resp = self.app.process_request(self.mock_environ, mock_sr)
        self.assertEqual(resp, [b"Internal Error"])
        mock_sr.assert_called_once_with(
            "500 Internal Server Error", [("Content-Type", "text/html")]
        )
        self.mock_index_view.assert_called_once_with(mock.ANY)

    def test_process_request_bad_404_override(self):
        class OopsApp(itty3.App):
            def error_404(self, request):
                # We didn't return a response OH NOES
                2 + 5

        app = OopsApp()

        self.mock_environ["wsgi.input"] = io.StringIO()
        self.mock_environ["REQUEST_METHOD"] = "GET"
        self.mock_environ["PATH_INFO"] = "/"
        mock_sr = mock.Mock()

        resp = app.process_request(self.mock_environ, mock_sr)
        self.assertEqual(resp, [b"Internal Error"])
        mock_sr.assert_called_once_with(
            "500 Internal Server Error", [("Content-Type", "text/html")]
        )


class TestAppDecorators(unittest.TestCase):
    def test_decorators(self):
        app = itty3.App()
        # Sanity check.
        self.assertEqual(len(app._routes), 0)

        @app.get("/")
        def index(req):
            return app.render("Index")

        @app.get("/lists/")
        def get_lists(req):
            return app.render("5 lists")

        @app.post("/lists/")
        def create_list(req):
            return app.render("Made a new list")

        @app.put("/lists/<int:list_id>")
        def create_list(req, list_id):
            return app.render("Updated that list")

        @app.patch("/lists/bulk")
        def bulk_list(req, list_id):
            return app.render("Changed a bunch of that list")

        @app.delete("/lists/<int:list_id>")
        def delete_list(req, list_id):
            return app.render("Killed that list")

        # Now check the routes to ensure they were populated.
        self.assertEqual(len(app._routes), 6)

        self.assertEqual(app._routes[0].method, "GET")
        self.assertEqual(app._routes[0].path, "/")

        self.assertEqual(app._routes[1].method, "GET")
        self.assertEqual(app._routes[1].path, "/lists/")

        self.assertEqual(app._routes[2].method, "POST")
        self.assertEqual(app._routes[2].path, "/lists/")

        self.assertEqual(app._routes[3].method, "PUT")
        self.assertEqual(app._routes[3].path, "/lists/<int:list_id>")

        self.assertEqual(app._routes[4].method, "PATCH")
        self.assertEqual(app._routes[4].path, "/lists/bulk")

        self.assertEqual(app._routes[5].method, "DELETE")
        self.assertEqual(app._routes[5].path, "/lists/<int:list_id>")

    def test__add_view(self):
        # This is largely for coverage, but is one of the more important
        # lines in itty3, so exercise it.
        app = itty3.App()
        mock_req = mock.Mock()

        def adder(req, x, y):
            return x + y

        head_wrapper = app._add_view("HEAD", "/")
        head_wrapped = head_wrapper(adder)

        self.assertEqual(head_wrapped(mock_req, 2, 3), 5)
