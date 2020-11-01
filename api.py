import inspect
import os
import time

from webob import Request, Response
from parse import parse
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter
from jinja2 import Environment, FileSystemLoader
from whitenoise import WhiteNoise
from middleware import Middleware

class API:
    def __init__(self, templates_directory="templates", static_dir="static"):
        self.routes = {} #paths are the keys and handlers (functions or classes) are the values

        self.templates_environment = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_directory))
        )

        self.exception_handler = None

        #self.whitenoise = WhiteNoise(self.wsgi_application, root=static_dir) #wrap wsgi application to serve static files
        
        self.middleware = Middleware(self)

    def __call__(self, environ, start_response): #Compatible WSGI server will call for each client HTTP request. 
       print("Callable was triggered due to request from client application at time: " + str(time.time()))
       return self.middleware(environ, start_response)

    def wsgi_application(self, environ, start_response):
        request = Request(environ)

        response = self.handle_request(request)

        return response(environ, start_response)

    """
    Middleware
    """
    def add_middleware(self, middleware_cls):
        self.middleware.add(middleware_cls)

    """
    TEST CLIENT
    """
    def test_session(self, base_url="http://testserver"):
        """
        Creates a test client associated with the given a url.
        The test session will be a requests session to be able to
        emulate a client in the browser.
        """
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session

    """
    ROUTING
    """
    def add_route(self, path, handler):
        """
        Adds a route which is a key-value pair.
        The key is the url path and the value is either
        a function handler or a class-based route.
        """
        if path in self.routes:
            raise AssertionError("Failed. Such a route already exists.")

        self.routes[path] = handler

    def route(self, path):
        """
        Adds a route via a decorator function.
        """
        def wrapper(handler):
            self.routes[path] = handler
            return handler

        return wrapper

    """
    TEMPLATING
    """
    def get_template(self, template_name, context=None):
        """
        Gets the template based on the template name
        """
        if context is None: 
            context = {}
        
        return self.templates_environment.get_template(template_name).render(**context)

    """
    HANDLING
    """
    def handle_request(self, request):
        """
        Handles the client request, which is an webob object.
        """
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
        """
        Gets the method associated with the requested path.
        This function is used with class based routes.
        """
        handler_method = getattr(handler(),request.method.lower(), None)
        
        return handler_method

    def lookup_handler(self, request_path):
        """
        Finds the function handler associated with the requested path
        """
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named
        
        return None, None
    
    def add_exception_handler(self, exception_handler):
        """
        Adds a function to the application that handle exceptions
        """
        self.exception_handler = exception_handler

    """
    RESPONSES
    """
    def default_response(self, response):
        response.status_code = 404
        response.text = "Requested path not found."