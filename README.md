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

## Setup

`pip install itty3` is what most people will want.

That said, `itty3` is completely self-contained to a single file & relies
only on the Python standard library. You can directly copy `itty3.py` into
your project & import it directly!

## Dependencies

* Python 3.7+

## License

New BSD
