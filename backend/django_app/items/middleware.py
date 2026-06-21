"""Adds an `X-Served-By` header so the frontend can show which backend
responded (handy when demoing the same component against Django vs FastAPI)."""


class ServedByMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response["X-Served-By"] = "django"
        return response
