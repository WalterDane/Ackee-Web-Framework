import inspect
import os

from webob import Request, Response
from parse import parse
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter
from jinja2 import Environment, FileSystemLoader
from whitenoise import WhiteNoise

class API:
    def __init__(self, templates_directory="templates"):
        self.routes = {} #paths are the keys and handlers (functions or classes) are the values

        self.templates_environment = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_directory))
        )

        self.exception_handler = None

        self.whitenoise = WhiteNoise(self.wsgi_application, root=static_dir)

    def __call__(self, environ, start_response): #Compatible WSGI server will call for each client HTTP request. 
        return self.wsgi_application(environ, start_response)

    def wsgi_application(self, environ, start_response):
        request = Request(environ)

        response = self.handle_client_request(request)

        return response(environ, start_response)

    """
    TEST CLIENT
    """
    def test_session(self, base_url="http://testserver"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session

    """
    ROUTING
    """
    def route(self, path):
        def wrapper(handler):
            self.routes[path] = handler
            return handler

        return wrapper

    def add_route(self, path, handler):
        if path in self.routes:
            raise AssertionError("Failed. Such a route already exists.")

        self.routes[path] = handler

    """
    TEMPLATING
    """
    def get_template(self, template_name, context=None):
        if context is None: 
            context = {} #dangerous to set mutable object (dict) as a default value ^
        
        return self.templates_environment.get_template(template_name).render(**context)

    """
    HANDLING
    """
    def handle_client_request(self, request):
        response = Response()

        handler, kwargs = self.lookup_handler(request_path=request.path)

        try:
            if handler is not None:
                if inspect.isclass(handler):
                    handler_method = self.get_class_method(handler, request)
                    if handler_method is None:
                        raise AttributeError("Method not allowed", request.method)
                    
                    handler_method(request, response, **kwargs)
                else:
                    handler(request, response, **kwargs)
            else:
                self.default_response(response)
        except Exception as exception:
            if self.exception_handler is None:
                raise exception
            else:
                self.exception_handler(request, response, exception)

        return response
    
    def get_class_method(self, handler, request):
        handler_method = getattr(handler(),request.method.lower(), None)
        
        return handler_method

    def lookup_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named
        
        return None, None
    
    def add_exception_handler(self, exception_handler):
        self.exception_handler = exception_handler

    """
    RESPONSES
    """
    def default_response(self, response):
        response.status_code = 404
        response.text = "Requested path not found."