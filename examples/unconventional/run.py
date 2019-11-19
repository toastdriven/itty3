"""
This example is all about showing unconventional uses of itty3.

Some things demonstrated:

* Manually instantiating the core objects (like `HttpResponse`)
* Using `App.add_route` instead of the typical `itty3` decorators
* Keeping views in other files
* Manually constructing an `App` out of a subset/superset of views
* Overriding/extending views
* Not using an `app` global object
* Not using `app.run()` to serve traffic

"""
import base64
import itty3

from . import api
from . import webui


USERNAME = "johndoe"
PASSWORD = "hunter2"


def overridden_create_post(request):
    # Check some HTTP Basic Auth for a known user/pass.
    #
    # NOTE: This isn't secure at all over regular HTTP! Add SSL if you deploy
    #     code like this to a production environment!
    #     It's probably also incomplete!
    if "Authorization" not in request.headers:
        return itty3.HttpResponse(request, "", status_code=403)

    # Take the header, base64-decode it & split on the ":".
    raw_auth = request.headers["Authorization"]
    bits = base64.b64decode(raw_auth).split(":", 1)

    # If there aren't enough bits or something is empty, reject.
    if len(bits) < 2 or not bits[0] or not bits[1]:
        return itty3.HttpResponse(request, "", status_code=403)

    # If the credentials don't match, reject.
    if bits[0] != USERNAME or bits[1] != PASSWORD:
        return itty3.HttpResponse(request, "", status_code=403)

    # They're authorized. Let them post.
    return webui.create_post(request)


def application(environ, start_response):
    # `app` isn't a special name, nor does it have to be module-level if
    # you don't want.
    app = itty3.App()

    # Manually register the views.
    # This allows you to create the URL structure & compose a given app
    # differently.
    # Leave views out, change the order they're handled in, add in functions
    # not present in the original `App`, etc.
    app.add_route("GET", "/", webui.index)
    app.add_route("GET", "/api/", api.index)
    app.add_route("POST", "/blog/post/create/", overridden_create_post)

    # Lastly, you can manually call the WSGI handler in `itty3.App`, in case
    # you want to wrap some middleware on it.
    return app.process_request(environ, start_response)
