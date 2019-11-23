# -*- coding: utf-8 -*-
"""
itty3
=====

The itty-bitty Python web framework... **Now Rewritten For Python 3!**
"""
import functools
import io
import json
import logging
import re
import urllib.parse
import wsgiref.headers
import wsgiref.util


__author__ = "Daniel Lindsley"
__version__ = (
    1,
    0,
    0,
)
__license__ = "New BSD"


def get_version(full=False):
    """
    Fetches the current version of itty3.

    Args:
        full (bool): Chooses between the short semver version and the
            longer/full version, including release information.

    Returns:
        str: The version string
    """
    short = ".".join([str(v) for v in __version__[:3]])

    if full:
        long = "-".join([str(v) for v in __version__[3:]])
        return "{}-{}".format(short, long)

    return short


# Default logging config for itty3.
# We attach a NullHandler by default, so that we don't produce logs.
# The user can choose to add new handlers to capture logs, at the
# level/location they wish.
log = logging.getLogger(__name__)
null_handler = logging.NullHandler()
log.addHandler(null_handler)


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

UUID_PATTERN = (
    r"[A-Fa-f0-9]{{8}}-"
    r"[A-Fa-f0-9]{{4}}-"
    r"[A-Fa-f0-9]{{4}}-"
    r"[A-Fa-f0-9]{{4}}-"
    r"[A-Fa-f0-9]{{12}}"
)

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
    """
    The base exception for all itty3 exceptions.
    """

    pass


class ResponseFailed(IttyException):
    """
    Raised when a response could not be returned to the server/user.
    """

    pass


class RouteNotFound(IttyException):
    """
    Raised when no method/path combination could be found.
    """

    pass


# Request/Response bits
class QueryDict(object):
    """
    Simulates a dict-like object for query parameters.

    Because HTTP allows for query strings to provide the same name for a
    parameter more than once, this object smoothes over the day-to-day usage
    of those queries.

    You can act like it's a plain `dict` if you only need a single value.

    If you need all the values, `QueryDict.getlist` & `QueryDict.setlist`
    are available to expose the full list.
    """

    def __init__(self, data=None):
        self._data = data

        if self._data is None:
            self._data = {}

    def __str__(self):
        return "<QueryDict: {} keys>".format(len(self._data))

    def __repr__(self):
        return str(self)

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
        """
        Tries to fetch a value for a given name.

        If not found, this returns the provided `default`.

        Args:
            name (str): The name of the parameter you'd like to fetch
            default (bool, defaults to `None`): The value to return if the
                `name` isn't found.

        Returns:
            Any: The found value for the `name`, or the `default`.
        """
        try:
            return self[name]
        except KeyError:
            return default

    def getlist(self, name):
        """
        Tries to fetch all values for a given name.

        Args:
            name (str): The name of the parameter you'd like to fetch

        Returns:
            list: The found values for the `name`.

        Raises:
            KeyError: If the `name` isn't found
        """
        if name not in self._data:
            raise KeyError("{} not found".format(name))

        return self._data[name]

    def setlist(self, name, values):
        """
        Sets all values for a given name.

        Args:
            name (str): The name of the parameter you'd like to fetch
            values (list): The list of all values

        Returns:
            None
        """
        self._data[name] = values

    def keys(self):
        """
        Returns all the parameter names.

        Returns:
            list: A list of all the parameter names
        """
        return self._data.keys()

    def items(self):
        """
        Returns all the parameter names & values.

        Returns:
            list: A list of two-tuples. The parameter names & the *first*
                value for that name.
        """
        results = []

        for key, values in self._data.items():
            if len(values) < 1:
                results.append((key, None))
            else:
                results.append((key, values[0]))

        return results


class HttpRequest(object):
    """
    A request object, representing all the portions of the HTTP request.

    Args:
        uri (str): The URI being requested.
        method (str): The HTTP method ("GET|POST|PUT|DELETE|PATCH|HEAD")
        headers (dict, Optional): The received HTTP headers
        body (str, Optional): The body of the HTTP request
        scheme (str, Optional): The HTTP scheme ("http|https")
        host (str, Optional): The hostname of the request
        port (int, Optional): The port of the request
        content_length (int, Optional): The length of the body of the request
        request_protocol (str, Optional): The protocol of the request
    """

    def __init__(
        self,
        uri,
        method,
        headers=None,
        body="",
        scheme="http",
        host="",
        port=80,
        content_length=0,
        request_protocol="HTTP/1.0",
    ):
        self.raw_uri = uri
        self.method = method.upper()
        self.body = body
        self.scheme = scheme
        self.host = host
        self.port = int(port)
        self.content_length = int(content_length)
        self.request_protocol = request_protocol

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

    def __str__(self):
        return "<HttpRequest: {} {}>".format(self.method, self.raw_uri)

    def __repr__(self):
        return str(self)

    def get_status_line(self):
        return "{} {} {}".format(
            self.method, self.path, self.request_protocol
        )

    def split_uri(self, full_uri):
        """
        Breaks a URI down into components.

        Args:
            full_uri (str): The URI to parse

        Returns:
            dict: A dictionary of the components. Includes `path`, `query`
                `fragment`, as well as `netloc` if host/port information is
                present.
        """
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
        """
        Builds a new HttpRequest from the provided WSGI `environ`.

        Args:
            environ (dict): The bag of YOLO that is the WSGI environment

        Returns:
            HttpRequest: A fleshed out request object, based on what was
                present.
        """
        headers = {}
        non_http_prefixed_headers = [
            "CONTENT-TYPE",
            "CONTENT-LENGTH",
            # TODO: Maybe in the future, add support for...?
            # 'GATEWAY_INTERFACE',
            # 'REMOTE_ADDR',
            # 'REMOTE_HOST',
            # 'SCRIPT_NAME',
            # 'SERVER_NAME',
            # 'SERVER_PORT',
        ]

        for key, value in environ.items():
            mangled_key = key.replace("_", "-")

            if mangled_key.startswith("HTTP-"):
                headers[mangled_key[5:]] = value
            elif mangled_key in non_http_prefixed_headers:
                headers[mangled_key] = value

        body = ""
        wsgi_input = environ.get("wsgi.input", io.StringIO(""))
        content_length = environ.get("CONTENT_LENGTH", 0)

        if content_length not in ("", 0):
            # StringIO & the built-in server have this attribute, but things
            # like gunicorn do not. Give it our best effort.
            if not getattr(wsgi_input, "closed", False):
                body = wsgi_input.read(int(content_length))
        else:
            content_length = 0

        return cls(
            uri=wsgiref.util.request_uri(environ),
            method=environ.get("REQUEST_METHOD", GET),
            headers=headers,
            body=body,
            scheme=wsgiref.util.guess_scheme(environ),
            port=environ.get("SERVER_PORT", "80"),
            content_length=content_length,
            request_protocol=environ.get("SERVER_PROTOCOL", "HTTP/1.0"),
        )

    def content_type(self):
        """
        Returns the received Content-Type header.

        Returns:
            str: The content-type header or "text/html" if it was absent.
        """
        return self.headers.get("Content-Type", HTML)

    def _ensure_unicode(self, body):
        raw_data = urllib.parse.parse_qs(body)
        revised_data = {}

        # `urllib.parse.parse_qs` can be a very BYTESTRING-Y BOI.
        # Ensure all the keys/value are Unicode.
        for key, value in raw_data.items():
            if isinstance(key, bytes):
                key = key.decode("utf-8")

            if isinstance(value, bytes):  # pragma: no cover
                value = value.decode("utf-8")
            elif isinstance(value, (list, tuple)):
                new_value = []

                for v in value:
                    if isinstance(v, bytes):
                        v = v.decode("utf-8")

                    new_value.append(v)

                value = new_value

            revised_data[key] = value

        return revised_data

    @property
    def GET(self):
        """
        Returns a `QueryDict` of the GET parameters.
        """
        if self._GET is not None:
            return self._GET

        self._GET = QueryDict(self.query)
        return self._GET

    @property
    def POST(self):
        """
        Returns a `QueryDict` of the POST parameters from the request body.

        Useless if the body isn't form-encoded data, like JSON bodies.
        """
        if self._POST is not None:
            return self._POST

        self._POST = QueryDict(self._ensure_unicode(self.body))
        return self._POST

    @property
    def PUT(self):
        """
        Returns a `QueryDict` of the PUT parameters from the request body.

        Useless if the body isn't form-encoded data, like JSON bodies.
        """
        if self._PUT is not None:
            return self._PUT

        self._PUT = QueryDict(self._ensure_unicode(self.body))
        return self._PUT

    def is_ajax(self):
        """
        Identifies if the request came from an AJAX call.

        Returns:
            bool: True if sent via AJAX, False otherwise
        """
        return AJAX in self.headers

    def is_secure(self):
        """
        Identifies whether or not the request was secure.

        Returns:
            bool: True if the environment specified HTTPs, False otherwise
        """
        return self.scheme == "https"

    def json(self):
        """
        Decodes a JSON body if present.

        Returns:
            dict: The data
        """
        if self.content_type() != JSON:
            return {}

        return json.loads(self.body)


class HttpResponse(object):
    """
    A response object, to make responding to requests easier.

    A lightly-internal `start_response` attribute must be manually set on the
    response object when in a WSGI environment in order to send the response.

    Args:
        body (str, Optional): The body of the response. Defaults to "".
        status_code (int, Optional): The HTTP status code (without the
            reason). Default is `200`.
        headers (dict, Optional): The headers to supply with the response.
            Default is empty headers.
        content_type (str, Optional): The content-type of the response.
            Default is `text/plain`.
    """

    def __init__(
        self, body="", status_code=200, headers=None, content_type=PLAIN,
    ):
        self.body = body
        self.status_code = int(status_code)
        self.headers = headers or {}
        self.content_type = content_type
        self.start_response = None

        self.set_header("Content-Type", self.content_type)

    def __str__(self):
        return "<HttpResponse: {}>".format(self.status_code)

    def __repr__(self):
        return str(self)

    def set_header(self, name, value):
        """
        Sets a header on the response.

        If the `Content-Type` header is provided, this also updates the
        value of `HttpResponse.content_type`.

        Args:
            name (str): The name of the header.
            value (Any): The value of the header.
        """
        self.headers[name] = value

        if name.lower() == "content-type":
            self.content_type = value

    def write(self):
        """
        Begins the transmission of the response.

        The lightly-internal `start_response` attribute **MUST** be manually
        set on the object **BEFORE** calling this method! This callable is
        called during execution to set the status line & headers of the
        response.

        Returns:
            iterable: An iterable of the content

        Raises:
            ResponseFailed: If no `start_response` was set before calling.
        """
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
    """
    Handles setting up a given route. Composed of a HTTP method, a URI path
    & "view" (a callable function that takes a `request` & returns a
    `response` object) for handling a matching request.

    Variables can be added to the path using a `<type:variable_name>` syntax.
    For instance, if you wanted to capture a UUID & an integer in a URI, you
    could provide the following `path`::

        "/app/<uuid:app_id>/version/<int:major_version>/"

    These would be added onto the call to the view as additional arguments.
    In the case of the previous `path`, the view's signature should look
    like::

        def app_info(request, app_id, major_version): ...

    Supported types include:

    * `str`
    * `int`
    * `float`
    * `slug`
    * `uuid`

    Args:
        method (str): The HTTP method
        path (str): The URI path to match against
        func (callable): The view function to handle a matching request
    """

    known_types = [
        "str",
        "int",
        "float",
        "uuid",
        "slug",
    ]

    def __init__(self, method, path, func):
        self.method = method.upper()
        self.path = path
        self.func = func
        self._regex, self._type_conversions = self.create_re(self.path)

    def __str__(self):
        return "<Route: {} for '{}'>".format(self.method, self.path,)

    def __repr__(self):
        return str(self)

    def get_re_for_int(self):
        return r"[\d]+"

    def get_re_for_float(self):
        return r"[\d]+.[\d]+"

    def get_re_for_uuid(self):
        return UUID_PATTERN

    def get_re_for_slug(self):
        return r"[\w\d._-]+"

    def get_re_for_type(self, desired_type):
        """
        Fetches the correct regex for a given type.

        Args:
            desired_type (str): The provided type to get a regex for

        Returns:
            str: A raw string of the regex (minus the variable name)
        """
        pattern = r"[^/]+"
        get_re_method_name = "get_re_for_{}".format(desired_type)
        get_re_method = getattr(self, get_re_method_name, None)

        if get_re_method is not None:
            pattern = get_re_method()

        regex_frag = r"(?P<{{var_name}}>{})".format(pattern)
        return regex_frag

    def create_re(self, path):
        """
        Creates a compiled regular expression of a `path`.

        It'd be unusual to need this as an end-user, but who am I to stop
        you? :)

        Args:
            path (str): A URI path, potentially with `<type:variable_name>`
                bits in it.

        Returns:
            tuple: A tuple of the compiled regular expression that suits the
                path & dict of the variable names/type conversions to be done
                upon matching.
        """
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
            # Get the type-appropriate replacement regex.
            replacement_raw_re = self.get_re_for_type(var_type)
            replacement = replacement_raw_re.format(var_name=var_name)
            # Swap out the pattern match for the regular expression
            # for matching.
            raw_regex = raw_regex.replace(search, replacement)

        regex = re.compile("^" + raw_regex + "$")
        return regex, type_conversions

    def can_handle(self, method, path):
        """
        Determines if the route can handle a specific request.

        Args:
            method (str): The HTTP method coming from the request
            path (str): The URI path coming from the request

        Returns:
            bool: True if this route can handle the request, False otherwise
        """
        if self.method != method:
            return False

        if not self._regex.match(path):
            return False

        return True

    def extract_kwargs(self, path):
        """
        Pulls variables out of the requested URI path.

        Args:
            path (str): The URI path coming from the request

        Returns:
            dict: A dictionary of the variable names from the path &
                converted data found for them. Empty dict if no variables
                were present.
        """
        matches = self._regex.match(path)

        if matches:
            return self.convert_types(matches.groupdict())

        return {}

    def convert_types(self, matches):
        """
        Takes raw matched from requested URI path & converts the data to
        their proper type.

        Args:
            matches (dict): The variable names & the *string* data found
                for them from the URI path.

        Returns:
            dict: The converted data
        """
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
    """
    An orchestration object that handles routing & request processing.

    Args:
        debug (bool): Allows for controlling a debugging mode.
    """

    def __init__(self, debug=False):
        self._routes = []
        self.debug = debug
        self.log = self.get_log()

    def get_log(self):
        """
        Returns a `logging.Logger` instance.

        By default, we return the `itty3` module-level logger. Users are
        free to override this to meet their needs.

        Returns:
            logging.Logger: The module-level logger
        """
        return log

    def __call__(self, environ, start_response):
        # Allows providing the `App` instance as the WSGI handler to
        # many WSGI servers.
        return self.process_request(environ, start_response)

    def add_route(self, method, path, func):
        """
        Adds a given HTTP method, URI path & view to the routing.

        Args:
            method (str): The HTTP method to handle
            path (str): The URI path to handle
            func (callable): The view function to process a matching request
        """
        route = Route(method, path, func)
        self._routes.append(route)
        self.log.debug("Added {} - {}".format(route, func.__name__))

    def find_route(self, method, path):
        """
        Determines the routing offset for a given HTTP method & URI path.

        Args:
            method (str): The HTTP method to handle
            path (str): The URI path to handle

        Returns:
            int: The offset of the matching route

        Raises:
            RouteNotFound: If a matching route is not found
        """
        for offset, route in enumerate(self._routes):
            if route.method == method:
                if route.path == path:
                    return offset

        raise RouteNotFound()

    def remove_route(self, method, path):
        """
        Removes a route from the routing.

        Args:
            method (str): The HTTP method to handle
            path (str): The URI path to handle
        """
        try:
            offset = self.find_route(method, path)
            old_route = self._routes.pop(offset)
            self.log.debug("Removed {}".format(old_route))
        except RouteNotFound:
            pass

    def render(
        self, request, body, status_code=200, content_type=HTML, headers=None,
    ):
        """
        A convenience method for creating a `HttpResponse` object.

        Args:
            request (HttpRequest): The request being handled
            body (str): The body of the response
            status_code (int, Optional): The HTTP status to return. Defaults
                to `200`.
            content_type (str, Optional): The `Content-Type` header to return
                with the response. Defaults to `text/html`.
            headers (dict, Optional): The HTTP headers to include on the
                response. Defaults to empty headers.

        Returns:
            HttpResponse: The populated response object
        """
        return HttpResponse(
            body=body,
            status_code=status_code,
            headers=headers,
            content_type=content_type,
        )

    def render_json(
        self, request, data, status_code=200, content_type=JSON, headers=None,
    ):
        """
        A convenience method for creating a JSON `HttpResponse` object.

        Args:
            request (HttpRequest): The request being handled
            data (dict/list): The Python data structure to be encoded as JSON
            status_code (int, Optional): The HTTP status to return. Defaults
                to `200`.
            content_type (str, Optional): The `Content-Type` header to return
                with the response. Defaults to `text/html`.
            headers (dict, Optional): The HTTP headers to include on the
                response. Defaults to empty headers.

        Returns:
            HttpResponse: The populated response object
        """
        kwargs = {}

        if self.debug:
            kwargs["indent"] = 4

        return self.render(
            request,
            json.dumps(data, **kwargs),
            status_code=status_code,
            content_type=content_type,
            headers=headers,
        )

    def redirect(self, request, url, permanent=False):
        """
        A convenience function for supplying a HTTP redirect.

        Args:
            request (HttpRequest): The request being handled
            url (str): A path or full URL to redirect the user to
            permanent (bool, Optional): Whether the redirect should be
                considered permanent or not. Defaults to `False` (temporary
                redirect).

        Returns:
            HttpResponse: The populated response object
        """
        status_code = 302

        if permanent:
            status_code = 301

        return self.render(
            request,
            body="",
            headers={"Location": url},
            status_code=status_code,
            content_type=PLAIN,
        )

    def error_404(self, request):
        """
        Generates a 404 page for when something isn't found.

        Exposed to allow for custom 404 pages. **Care** should be taken when
        overriding this function, as it is used internally by the routing
        & Python errors bubbling from within can break the server.

        Args:
            request (HttpRequest): The request being handled

        Returns:
            HttpResponse: The populated response object
        """
        return self.render(request, "Not Found", status_code=404)

    def error_500(self, request):
        """
        Generates a 500 page for when something is broken.

        Exposed to allow for custom 500 pages. **Care** should be taken when
        overriding this function, as it is used internally by the routing
        & Python errors bubbling from within can break the server.

        Args:
            request (HttpRequest): The request being handled

        Returns:
            HttpResponse: The populated response object
        """
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
        """
        A convenience decorator for adding a view that processes a `GET`
        request to routing.

        Example::

            app = itty3.App()

            @app.get("/blog/<slug:post_slug>/")
            def post_detail(request, post_slug):
                ...

        Args:
            path (str): The URI path to handle
        """
        return self._add_view(GET, path)

    def post(self, path):
        """
        A convenience decorator for adding a view that processes a `POST`
        request to routing.

        Example::

            app = itty3.App()

            @app.post("/blog/create/")
            def create_post(request):
                ...

        Args:
            path (str): The URI path to handle
        """
        return self._add_view(POST, path)

    def put(self, path):
        """
        A convenience decorator for adding a view that processes a `PUT`
        request to routing.

        Example::

            app = itty3.App()

            @app.put("/blog/<slug:post_slug>/")
            def update_post(request, post_slug):
                ...

        Args:
            path (str): The URI path to handle
        """
        return self._add_view(PUT, path)

    def delete(self, path):
        """
        A convenience decorator for adding a view that processes a `DELETE`
        request to routing.

        Example::

            app = itty3.App()

            @app.delete("/blog/<slug:post_slug>/")
            def delete_post(request, post_slug):
                ...

        Args:
            path (str): The URI path to handle
        """
        return self._add_view(DELETE, path)

    def patch(self, path):
        """
        A convenience decorator for adding a view that processes a `PATCH`
        (partial update) request to routing.

        Example::

            app = itty3.App()

            @app.patch("/blog/bulk/")
            def bulk_post(request):
                ...

        Args:
            path (str): The URI path to handle
        """
        return self._add_view(PATCH, path)

    def create_request(self, environ):
        """
        Given a WSGI environment, creates a `HttpRequest` object.

        Args:
            environ (dict-alike): The environment data coming from the WSGI
                server, including request information.

        Returns:
            HttpRequest: A built request object
        """
        self.log.debug("Received environ {}".format(environ))
        return HttpRequest.from_wsgi(environ)

    def process_request(self, environ, start_response):
        """
        Processes a specific WSGI request.

        This kicks off routing & attempts to find a route matching the
        requested HTTP method & URI path.

        If found, the view associated with the route is called, optionally
        with the parameters from the URI. The resulting `HttpResponse`
        then performs the actions to write the response to the server.

        If not found, `App.error_404` is called to produce a 404 page.

        If an unhandled exception occurs, `App.error_500` is called to
        produce a 500 page.

        Args:
            environ (dict-alike): The environment data coming from the WSGI
                server, including request information.
            start_response (callable): The function/callable to execute when
                beginning a response.

        Returns:
            iterable: The body iterable for the WSGI server
        """
        request = self.create_request(environ)
        self.log.debug(
            "Started processing request for {} {}...".format(
                request.method, request.path
            )
        )
        resp = None

        try:
            for route in self._routes:
                if not route.can_handle(request.method, request.path):
                    continue

                # We have a route that can handle the method & path!
                # Call the view function!
                try:
                    self.log.debug(
                        "Route {} will handle {} {}...".format(
                            route, request.method, request.raw_uri
                        )
                    )
                    kwargs = route.extract_kwargs(request.path)
                    self.log.debug(
                        "Calling {} with arguments {}".format(
                            route.func.__name__, kwargs
                        )
                    )
                    resp = route.func(request, **kwargs)
                    break
                except Exception:
                    self.log.exception(
                        "View {} raised an exception!".format(
                            route.func.__name__
                        )
                    )

                    if self.debug:
                        raise

                    resp = self.error_500(request)
                    break

            if not resp:
                raise RouteNotFound("No view found to handle method/path")
        except RouteNotFound:
            self.log.debug("No route matched. Returning a 404...")
            resp = self.error_404(request)

        if not resp:
            self.log.debug("No response returned by view. Returning a 500...")
            resp = self.error_500(request)

        self.log.info(
            '"{}" {}'.format(request.get_status_line(), resp.status_code)
        )
        resp.start_response = start_response
        return resp.write()

    def reset_logging(self, level=logging.INFO):
        """
        A method for controlling how `App.run` does logging.

        Disables `wsgiref`'s default "logging" to `stderr` & replaces it
        with `itty3`-specific logging.

        Args:
            level (int, Optional): The `logging.LEVEL` you'd like to have
                output. Default is `logging.INFO`.

        Returns:
            wsgiref.WSGIRequestHandler: The handler class to be used.
                Defaults to a custom `NoStdErrHandler` class.
        """
        from wsgiref.simple_server import WSGIRequestHandler

        # Disable the vanilla wsgiref logging & enable itty3's logging.
        # We don't do this by default at the top of the module, because it
        # should be the user's choice how logging happens.
        class NoStdErrHandler(WSGIRequestHandler):
            def log_message(self, *args, **kwargs):
                pass

        self.log.removeHandler(null_handler)
        default_format = logging.Formatter(
            "%(asctime)s %(name)s %(levelname)s %(message)s"
        )
        stdout_handler = logging.StreamHandler()
        stdout_handler.setFormatter(default_format)
        self.log.addHandler(stdout_handler)
        self.log.setLevel(level)
        return NoStdErrHandler

    def run(self, addr="127.0.0.1", port=8000, debug=None):
        """
        An included development/debugging server for running the `App`
        itself.

        Runs indefinitely. Use `Ctrl+C` or a similar process killing method
        to exit the server.

        Args:
            addr (str, Optional): The address to bind to. Defaults to
                `127.0.0.1`.
            port (int, Optional): The port to bind to. Defaults to `8000`.
            debug (bool, Optional): Whether the server should be run in a
                debugging mode. If provided, this overrides the `App.debug`
                set during initialization.
        """
        import sys
        from wsgiref.simple_server import make_server

        handler = self.reset_logging()

        if self.debug is not None:
            self.debug = bool(debug)

        httpd = make_server(
            addr, port, self.process_request, handler_class=handler
        )

        server_msg = "itty3 {}: Now serving requests at http://{}:{}..."
        self.log.info(server_msg.format(get_version(full=True), addr, port))

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            sys.exit(1)
