from webob import Request, Response

class API():
    def __init__(self):
        self.routes = {} #store the paths as keys and handlers as values

    def __call__(self, environ, start_response):
        """
        Each time a client makes an HTTP request, this function
        will (must) be called by a compatable WSGI HTTP Server
        --------------------------------------------------------
        environment: a dictionary with environment variables
        start_response: a call after function used to send HTTP statuses and HTTP headers to the server
        """
        request = Request(environ)

        response = self.request_handler(request)

        return response(environ, start_response)

    def route(self, path):
        """
        This method is a decorator that accepts a path and wraps the handlers
        --------------------------------------------------------------------
        path: the path to the specified directory
        """
        def wrapper(handler):
            self.routes[path] = handler
            return handler
        
        return wrapper

    def request_handler(self, request):
        """
        This method will handle the request from the client
        ---------------------------------------------------
        request: the request from the client
        """
        user_agent = request.environ.get("HTTP_USER_AGENT", "No User Agent Found") #identifies the application, OS, vender, and/or version of the requesting user agent

        response = Response()
        response.text = f"Response from server, {user_agent}"

        return response