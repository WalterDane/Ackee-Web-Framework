from api import API
from middleware import Middleware

app = API() #calling instance of API class is the responsibility of the web server

"""
Directories
"""
@app.route("/")
def default(request, response):
    response.text = "Hello from local host"

@app.route("/home")
def home(request, response):
    response.text = "Hello from the HOME page"

@app.route("/about")
def about(request, response):
    response.text = "Hello from the ABOUT page"

"""
Templating
"""
@app.route("/template")
def template_handler(request, response):
    response.body = app.get_template(
        "index.html",
        context={"name": "Ackee", "title": "Legit framework"}
    ).encode()

@app.route("/exception")
def throw_handler_exception(request, response):
    raise AssertionError("This handler should not be used")

"""
Exceptions
"""
def custom_exception_handler(request, response, exception_cls):
    response.text = str(exception_cls)

app.add_exception_handler(custom_exception_handler)