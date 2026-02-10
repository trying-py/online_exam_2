import logging
import time

req_logger = logging.getLogger("requests")


class RequestLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration_ms = int((time.time() - start) * 1000)

        user = getattr(request, "user", None)
        username = user.username if (
            user and user.is_authenticated) else "anonymous"

        req_logger.info(
            "%s %s status=%s user=%s duration_ms=%s",
            request.method,
            request.get_full_path(),
            response.status_code,
            username,
            duration_ms,
        )
        return response
