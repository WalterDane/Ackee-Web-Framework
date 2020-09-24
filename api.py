from webob import Request, Response

class API():
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

    def request_handler(self, request):
        """
        request: the request from the client
        """
        user_agent = request.environ.get("HTTP_USER_AGENT", "No User Agent Found") #identifies the application, OS, vender, and/or version of the requesting user agent

        response = Response()
        response.text = f"Hello, {user_agent}"

        return response