import pytest
from fixtures import api, client

"""
DIRECTORIES
"""
def test_default(api, client):
    response_text = "Hello from local host"

    @api.route("/")
    def default(request, response):
        response.text = response_text

    assert client.get("http://testserver/").text == response_text

def test_home(api, client):
    response_text = "Django like way to add routes"

    def home(request, response):
        response.text = response_text

    api.add_route("/home", home)

    assert client.get("http://testserver/home").text == response_text

"""
HTTP
"""
def test_default_404_response(client):
    response = client.get("http://testserver/doesnotexist")

    assert response.status_code == 404
    assert response.text == "Not found."


def test_404_returned_for_nonexistent_static_file(client):
    assert client.get(f"http://testserver/main.css").status_code == 404

"""
TEMPLATES
"""
def test_template(api, client):
    @api.route("/html")
    def html_handler(request, response):
        response.body = api.get_template("index.html", context={"title": "Some Title", "name": "Some Name"}).encode()

    response = client.get("http://testserver/html")

    assert "text/html" in response.headers["Content-Type"]
    assert "Some Title" in response.text
    assert "Some Name" in response.text

"""
HANDLERS
"""
def test_custom_exception_handler(api, client):
    def on_exception(request, response, exception):
        response.text = "AttributeErrorOccured"
    
    api.add_exception_handler(on_exception)

    @api.route("/")
    def index(request, response):
        raise AttributeError()

    response = client.get("http://testserver/")

    assert response.text == "AttributeErrorOccured"