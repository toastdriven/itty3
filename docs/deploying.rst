.. _deploying:

===================
Deploying ``itty3``
===================

Deployment Checklist
====================

* Ensure ``App.debug`` is set to ``False``
* Use a proper WSGI server
* Check your 404 & 500 pages to ensure no data is leaking
* Set up static asset serving

Managing ``App.debug``
======================

A solid way to manage the ``App.debug`` option is to rely on
environment-based configuration.::

    import os

    import itty3

    # Rely on environment variables to set `debug`.
    app = itty3.App(
        debug=bool(os.environ.get("APP_DEBUG", False))
    )

This allows your code to automatically deploy to new environments (such as
production) with ``debug=False``. For local development, you can export
the environment variable to turn debug back on.::

    $ export APP_DEBUG=1
    $ python app.py

Use A Proper WSGI Server
========================

While the built-in ``wsgiref`` server is convenient, it's not particularly
feature-rich or configurable. Some good production-ready alternatives
include:

* Gunicorn_
* Bjoern_
* uWSGI_
* CherryPy_
* gevent_
* Twisted_

All are good options, boasting good speed/compliance/configuration across
the board. You can't really go wrong, so experiment & find the one you like
best.

The author has the most experience with Gunicorn_, so example configuration
to accommodate that follows::

    # gunicorn.conf
    import multiprocessing

    bind = "127.0.0.1:8000"
    workers = multiprocessing.cpu_count() * 2 + 1
    daemon = True
    reload = False
    max_requests = 1000
    user = "<a-configured-non-root-user>"
    # group = "<an-optional-group>"

Then running the daemon with::

    $ gunicorn -c gunicorn.conf myapp:app

It's important to note that this runs ``gunicorn`` still only on the
localhost. It's generally advised to put a reverse proxy or similar in
front of your WSGI workers.

As an example, here's an nginx_ setup for proxying to `Gunicorn`_::

    server {
        listen 80;
        server_name example.org;
        access_log  /var/log/nginx/access.log;

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }

.. _Gunicorn: https://gunicorn.org/
.. _Bjoern: https://github.com/jonashaag/bjoern
.. _uWSGI: https://uwsgi-docs.readthedocs.io/en/latest/
.. _CherryPy: https://cherrypy.org/
.. _gevent: http://www.gevent.org/
.. _Twisted: https://twistedmatrix.com/trac/
.. _nginx: http://nginx.org/
