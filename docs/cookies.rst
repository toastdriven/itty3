.. _cookies:

=======
Cookies
=======

The nature of HTTP is **state-less** requests. However, this can make
user-specific behaviors difficult (without endlessly prompting the user).

A solution to this problem are `HTTP Cookies`_. Cookies provide a way to share
information between requests.

``itty3`` includes support for both sending & receiving cookies. We'll be
working with the following baseline code::

    import itty3


    app = itty3.App()


    @app.get("/")
    def greet_user(req):
        return app.render(req, "Hello, user!")

    @app.get("/set/")
    def set_username(req):
        username = req.GET.get("username", "unknown")
        return app.redirect("/")


    if __name__ == "__main__":
        app.run()


Setting Cookies
===============

Right now, that ``set_username`` function doesn't do a whole lot. Sure, the
user can provide their username via ``/set/?username=daniel``, but it only
lives for the life of that request/response cycle.

Once they're redirected back to ``/``, the ``username`` is gone. But we
can store this value in a cookie to make it persist...

Since cookies are a (relatively) more advanced concept, we'll be bypassing
the typical ``App.render`` & ``App.redirect`` shortcuts in favor of working
with ``itty3.HttpResponse`` directly. Let's change up the ``set_username``
code::

    @app.get("/set/")
    def set_username(req):
        username = req.GET.get("username", "unknown")

        # First, we manually create the redirect response.
        resp = itty3.HttpResponse(
            body="",
            headers={"Location": "/"},
            status_code=302,
        )

        # Now, set the `username` in the cookies!
        resp.set_cookie("username", username)

        # Don't forget to return that `resp` at the end!
        return resp

Now when the user hits the ``/set/`` URL & provides a username, that
information is persisted (by their browser) & sent with all following
requests.

On their next request (in this case, to ``/``), their browser will provide
the ``Cookie:`` header with their username filled in.

.. note:: This code is for demonstration & display purposes. Cookies are
    **editable** by the user, so never trust the input & blindly look up
    records using the cookies' data.

    This is a form of session stealing attack, made even easier by being
    plain text of a non-changing value!

    Using the concept of a session (or signed cookies), as well as
    verification checks, are the best way to prevent such attacks. This
    ``cookie`` support enables such things, but are beyond the scope of
    this guide.

Lastly, you can make as many calls to ``HttpResponse.set_cookie`` as you
like. So if multiple cookies need to be set/updated, call it multiple times,
once per cookie.

Reading Cookies
===============

Unfortunately, while we've stored the user's data, we're not doing anything
with it. Let's fix that & give the user a proper greeting::

    @app.get("/")
    def greet_user(req):
        # Set up a default.
        username = "unknown"

        # `req.COOKIES` is a `dict` with all the key/value pairs of
        # cookie data.
        if "username" in req.COOKIES:
            username = req.COOKIES["username"]

        body = "Hello, {}!".format(username)
        return app.render(req, body)

Now, when the user hits the ``/`` URL, they should be greeted by their
username!

Cookie Expiration
=================

This is all well & good, until the user closes their browser. When that
happens, then they open the browser again & go back to ``/``, they're
greeted with ``Hello, unknown!`` again!

What happened?!!

The problem is that our use of ``HttpResponse.set_cookie`` doesn't specify
an expiration. Because nothing is set, the browser automatically deletes the
cookies upon closing.

We can fix this easily enough, with one of two options: ``max_age`` or
``expires``. ``max_age`` lets you specify the number of seconds until the
cookie expires, while ``expires`` lets you set a specific date/time for
the expiration.

To use ``max_age``::

    @app.get("/set/")
    def set_username(req):
        username = req.GET.get("username", "unknown")
        resp = itty3.HttpResponse(
            body="",
            headers={"Location": "/"},
            status_code=302,
        )

        # Here's the change! Let's expire the cookie in 2 weeks time:
        # (60 sec/min * 60 min/hr * 24 hr/day * 7 days/week * 2 weeks)
        two_weeks = 60 * 60 * 24 * 7 * 2
        resp.set_cookie("username", username, max_age=two_weeks)

        return resp

To use ``expires``::

    # Add the import at the top!
    import datetime

    # ...then...

    @app.get("/set/")
    def set_username(req):
        username = req.GET.get("username", "unknown")
        resp = itty3.HttpResponse(
            body="",
            headers={"Location": "/"},
            status_code=302,
        )

        # Here's the change! Let's expire the cookie in 2 weeks time:
        two_weeks = datetime.date.today() + datetime.timedelta(weeks=2)
        resp.set_cookie("username", username, expires=two_weeks)

        return resp

Either way, no matter what the user does, that cookie will last for two
weeks.

But what if we want to make it go away sooner?

Deleting Cookies
================

Let's simulate a "logout" & make sure the user's ``username`` cookie goes
away **now**, rather than in two weeks time...::

    # Add a new function.
    @app.get("/logout/")
    def logout(req):
        resp = itty3.HttpResponse(
            body="",
            headers={"Location": "/"},
            status_code=302,
        )

        # All we need to provide is the key.
        resp.delete_cookie("username")

        return resp

After visiting ``/logout/`` & returning to ``/``, the user is back to being
unknown.

Other Options
=============

There are other, more advanced behaviors also possible via ``set_cookie``:

* ``path``: The path the cookie is valid for. Default is ``"/"``.
* ``domain``: The domain the cookie is valid for. Default is only the domain
  that set it.
* ``secure``: If the cookie should only be served by HTTPS. Default is
  ``False``.
* ``httponly``: If ``True``, prevents the cookie from being provided to
  Javascript requests. Default is `False`.
* ``samesite``: How the cookie should behave under cross-site requests.
  Options are ``itty3.SAME_SITE_NONE``, ``itty3.SAME_SITE_LAX``, and
  ``itty3.SAME_SITE_STRICT``. Default is ``itty3.SAME_SITE_NONE``.
  This is only available for Python 3.8+.


.. _`HTTP Cookies`: https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies
