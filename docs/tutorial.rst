.. _tutorial:

========
Tutorial
========

This guide is aimed at getting started with ``itty3``. You should be at least
basically familiar with Python & HTTP in order to get the most out of this
tutorial.

Installation
============

For most users in a modern Python environment they can control, you'll want
to run::

    $ pip install itty3

Ideally, this should be run within a ``virtualenv``/``pipenv``/similar to
give you some isolation. Installing Python libraries globally is a recipe
for pain & there are many good options out there that are easy/quick to learn
to help you avoid dependency hell.

That said, ``itty3`` is small/minimal by design. The code (minus docstrings
& comments) is less than 1k lines of code. This allows you to embed ``itty3``
directly into your application by copying in ``itty3.py`` (or even within
your app file directly!).

Regardless, ``itty3``'s only dependency is Python 3. It's been tested on
Python 3.7.4+, but may work on older versions.

Finally, you can find the complete source for this tutorial within
the `examples/tutorial_todolist` directory of ``itty3``'s source code.

Starting An App
===============

Once you have installed ``itty3``, the next thing you'll want to do is start
an application file. A good choice for starting out is to create an
empty ``app.py`` file.

You'll start out by importing ``itty3``::

    import itty3

Next, define a module-wide `App` object instance::

    app = itty3.App()

This will allow you start registering "routes", a combination of an HTTP
method, a URI path & a view (a callable function that takes a request &
produces a response).

After that, provide a way for the built-in server code to run your new
``app``. At the bottom of the file, add the following::

    if __name__ == "__main__":
        app.run()

This tells the Python interpreter that, if the file itself is being run by
Python, to execute the code within the ``if`` block. The ``app.run()``
runs the built-in **development** server & starts listening for requests.

Your complete ``app.py`` file should now look like::

    import itty3


    app = itty3.App()


    if __name__ == "__main__":
        app.run()

Now run the server using ``python app.py``. You should get a message about
the server starting & where it'll handle requests at::

    itty3 <version>: Now serving requests at http://127.0.0.1:8000...

You can now go to the browser & hit http://127.0.0.1:8000/ to access the app!

However, because we haven't written any application-specific code, you're
going to get a `404 Not Found` page, which isn't super-useful. Let's fix
that...

Adding Your First View
======================

A "view" function is any callable that can accept a ``request`` object &
produce a ``response`` object for serving back to the user. We don't
need to focus on the details of those for now (more later), so let's just
write a basic index view::

    import itty3


    app = itty3.App()


    # NEW CODE HERE!
    @app.get("/")
    def index(request):
        body = "Hello, world!"
        return app.render(request, body)


    if __name__ == "__main__":
        app.run()

The first line (``@app.get("/")``) is a decorator. That automatically
registers your ``index`` view with the ``app``, telling it that the attached
view can handle an HTTP ``GET`` request at the path ``/``.

The next line (``def index(request):``) declares the callable that is
run when that request is seen. In simple ``itty3`` applications, that's
usually just a plain Python function, but any callable (instance methods,
entire classes, etc.) will work. The only guideline is that it should accept
a ``request`` parameter (a ``itty3.HttpRequest`` object) as the first
positional argument.

We then build a simple string body, just to see a customized result out on
the page.

The final piece is the ``return app.render(request, body)`` line. This builds
and returns a ``HttpResponse`` object, which handles all the details of
serving a proper HTTP response back to the user, including status codes &
headers. ``app.render(...)`` is simply a convenience function for producing
that object.

If you ``Ctrl+C`` the ``python app.py`` & restart it, then hit
http://127.0.0.1:8000/ in your browser, you should now get a simple page
that says ``Hello, world!``.

Hurray! Our first real web response works!

.. note:: You'll note that "render"-ing in the context of ``itty3`` doesn't
    do any templating. ``itty3`` doesn't care how you produce response
    bodies, as long as a string or iterable can be returned.

    This opens a world of options, from reading/returning entire files
    (good for Single-Page Apps), returning serialized data (like JSON, YAML
    or XML), or using your own choice of template language (like ``Jinja2``,
    ``Mako`` or even regular Python format strings).

    The downside is that you need to do a bit more work & make a choice
    around what you want to do. Evaluate your options & choose the one that
    works for you.

Building A TODO List App
========================

Let's step beyond this & start crafting a real interactive app.
We'll build a very basic TODO list application.

.. note:: We're going to use a file-based & JSON setup. This is for
    simplicity in the example code & to avoid further dependencies.

    This is suitable for this toy app, but isn't recommended for production
    unless you know what you're doing. GET YOU AN DATABASE!

We'll leave the beginning code (``import itty3`` & ``app = itty3.App()``) as
well as the ending code (everything after ``if __name__ == "__main__":``)
alone, focusing only on our application code.

We'll make the index view more useful first.

The Index View
--------------

First, let's create a prettier index page. Alongside your ``app.py`` file,
let's create an ``index.html`` file.

Add the following to that new ``index.html`` file::

    <html>
        <head>
            <title>My TODO List</title>
            <style>
                /* Just a quick reset & some basic styles. */
                * { margin: 0; padding: 0; }
                html { background-color: #CCCCCC; text-align: center; }
                body { background-color: #FFFFFF; border-left: 2px solid #999999; border-right: 2px solid #999999; font-family: Helvetica, Arial, sans-serif; font-size: 14px; margin: 0 auto; text-align: left; width: 60%; padding: 40px 20px; }
                h1, h2, h3 { margin: 10px 0px; font-family: Georgia, 'Times New Roman', Times, serif; }
                p { display: block; padding: 10px 0px; }
                ul { display: block; padding: 10px 0px; list-style: none; }
                ul li { border: 1px solid #EEEEEE; padding: 5px; }
                ul li form { display: inline; }
                ul li input { margin: 0px 10px 0px 0px; }
            </style>
        </head>

        <body>
            <header>
                <h1>My TODO List</h1>
            </header>

            <content>
                <ul>
                    <!--
                        We'll manually search/replace this out with string formatting.
                        This is where a real template language would come in handy.
                    -->
                    {{ content }}
                </ul>

                <p>
                    <form method="post" action="/create/">
                        <label for="id_todo">Add TODO:</label>
                        <input type="text" id="id_todo" name="todo">
                        <input type="submit" value="Create">
                    </form>
                </p>
            </content>
        </body>
    </html>

Save the file & close it.

Next, alongside the ``app.py`` & ``index.html`` files, create a
``data.json`` file::

    {
        "items": []
    }

Save the file & close it.

Now go back to ``app.py`` & let's update the ``index`` view to use our
new files::

    # At the top of the file, add:
    import json

    # ...

    # Then update the ``index`` view.
    @app.get("/")
    def index(request):
        # We'll open/read the HTML file.
        with open("index.html") as index_file:
            template = index_file.read()

        # Pull in the JSON data (currently mostly-empty).
        with open("data.json") as data_file:
            data = json.load(data_file)

        content = ""

        # Create the list of TODO items.
        for offset, item in enumerate(data.get("items", [])):
            # Note: This is gross & dangerous! You need to escape your
            # data in a real app to prevent XSS attacks!
            content += "<li>{}</li>".format(item)

        if not content:
            content = "<li>Nothing to do!</li>"

        # Now "template" in the data.
        template = template.replace("{{ content }}", content)

        # Return the response.
        return app.render(request, template)

Restart the server & check http://127.0.0.1:8000/ in your browser. You
should now have some HTML & an empty TODO list!

You can verify things are working by manually changing your ``data.json``
to::

    {
        "items": [
            "Finish TODO list app",
            "Do some gardening",
            "Take a nap"
        ]
    }

Then reloading the page (no server restart needed).


Creating New TODOs View
-----------------------

Now that we can see our TODO list, let's add a way to create new TODO.
We'll be creating a **second** function::

    @app.post("/create/")
    def create_todo(request):
        # Pull in the JSON data (currently mostly-empty).
        with open("data.json") as data_file:
            data = json.load(data_file)

        # Retrieve the new TODO text from the POST'ed data.
        new_todo = request.POST.get("todo", "---").strip()

        # Append it onto the TODO items.
        data["items"].append(new_todo)

        # Write the data back out.
        with open("data.json", "w") as data_file:
            json.dump(data, data_file, indent=4)

        # Finally, redirect back to the main list.
        return app.redirect(request, "/")

We're doing a couple new things here. First, we're using ``@app.post(...)``,
which hooks up a route for an HTTP POST request.

Second, we're making use of ``request.POST``. This is a ``QueryDict``,
a ``dict``-like object that contains all the ``POST``'ed form values.

.. note:: If you're handling JSON or another different request body, you
    should **NOT** use ``request.POST``. Instead, use ``request.body`` &
    manually decode the contents of that string.

Finally, we're using ``app.redirect(...)``, which is a convenience function
for sending an HTTP (temporary) redirect back to the main page. This
triggers a fresh load of the TODO list, including the newly added TODO.

Restart your ``python app.py``, reload in your browser & try creating a new
TODO item.

Aside: Auto-Reloading Server
----------------------------

By now, you may be tired of manually restarting your ``app.py`` server.
To make things a little easier, we'll set up Gunicorn_ to serve our
local traffic.

First, install ``gunicorn``::

    $ pip install gunicorn

Next, instead of running ``python app.py``, we'll run::

    $ gunicorn -w 1 -t 0 --reload app:app

Now, whenever we change our ``app.py`` file, ``gunicorn`` will automatically
reload the code. Now it'll always be serving the current code to our browser.

No more restarts!

.. _Gunicorn: https://gunicorn.org/

Marking TODOs As Done
---------------------

The last bit of our TODO list app is being able to mark a TODO as completed.

First, we'll need to modify our ``index`` view. Find the line::

    content += "<li>{}</li>".format(item)

...and change it to::

    content += '<li><form method="post" action="/done/{offset}/"><input type="submit" value="Complete"></form>{item}</li>'.format(
        offset=offset,
        item=item
    )

We unfortunately need to use ``POST`` here, as HTML forms can't submit
``DELETE`` requests.

.. note:: Yes, there are better ways to handle this form submission.
    Adding some modern JS would be a good exercise for the reader. :)

Finally, we need to add a new view::

    @app.post("/done/<int:offset>/")
    def mark_done(request, offset):
        # Pull in the JSON data (currently mostly-empty).
        with open("data.json") as data_file:
            data = json.load(data_file)

        items = data.get("items", [])

        if offset < 0 or offset >= len(items):
            return app.error_404(request, "Not Found")

        # Move it to "done".
        data.setdefault("done", [])
        data["done"].append(items[offset])

        # Slice out the offset.
        plus_one = offset + 1
        data["items"] = items[:offset] + items[plus_one:]

        # Write the data back out.
        with open("data.json", "w") as data_file:
            json.dump(data, data_file, indent=4)

        # Finally, redirect back to the main list.
        return app.redirect(request, "/")

This is very similar to the ``create_todo`` view, with just a couple
modifications.

First, note that our path is ``/done/<int:offset>/`` & we've added a
``offset`` parameter to the view's function declaration. This lets us
capture data out of the URL & use it in our app.

Next, we use that ``offset`` to check to ensure it's within the bounds
of the ``items``. If not, we call ``app.error_404(...)`` to supply a
``404 Not Found`` response.

We then archive the item to a (potentially new) ``"done"`` key within our
JSON. And then we overwrite the ``items`` with a slice that excludes the
desired offset.

Reload in the browser & give it a spin!


Congratulations!
================

With this, you've built your first working application with ``itty3``.

For more information, you can:

* Refer to the API docs at :doc:`reference/itty3`
* Check out the :ref:`deploying` guide
* Find out how to :ref:`extending`
* Learn how to :ref:`troubleshooting`

Happy developing!
