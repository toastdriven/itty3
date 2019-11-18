"""
The complete, runnable source code from the `docs/tutorial.rst` documentation.
"""
import json

import itty3


app = itty3.App(debug=True)


@app.get("/")
def index(request):
    # We'll open/read the HTML file.
    with open("index.html") as index_file:
        template = index_file.read()

    # Pull in the JSON data (currently mostly-empty).
    with open("data.json") as data_file:
        data = json.load(data_file)

    content = ""

    # Create the list of TODO items.
    for offset, item in enumerate(data.get("items", [])):
        # Note: This is gross & dangerous! You need to escape your
        # data in a real app to prevent XSS attacks!
        content += '<li><form method="post" action="/done/{offset}/"><input type="submit" value="Complete"></form>{item}</li>'.format(
            offset=offset, item=item
        )

    if not content:
        content = "<li>Nothing to do!</li>"

    # Now "template" in the data.
    template = template.replace("{{ content }}", content)

    # Return the response.
    return app.render(request, template)


@app.post("/create/")
def create_todo(request):
    # Pull in the JSON data (currently mostly-empty).
    with open("data.json") as data_file:
        data = json.load(data_file)

    # Retrieve the new TODO text from the POST'ed data.
    new_todo = request.POST.get("todo", "---").strip()

    # Append it onto the TODO items.
    data["items"].append(new_todo)

    # Write the data back out.
    with open("data.json", "w") as data_file:
        json.dump(data, data_file, indent=4)

    # Finally, redirect back to the main list.
    return app.redirect(request, "/")


@app.post("/done/<int:offset>/")
def mark_done(request, offset):
    # Pull in the JSON data (currently mostly-empty).
    with open("data.json") as data_file:
        data = json.load(data_file)

    items = data.get("items", [])

    if offset < 0 or offset >= len(items):
        return app.error_404(request, "Not Found")

    # Move it to "done".
    data.setdefault("done", [])
    data["done"].append(items[offset])

    # Slice out the offset.
    plus_one = offset + 1
    data["items"] = items[:offset] + items[plus_one:]

    # Write the data back out.
    with open("data.json", "w") as data_file:
        json.dump(data, data_file, indent=4)

    # Finally, redirect back to the main list.
    return app.redirect(request, "/")


if __name__ == "__main__":
    app.run()
