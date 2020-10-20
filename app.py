from api import API

app = API() #calling instance of API class is the responsibility of the web server

@app.route("/")
def default(request, response):
    response.text = "Hello from local host"

@app.route("/home")
def home(request, response):
    response.text = "Hello from the HOME page"

@app.route("/about")
def about(request, response):
    response.text = "Hello from the ABOUT page"

@app.route("/template")
def template_handler(request, response):
    response.body = app.get_template(
        "index.html",
        context={"name": "Ackee", "title": "Legit framework"}
    ).encode()