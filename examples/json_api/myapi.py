"""
This app demonstrates a JSON-based API, including a simple OpenAPI
specification for the API.

You can test the POST portion using curl via::

    curl -X POST -d '{"newQuote": "Uh, hi?"}' \
        -H 'Content-Type: application/json' \
        http://127.0.0.1:8000/api/2019-11-18/quotes

"""
import json
import random

import itty3


app = itty3.App()

# Because a proper database would add complexity, we'll just use an
# in-memory list.
#
# Note that this isn't persistent, it's not thread-safe, mutable globals are
# a sign of poor design & it's not a scalable, production-ready thing!
#
# The point here is demonstrating JSON & HTTP.
QUOTES = [
    "A rose, by any other name, would smell as sweet.",
    (
        "To be or not to be, that is the question. Whether 'tis nobler in "
        "the mind to suffer the slings and arrows of outrageous fortune..."
    ),
    "But soft, what light through yonder window breaks?",
    "Let them eat cake.",
    "There is no reason for any individual to have a computer in his home.",
]


@app.get("/api/2019-11-18/")
def schema(request):
    # In the real world, you'd probably want to pull out your schema.
    # But since this is such a small API, we'll just inline it here.
    data = {
        "openapi": "3.0.0",
        "info": {
            "title": "A JSON API in itty3",
            "description": "Just a simple demonstration.",
            # CalVer
            "version": "2019-11-18",
        },
        "servers": [
            {
                "url": "http://127.0.0.1/api/2019-11-18/",
                "description": "Local development",
            }
        ],
        "paths": {
            "/quotes": {
                "get": {
                    "summary": "",
                    "description": "",
                    "responses": {
                        "200": {
                            "description": "",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {"type": "string",},
                                    },
                                },
                            },
                        },
                    },
                },
                "post": {
                    "summary": "Adds a new quote",
                    "description": "...",
                    "requestBody": {
                        "description": "A new quote to add",
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "newQuote": {"type": "string",},
                                    },
                                    "additionalProperties": False,
                                },
                            },
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "bool",},
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            "/quotes/random": {
                "get": {
                    "summary": "Fetches a random quote",
                    "description": "What it says on the tin.",
                    "responses": {
                        "200": {
                            "description": "The randomly-selected quote",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "quote": {"type": "string",},
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
    }
    return app.render_json(request, data)


# You can safely stack decorators, even with different URLs!
# You must handle them appropriately in the view's body though...
@app.post("/api/2019-11-18/quotes")
@app.get("/api/2019-11-18/quotes")
def quote_list(request):
    if request.method == itty3.POST:
        # We've got a `POST`, meaning a new quote to add.
        # Default to a failed request body & change it only if things
        # work out.
        data = {
            "success": False,
        }

        try:
            # Since the `POST`'d body is in JSON, we'll need to decode it.
            body = request.json()
            new_quote = body.get("newQuote")

            if new_quote:
                QUOTES.append(new_quote)
                data["success"] = True
        except json.decoder.JSONDecodeError:
            pass

        return app.render_json(request, data)

    # Otherwise, we process the `GET` as normal.
    return app.render_json(request, QUOTES)


@app.get("/api/2019-11-18/quotes/random")
def random_quote(request):
    quote = random.choices(QUOTES)
    return app.render_json(request, {"quote": quote})


if __name__ == "__main__":
    app.run(debug=True)
