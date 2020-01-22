.. _static_files:

=====================
Serving Static Assets
=====================

Web pages & web apps are usually made up of more than just HTML or JSON.
``itty3`` ships with built-in support for serving up static assets, such as:
CSS, images, Javascript, etc.

.. note:: Serving media in this way is really only suitable for
    **development**. The drawbacks outside of development are numerous:

    * It hasn't been vetted for security
    * It's slower than something like nginx/S3/etc.
    * It'll tie up your server process(es)

    Please don't do this in production & take the time to setup your media
    the Right Way™.

Setup
=====

Setting up your app to serve static assets is easy. First, create a directory
for the assets alongside your application code.::

    $ ls
    app.py
    $ mkdir static_media

The name of the directory isn't very important, so feel free to use what
works for you.

Next, create some assets::

    # We create a nested structure inside, but there are no requirements.
    # You can have a completely flat directory if you like, or go
    # full Java & have an extremely deeply nested set of directories.
    $ mkdir -p static_media/css
    $ mkdir -p static_media/js

    $ touch static_media/css/default.css
    $ touch static_media/js/index.js

    # Dump some simple contents into them.
    $ echo "* { margin: 0; padding: 0}" >> static_media/css/default.css
    $ echo "window.alert('Yo!');" >> static_media/js/index.js

Finally, go back to your app's code. Change your ``app.run(...)`` to::

    if __name__ == "__main__":
        app.run(
            # Any other args you might have here, then...
            static_url_path="/static/",
            static_root="static_media",
        )

``static_root`` is the **file-system path** to the directory we created
above. This tells the `itty3.App`` where to look for the assets.

The ``static_url_path``, on the other hand, sets up a special route in the
``app`` for serving static media. Anything that starts with that path
will be served by the ``render_static`` handler.

So in this case, the following URLs will now serve the assets we created:

* ``/static/css/default.css``
* ``/static/js/index.js``

Run your app & give it a try!
