import itty3


# Note: The typical `itty3` decorators aren't present!
def index(request):
    # You can imagine the database lookup & template rendering here.
    posts = "<p>No posts yet.</p>"
    # You can directly instantiate responses if you don't want to use
    # the `app` module-level object or `app.render` specifically.
    return itty3.HttpResponse(posts)


def create_post(request):
    # This is unauthorized. Maybe for development or different auth in
    # production.
    # Regardless, some HTTP Basic Auth is added in `run.py`.
    if request.method != itty3.POST:
        return itty3.HttpResponse(request, "Nerp.", status_code=400)

    title = request.POST.get("title", "")
    content = request.POST.get("content", "")

    # Imagine putting it in a database here.

    return itty3.HttpResponse("", status_code=302, headers={"Location": "/"})
