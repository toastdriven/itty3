"""
This one needs its own `virtualenv` (or similar).

Install the `./requirements.txt` to make it run.

Start a Python shell, then create the DB:

    >>> import imakemyownchoices as immoc
    >>> immoc.db.connect()
    >>> immoc.db.create_tables([immoc.App])
    >>> immoc.App.create(
    ...     app_id=str(uuid.uuid4()),
    ...     title="Complacent Lizards",
    ... )
    >>> immoc.App.create(
    ...     app_id=str(uuid.uuid4()),
    ...     title="Geometry Minor Conflicts",
    ... )
    >>> immoc.App.create(
    ...     app_id=str(uuid.uuid4()),
    ...     title="Fifthnite",
    ... )
    >>> immoc.db.close()

You can now run the app: `$ python imakemyownchoices.py`.

"""
import datetime

import itty3
import jinja2
import peewee


webapp = itty3.App()
db = peewee.SqliteDatabase("apps.db")
env = jinja2.Environment(
    loader=jinja2.FileSystemLoader("./templates", followlinks=True),
    autoescape=jinja2.select_autoescape(["html"]),
)


# Peewee Models
class App(peewee.Model):
    app_id = peewee.CharField(primary_key=True, unique=True)
    title = peewee.CharField()
    created = peewee.DateTimeField(default=datetime.datetime.utcnow)

    class Meta:
        database = db


@webapp.get("/apps/")
def app_list(request):
    with db:
        apps = App.select()
        template = env.get_template("list.html")
        return webapp.render(request, template.render(apps=apps))


@webapp.get("/apps/<uuid:app_id>/")
def app_details(request, app_id):
    with db:
        app = App.get(App.app_id == app_id)
        template = env.get_template("detail.html")
        return webapp.render(request, template.render(app=app))


if __name__ == "__main__":
    webapp.run(debug=True)
