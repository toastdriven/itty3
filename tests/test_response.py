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
