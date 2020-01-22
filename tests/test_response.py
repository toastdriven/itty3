import datetime
import unittest
from unittest import mock

import itty3


class TestHttpResponse(unittest.TestCase):
    def setUp(self):
        self.response = itty3.HttpResponse("Hello, world!")
        self.complex_resp = itty3.HttpResponse(
            '{"success": false}',
            status_code=403,
            headers={"X-Auth-Token": "abcdef1234567890",},
            content_type="application/json",
        )

    def test_attributes_simple(self):
        self.assertEqual(self.response.body, "Hello, world!")
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(
            self.response.headers, {"Content-Type": "text/plain"}
        )
        self.assertEqual(self.response.content_type, "text/plain")

    def test_attributes_complex(self):
        self.assertEqual(self.complex_resp.body, '{"success": false}')
        self.assertEqual(self.complex_resp.status_code, 403)
        self.assertEqual(
            self.complex_resp.headers,
            {
                "Content-Type": "application/json",
                "X-Auth-Token": "abcdef1234567890",
            },
        )
        self.assertEqual(self.complex_resp.content_type, "application/json")

    def test_set_header(self):
        # Sanity check.
        self.assertEqual(self.response.headers["Content-Type"], "text/plain")
        self.assertEqual(self.response.content_type, "text/plain")
        self.assertFalse("X-So-Awesome" in self.response.headers)

        self.response.set_header("Content-Type", "text/html")
        self.response.set_header("X-So-Awesome", "true")
        self.assertEqual(self.response.headers["Content-Type"], "text/html")
        self.assertEqual(self.response.content_type, "text/html")
        self.assertEqual(self.response.headers["X-So-Awesome"], "true")

    def test_set_cookie(self):
        self.response.set_cookie("session", "abc123")
        self.response.set_cookie(
            "username",
            "johndoe",
            expires=datetime.datetime(2020, 1, 21, 20, 26, 8),
        )
        self.response.set_cookie(
            "moof", "dogcow", max_age=120, path="/history/macOS/", domain="*"
        )
        self.assertTrue("session" in self.response._cookies)
        self.assertTrue("username" in self.response._cookies)
        self.assertTrue("moof" in self.response._cookies)

    def test_delete_cookie(self):
        self.response.delete_cookie("session")
        self.assertEqual(
            self.response._cookies.output(),
            ("Set-Cookie: session=; Max-Age=0; Path=/"),
        )

    def test_write_no_start_response(self):
        with self.assertRaises(itty3.ResponseFailed):
            self.response.write()

    def test_write(self):
        mock_start_response = mock.Mock()
        self.response.start_response = mock_start_response

        res = self.response.write()
        self.assertEqual(res, [b"Hello, world!"])

        mock_start_response.assert_called_once_with(
            "200 OK", [("Content-Type", "text/plain")]
        )

    def test_write_with_cookies(self):
        mock_start_response = mock.Mock()
        self.response.start_response = mock_start_response

        self.response.set_cookie("session", "abc123")
        self.response.set_cookie(
            "username",
            "johndoe",
            expires=datetime.datetime(2020, 1, 21, 20, 26, 8),
        )
        self.response.set_cookie(
            "moof", "dogcow", max_age=120, path="/history/macOS/", domain="*"
        )

        res = self.response.write()
        self.assertEqual(res, [b"Hello, world!"])

        mock_start_response.assert_called_once_with(
            "200 OK",
            [
                ("Content-Type", "text/plain"),
                (
                    "Set-Cookie",
                    (
                        "moof=dogcow; Domain=*; Max-Age=120; "
                        "Path=/history/macOS/"
                    ),
                ),
                ("Set-Cookie", "session=abc123; Path=/"),
                (
                    "Set-Cookie",
                    (
                        "username=johndoe; "
                        "expires=Tue, 21 Jan 2020 20:26:08 GMT; Path=/"
                    ),
                ),
            ],
        )
