from webob import Request, Response
from parse import parse

class API():
    def __init__(self):
        self.routes = {} #store the path request as keys and handlers (function references) as values

    def __call__(self, environ, start_response):
        """
        Each time a client makes an HTTP request, this function will (must) be called by a compatable WSGI HTTP Server
        """
        request = Request(environ)

        response = self.request_handler(request)

        return response(environ, start_response)

    def route(self, path):
        def wrapper(handler):
            if path in self.routes:
                raise AssertionError("Sorry, the route already exists")
            else:
                self.routes[path] = handler
                return handler

        return wrapper

    def lookup_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result != None:
                return handler, parse_result.named
        
        return None, None

    def request_handler(self, request):
        response = Response()

        handler, kwargs = self.lookup_handler(request_path=request.path)

        if handler != None:
            handler(request, response, **kwargs)
        else:
            self.default_response(response)
        
        return response

    def default_response(self, response):
        response.status_code = 404
        response.text = "Requested path not found."