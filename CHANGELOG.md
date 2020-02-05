# CHANGELOG


## 1.1.2-develop

TBD


## 1.1.1

Bugfix release.

### Bugfixes

* Altered the `static` handler provide `Content-Length` as a string, which
  avoids crashing under `wsgiref`


## 1.1.0

### Features

* Added static assets support for development
* Added cookies support

### Documentation

* Documentation for serving static assets
* Documentation for using cookies


## 1.0.0

Whoo! :tada:

After over 10 years since the initial `itty` (Python 2) [commit](https://github.com/toastdriven/itty/commit/e8ec06096ed70179a7d4c0fea89ac95246604c3b),
I finally did the re-write I've been wanting to do for 4+ years.

`itty3` has reached `1.0.0` status & is in active production use. It is not
a perfect 1:1 match for the original codebase (a couple missing features),
but it has been completely rewritten for Python 3. It also features:

* A more extensible codebase & less global-dependence
* Better WSGI server compatibility
* Documentation!
* 100% test coverage!

It's not an end-all Python web framework (nor should it be), but if you need
to solve a small problem fast, it'd be great if you considered using `itty3`!

Enjoy!


### Features

* Added logging support

  `itty3` now ships with support for Python's `logging` module. By default,
  this is configured to ship logs to a `NullHandler` (no logs), unless you're
  using `App.run`.

  You can customize/extend this using all the typical `logging` configuration
  options, including adding your own handlers, changing the logging level,
  etc.

  If you need to further customize things, `App.get_log` and
  `App.reset_logging` are the methods you'll want to look at.

### Bugfixes

* Added more `str` methods to all the classes missing them


## 1.0.0-alpha2

### Features

* Added runnable examples

    * `examples/tutorial_todolist` - The full code of the tutorial
    * `examples/json_api` - A simple JSON-based API
    * `examples/us_db_templates` - Demonstrates how to incorporate database &
      template libraries into `itty3`. In this case, `peewee` & `Jinja2`
    * `examples/unconventional` - Demonstrates some unconventional usages
      of `itty3`.

* Added `App.render_json` as a convenience/shortcut for returning JSON
  responses

### Documentation

* Added deployment docs
* Added docs about test coverage
* Added docs on how to extend `itty3`

### Bugfixes

* Added support for Read The Docs
* Added support for GitHub templates
* Fixed route regular expressions to be more consistent with the captured
  types
* Removed an incorrect package classifiers (oops!)


## 1.0.0-alpha

The initial version of `itty3`.

Ships with:

* GET/POST/PUT/DELETE/PATCH
* HTML/JSON
* Ajax support
* Built-in development server
* Support for other WSGI servers, like Gunicorn
* Full test suite
* Documentation
