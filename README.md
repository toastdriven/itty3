# itty3

The itty-bitty Python web framework... **Now Rewritten For Python 3!**

If you're on Python 2, you're looking for
[itty for Python 2](https://github.com/toastdriven/itty) instead...

## Quick Start

```python
import itty3

# Make an app (mostly just for routing & niceties).
app = itty3.App()

# Register your views with the app.
@app.get("/")
def index(request):
    return app.render(request, "Hello, world!")

if __name__ == "__main__":
    # Run a simple WSGI server!
    app.run()
```

## Why?

`itty3` is a micro-framework for serving web traffic. At its `1.0.0`
release, `itty3` weighed in at less than ~1k lines of code.

Granted, it builds on the shoulders of giants, using big chunks of the Python
standard library. But it has **no** other external dependencies!

Reasons for `itty3`:

* Extremely lightweight
* Fast to start working with
* Easy to produce initial/toy services
* Minimal boilerplate
* Useful for places where you can't/don't have a full Python setup
* Useful for including directly, like when you lack permissions
* Works with a variety of WSGI servers, including Gunicorn

If you need to produce a big application, you're probably better off with
[Django](https://djangoproject.com/),
[Flask](https://www.palletsprojects.com/p/flask/), or any of the other
larger/more mature web frameworks. No pressure!

## Setup

`pip install itty3` is what most people will want.

That said, `itty3` is completely self-contained to a single file & relies
only on the Python standard library. You can directly copy `itty3.py` into
your project & import it directly!

## Dependencies

* Python 3.7+

## License

New BSD

## Running Tests

```
$ pip install pytest pytest-cov
$ pytest tests

# For code coverage
$ pytest --cov=itty3 tests
```

## Building Docs

```
$ pip install -r docs/requirements.txt
$ cd docs
$ make html
```
