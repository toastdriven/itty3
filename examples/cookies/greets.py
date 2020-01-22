import itty3


app = itty3.App()


@app.get("/")
def greet_user(req):
    # Set up a default.
    username = "unknown"

    if "username" in req.COOKIES:
        username = req.COOKIES["username"]

    body = "Hello, {}!".format(username)
    return app.render(req, body)


@app.get("/set/")
def set_username(req):
    username = req.GET.get("username", "unknown")

    # First, we manually create the redirect response.
    resp = itty3.HttpResponse(
        body="", headers={"Location": "/"}, status_code=302,
    )

    # Now, set the `username` in the cookies!
    resp.set_cookie("username", username)

    # Don't forget to return that `resp` at the end!
    return resp


@app.get("/logout/")
def logout(req):
    resp = itty3.HttpResponse(
        body="", headers={"Location": "/"}, status_code=302,
    )

    # All we need to provide is the key.
    resp.delete_cookie("username")

    return resp


if __name__ == "__main__":
    app.run()
