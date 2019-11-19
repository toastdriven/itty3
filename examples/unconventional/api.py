import json

import itty3


def api_list(request):
    # We're taking a whole different set of views (an API in this case) &
    # composing it into our main app in `run.py`.
    # Imagine this is doing something interesting.
    data = {
        "posts": [
            {
                "title": "First Post!",
                "content": "I started a blog today like it was 2008.",
            },
        ],
    }
    return itty3.HttpResponse(json.dumps(data), content_type=itty3.JSON)


def unused_api(request, post_id):
    # And in `run.py`, this view isn't even hooked up!
    post = {
        # ...
    }
    return itty3.HttpResponse(json.dumps(post), content_type=itty3.JSON)
