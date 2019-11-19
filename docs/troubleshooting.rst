.. _troubleshooting:

===============
Troubleshooting
===============

"My server isn't responding to traffic!"
========================================

This is commonly because of the host address ``itty3`` is bound to. By
default, the code & docs default to ``127.0.0.1`` ("localhost"). This
prevents your application server from responding to requests from the
outside world.

You'll likely need to change the address to something like ``0.0.0.0``
("respond to requests from any host") or have a server that sits in front
of your application server (like Nginx or similar).

A way to check if the application server is responding is to be on the server
& issue a ``curl`` command to ``http://127.0.0.1:<port-goes-here>/``. If
it responds as expected, it's likely an address (or port) issue.

"I'm getting a 500 error and don't know what's wrong!"
======================================================

When ``App.debug=False`` (the default), ``itty3`` suppresses exceptions &
simply returns a static 500 error page.

You'll want to set ``App.debug`` to ``True``, either via:

* the initialization - ``itty3.App(debug=True)``
* setting the attribute on the ``App`` itself - ``app.debug = True``
* the ``app.run(debug=True)`` if you're using that

When you do this, a traceback will be provided in the console output for
the server. You can use this to debug your issue.

"The traceback of my error isn't enough!"
=========================================

Other frameworks provide more comprehensive or even interactive debug
pages. While nice, these come at a complexity & security cost.

Being minimalist, the next best way to figure out what's wrong in your
``itty3`` application is through the use of an interactive debugger, such
as pdb_.

You can drop a ``import pdb; pdb.set_trace()`` pretty much anywhere in your
code, step through instructions & examine variable contents.

There are other options, such as ``wdb``, ``pudb`` or even in-editor
interactive debuggers! Experiment & find one you like.

Experience with an interactive debugger is an invaluable skillset to have
& well worth the time you invest into it.

.. _pdb: https://docs.python.org/3/library/pdb.html
