from webob import Request, Response

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
            self.routes[path] = handler
            print(handler)
            return handler
        
        return wrapper

    def request_handler(self, request):
        response = Response()

        handler = self.lookup_handler(request.path)

        if handler != None:
            handler(request, response)
        else:
            self.default_response(response)
        
        return response

    def lookup_handler(self, request_path):
        for path, handler in self.routes.items():
            if path == request_path:
                return handler

    def default_response(self, response):
        response.status_code = 404
        response.text = "Requested path not found."