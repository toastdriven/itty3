.. _philosophy:

==========
Philosophy
==========

The following are the guiding principles around ``itty3``:

What ``itty3`` Is
=================

* Small (ideally, ~1kloc of code or less)
* Self-contained (depends only on the Python stdlib)
* Open (BSD license, baby!)
* Respects HTTP & the Web (all the HTTP verbs, good status codes,
    content-types, etc.)
* Easy to start working with (import ``itty3`` & define some functions)
* Flexible & easy to extend (all code can be used in relative isolation)
* Few to no globals (outside of constants)
* Fast & efficient (within reason/readability)
* Well-tested
* Well-documented
* Unicode everywhere (that we can)

``itty3`` is designed for the sweet spot around creating single-page apps,
small APIs & experiments. The code you produce with ``itty3`` should be
(relatively) easy to migrate to other things (Django, Flask, etc.) when
you've moved beyond ``itty3``'s capabilities.

What ``itty3`` Isn't
====================

* An everything-and-the-kitchen-sink webframework (there are better options)
* Strongly opinionated about tools
    (BYO-database-layer-template-engine-Javascript-framework-etc)
* A perfect solution

``itty3`` won't ever ship with an authentication layer, database engines,
scaffolding, Makefiles (beyond the Sphinx one), etc.

It's designed for the modern Web, so I'm sure there's ancient things that
don't work. Sorrynotsorry.

The Future
==========

There are planned improvements for the future. The `Github Issues`_ for
the project is the most up-to-date source of that information, but generally
speaking:

* Cookie support
* Included example code
* More/better docs
* Maybe file uploads? *Maybe*

.. _`GitHub Issues`: https://github.com/toastdriven/itty3/issues
