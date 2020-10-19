import inspect
from webob import Request, Response
from parse import parse
from requests import Session as RequestsSession
from wsgiadapter import WSGIAdapter as RequestsWSGIAdapter

class API:
    def __init__(self):
        self.routes = {} #paths are the keys and handlers (functions or classes) are the values

    def __call__(self, environ, start_response): #Compatible WSGI server will call for each client HTTP request. 
        request = Request(environ)

        response = self.handle_client_request(request)

        return response(environ, start_response)

    def test_session(self, base_url="http://testserver"):
        session = RequestsSession()
        session.mount(prefix=base_url, adapter=RequestsWSGIAdapter(self))
        return session

    def route(self, path):
        def wrapper(handler):
            self.routes[path] = handler
            return handler

        return wrapper

    def add_route(self, path, handler):
        if path in self.routes:
            raise AssertionError("Failed. Such a route already exists.")

        self.routes[path] = handler

    def handle_client_request(self, request):
        response = Response()

        handler, kwargs = self.lookup_handler(request_path=request.path)

        if handler is None:
            self.default_response(response)
        
        if handler is not None:
            if inspect.isclass(handler):
                handler_method = self.get_class_method(handler, request)
                if handler_method is None:
                    raise AttributeError("Method not allowed", request.method)
                
                handler_method(request, response, **kwargs)
            else:
                handler(request, response, **kwargs)
        
        return response

    def lookup_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named
        
        return None, None

    def default_response(self, response):
        response.status_code = 404
        response.text = "Requested path not found."

    def get_class_method(self, handler, request):
        handler_method = getattr(handler(),request.method.lower(), None)
        
        return handler_method