.. _extending:

===================
Extending ``itty3``
===================

``itty3`` is designed to be streamlined & simple to use out of the box.
However, it's relatively easy to customize as well.

Custom ``HttpResponse``
=======================

In normal usage, ``app.render(...)`` is simply a shortcut/convenience
method for constructing an ``itty3.HttpResponse`` object. There's
nothing extraordinary about these instances, so you can make them yourself
if you prefer::

    import pyyaml

    @app.get("/whatev/")
    def whatev(request):
        data = {
            "greeting": "Hello",
            "noun": "world",
            "punctuation": "!",
        }
        return itty3.HttpResponse(
            body=pyyaml.dump(data)
            content_type="text/yaml"
        )

Or even subclass it to "bake in" complex behavior::

    class YAMLResponse(itty3.HttpResponse):
        def __init__(self, data, **kwargs):
            body = pyyaml.dump(data)
            kwargs["content_type"] = "text/yaml"
            super().__init__(body, **kwargs)


    @app.get("/whatev/")
    def whatev(request):
        data = {
            "greeting": "Hello",
            "noun": "world",
            "punctuation": "!",
        }
        return YAMLResponse(data)

And you can override/extend ``App.render`` if you want to automatically
use your new subclass::

    class MyApp(itty3.App):
        def render(self, request, *args, **kwargs):
            # Because of the mismatch in signatures (`body` vs `data`), this
            # may not work perfectly in all situations.
            return YAMLResponse(*args, **kwargs)

Custom ``HttpRequest``
======================

As with ``HttpResponse``, ``itty3.HttpRequest`` isn't particularly
special. The only interesting/tricky part is automatically constructed by
``App.create_request``, so you'll need to override that method when creating
a subclass.

For instance, if you wanted to identify a request was secure in a different
way (e.g. verifying a nonce was present in headers)::

    class NonceHttpRequest(itty3.HttpRequest):
        def is_secure(self):
            if "X-Secure-Nonce" not in self.headers:
                return False

            nonce = self.headers["X-Secure-Nonce"]
            # Check a DB for that nonce within a time range.

            if not verified:
                return False

            # The request is good. Carry on.
            return True

You could then tell your ``App`` to always use this subclass with::

    class SuperSecureApp(itty3.App):
        def create_request(self, environ):
            return NonceHttpRequest.from_wsgi(environ)

Different Routing
=================

If ``itty3``'s routing doesn't suit you, you can even define your own
variant of ``Route``. As long as it conforms to a bit of expected API
& with a couple minor tweaks to ``App``...::

    # We want to support routes like:
    #
    #     "/app/:id/:title"
    #
    # ...and attempt automatic conversion of types.
    # This is a naive implementation of that.

    class SimpleRoute(object):
        def __init__(self, method, path, func):
            self.method = method
            self.path = path
            self.func = func

        def split_uri(self, path):
            return path.split("/")

        def can_handle(self, method, path):
            if not self.method == method:
                return False

            internal_path_bits = self.split_uri(self.path)
            external_path_bits = self.split_uri(path)

            if len(internal_path_bits) != len(external_path_bits):
                # Without even iterating, we know it's not right.
                return False

            matched = True

            for offset, bit in enumerate(internal_path_bits):
                if not bit.startswith(":"):
                    # We're looking for a non-variable, exact match.
                    if bit != external_path_bits[offset]:
                        matched = False
                        break
                else:
                    # It's a variable. Carry on.
                    continue

            return matched

        def extract_kwargs(self, path):
            # This only gets called if the route can handle the URI.
            # So we'll take a shortcut or two here for brevity.
            internal_path_bits = self.split_uri(self.path)
            external_path_bits = self.split_uri(path)

            matches = {}

            for offset, bit in enumerate(internal_path_bits):
                if not bit.startswith(":"):
                    # It's not a variable, we don't care.
                    continue

                # It's a variable. Slice off the colon.
                var_name = bit[1:]

                # Extract it from the actual URI.
                value = external_path_bits[offset]

                # Try to convert the type.
                try:
                    value = int(value)
                except ValueError:
                    pass

                try:
                    value = float(value)
                except ValueError:
                    pass

                if value in ("true", "false"):
                    # Store it as a boolean.
                    value = value == "true"

                # Finally, track what we found.
                matches[var_name] = value

            return matches


    # Now, just override ``App`` to use your new routes.
    class SimpleRoutesApp(itty3.App):
        def add_route(self, method, path, func):
            # We swap in the custom class here.
            route = SimpleRoute(method, path, func)
            self._routes.append(route)
