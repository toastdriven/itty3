"""
itty3
=====

The itty-bitty Python web framework... **Now Rewritten For Python 3!**
"""
import functools
import io
import re
import urllib.parse
import wsgiref.headers
import wsgiref.util


__author__ = "Daniel Lindsley"
__version__ = (1, 0, 0, "alpha")
__license__ = "New BSD"


def get_version(full=False):
    short = ".".join([str(v) for v in __version__[:3]])

    if full:
        long = "-".join([str(v) for v in __version__[3:]])
        return "{}-{}".format(short, long)

    return short


# Constants
GET = "GET"
POST = "POST"
PUT = "PUT"
DELETE = "DELETE"
PATCH = "PATCH"
HEAD = "HEAD"
OPTIONS = "OPTIONS"
TRACE = "TRACE"

PLAIN = "text/plain"
HTML = "text/html"
JSON = "application/json"
FORM = "application/x-www-form-urlencoded"
AJAX = "X-Requested-With"

# Borrowed & modified from Django.
RESPONSE_CODES = {
    100: "Continue",
    101: "Switching Protocols",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    306: "Reserved",
    307: "Temporary Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request-URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm A Teapot",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
}


# Exceptions
class IttyException(Exception):
    pass


class ResponseFailed(IttyException):
    pass


class RouteNotFound(IttyException):
    pass


# Request/Response bits
class QueryDict(object):
    def __init__(self, data=None):
        self._data = data

        if self._data is None:
            self._data = {}

    def __iter__(self):
        return iter(self._data)

    def __contains__(self, name):
        return name in self._data

    def __getitem__(self, name):
        values = self.getlist(name)
        return values[0]

    def __setitem__(self, name, value):
        self._data.setdefault(name, [])
        self._data[name][0] = value

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

    def getlist(self, name):
        if name not in self._data:
            raise KeyError("{} not found".format(name))

        return self._data[name]

    def setlist(self, name, values):
        self._data[name] = values

    def keys(self):
        return self._data.keys()

    def items(self):
        results = []

        for key, values in self._data.items():
            if len(values) < 1:
                results.append((key, ""))
            else:
                results.append((key, values[0]))

        return results


class HttpRequest(object):
    def __init__(
        self,
        uri,
        method,
        headers=None,
        body="",
        scheme="http",
        host="",
        port=80,
    ):
        self.raw_uri = uri
        self.method = method.upper()
        self.body = body
        self.scheme = scheme
        self.host = host
        self.port = int(port)

        # For caching.
        self._GET, self._POST, self._PUT = None, None, None

        if not headers:
            headers = {}

        # `Headers` is specific about wanting a list of tuples, so just doing
        # `headers.items()` isn't good enough here.
        self.headers = wsgiref.headers.Headers(
            [(k, v) for k, v in headers.items()]
        )

        uri_bits = self.split_uri(self.raw_uri)
        domain_bits = uri_bits.get("netloc", ":").split(":", 1)

        self.path = uri_bits["path"]
        self.query = uri_bits.get("query", {})
        self.fragment = uri_bits.get("fragment", "")

        if not self.host:
            self.host = domain_bits[0]

        if len(domain_bits) > 1 and domain_bits[1]:
            self.port = int(domain_bits[1])

    def split_uri(self, full_uri):
        bits = urllib.parse.urlparse(full_uri)

        uri_data = {
            "path": bits.path,
            "query": {},
            "fragment": bits.fragment,
        }

        # We need to do a bit more work to make the query portion useful.
        if bits.query:
            uri_data["query"] = urllib.parse.parse_qs(
                bits.query, keep_blank_values=True
            )

        if bits.netloc:
            uri_data["netloc"] = bits.netloc

        return uri_data

    @classmethod
    def from_wsgi(cls, environ):
        headers = {}

        for key, value in environ.items():
            if key.startswith("HTTP_"):
                headers[key[5:]] = value

        return cls(
            uri=wsgiref.util.request_uri(environ),
            method=environ.get("REQUEST_METHOD", GET),
            headers=headers,
            body=environ.get("wsgi.input", io.StringIO()).read(),
            scheme=wsgiref.util.guess_scheme(environ),
            port=environ.get("SERVER_PORT", "80"),
        )

    def content_type(self):
        return self.headers.get("Content-Type", HTML)

    @property
    def GET(self):
        if self._GET is not None:
            return self._GET

        self._GET = QueryDict(self.query)
        return self._GET

    @property
    def POST(self):
        if self._POST is not None:
            return self._POST

        self._POST = QueryDict(urllib.parse.parse_qs(self.body))
        return self._POST

    @property
    def PUT(self):
        if self._PUT is not None:
            return self._PUT

        self._PUT = QueryDict(urllib.parse.parse_qs(self.body))
        return self._PUT

    def is_ajax(self):
        return AJAX in self.headers

    def is_secure(self):
        return self.scheme == "https"


class HttpResponse(object):
    def __init__(
        self, body="", status_code=200, headers=None, content_type=PLAIN,
    ):
        self.body = body
        self.status_code = int(status_code)
        self.headers = headers or {}
        self.content_type = content_type
        self.start_response = None

        self.set_header("Content-Type", self.content_type)

    def set_header(self, name, value):
        self.headers[name] = value

        if name.lower() == "content-type":
            self.content_type = value

    def write(self):
        if not self.start_response:
            raise ResponseFailed(
                "{}.write called before being provided a callable".format(
                    self.__class__.__name__
                )
            )

        status = "{} {}".format(
            self.status_code,
            RESPONSE_CODES.get(self.status_code, RESPONSE_CODES[500]),
        )
        self.start_response(status, [(k, v) for k, v in self.headers.items()])
        return [self.body.encode("utf-8")]


# Routing
class Route(object):
    known_types = [
        "int",
        "float",
        "str",
        "uuid",
        "slug",
    ]

    def __init__(self, method, path, func):
        self.method = method
        self.path = path
        self.func = func
        self._regex, self._type_conversions = self.create_re(self.path)

    def __str__(self):
        return "<Route: {} for '{}'>".format(self.method, self.path,)

    def __repr__(self):
        return str(self)

    def create_re(self, path):
        # Start out assuming there will be no kwargs.
        raw_regex = path
        type_conversions = {}

        # Next, check for any variables
        variable_re = re.compile(r"\<(?P<ts>\w+):(?P<var_name>[\w\d]+)\>")
        var_matches = variable_re.findall(path)

        # Iterate over the two tuple, add to the type conversions &
        # spruce up the path regex.
        for var_type, var_name in var_matches:
            type_conversions[var_name] = var_type

            search = "<{}:{}>".format(var_type, var_name)
            replacement = r"(?P<{}>[\w\d._-]+)".format(var_name)
            raw_regex = raw_regex.replace(search, replacement)

        regex = re.compile("^" + raw_regex + "$")
        return regex, type_conversions

    def can_handle(self, method, path):
        if self.method != method:
            return False

        if not self._regex.match(path):
            return False

        return True

    def extract_kwargs(self, path):
        matches = self._regex.match(path)

        if matches:
            return self.convert_types(matches.groupdict())

        return {}

    def convert_types(self, matches):
        for name, value in matches.items():
            if name not in self._type_conversions:
                continue

            if self._type_conversions[name] == "int":
                matches[name] = int(value)
            elif self._type_conversions[name] == "float":
                matches[name] = float(value)

        return matches


# App!
class App(object):
    def __init__(self, debug=False):
        self._routes = []
        self.debug = debug

    def add_route(self, method, path, func):
        route = Route(method, path, func)
        self._routes.append(route)

    def find_route(self, method, path):
        for offset, route in enumerate(self._routes):
            if route.method == method:
                if route.path == path:
                    return offset

        raise RouteNotFound()

    def remove_route(self, method, path):
        try:
            offset = self.find_route(method, path)
            self._routes.pop(offset)
        except RouteNotFound:
            pass

    def error_404(self, request):
        return self.render(request, "Not Found", status_code=404)

    def error_500(self, request):
        return self.render(request, "Internal Error", status_code=500)

    def _add_view(self, method, path):
        def _wrapper(func):
            @functools.wraps(func)
            def _wrapped(request, *args, **kwargs):
                return func(request, *args, **kwargs)

            self.add_route(method, path, _wrapped)
            return _wrapped

        return _wrapper

    def get(self, path):
        return self._add_view(GET, path)

    def post(self, path):
        return self._add_view(POST, path)

    def put(self, path):
        return self._add_view(PUT, path)

    def delete(self, path):
        return self._add_view(DELETE, path)

    def patch(self, path):
        return self._add_view(PATCH, path)

    def render(
        self, request, body, status_code=200, content_type=HTML, headers=None,
    ):
        return HttpResponse(
            body=body,
            status_code=status_code,
            headers=headers,
            content_type=content_type,
        )

    def redirect(self, request, url, permanent=False):
        status_code = 302

        if permanent:
            status_code = 301

        resp = HttpResponse(body="", status_code=status_code)
        resp.set_header("Location", url)
        return resp

    def process_request(self, environ, start_response):
        request = HttpRequest.from_wsgi(environ)
        resp = None

        try:
            for route in self._routes:
                if not route.can_handle(request.method, request.path):
                    continue

                # We have a route that can handle the method & path!
                # Call the view function!
                try:
                    kwargs = route.extract_kwargs(request.path)
                    resp = route.func(request, **kwargs)
                    break
                except Exception:
                    if self.debug:
                        raise

                    resp = self.error_500(request)
                    break

            if not resp:
                raise RouteNotFound("No view found to handle method/path")
        except RouteNotFound:
            resp = self.error_404(request)

        if not resp:
            resp = self.error_500(request)

        resp.start_response = start_response
        return resp.write()

    def run(self, addr="", port=80):
        import sys
        from wsgiref.simple_server import make_server

        httpd = make_server(addr, port, self.process_request)

        print(
            "itty3 {}: Now serving requests at http://{}:{}...".format(
                get_version(full=True), addr, port
            )
        )

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            sys.exit(1)
