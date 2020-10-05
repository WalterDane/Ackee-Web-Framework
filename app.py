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

@app.route("/book")
class BooksResource:
    def get(self, request, response):
        response.text = "Books Page"

    def post(self, request, response):
        response.text = "Endpoint to create a book"
    
    def put(self, request, response):
        response.text = "Replacing current representation of the target resource"

    def delete(self, request, response):
        response.text = "Deleting the specified resoue"
