import pytest

from api import API

@pytest.fixture
def api():
    return API()

def test_basic_route_adding(api):
    @api.route("/home")
    def home(req, resp):
        resp.text = "test"

def test_route_overlap_throws_exception(api):
    @api.route("/home")
    def home(req, resp):
        resp.text = "test"

    with pytest.raises(AssertionError): #function raises assertion error in the case of a duplicate route
        @api.route("/home")
        def home2(req, resp): #handles duplicate routes
            resp.text = "YOLO"