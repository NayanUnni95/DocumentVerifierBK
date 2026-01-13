from rest_framework.views import APIView

from utils.response import CustomResponse


class Common(APIView):
    """
    Common endpoint for server health check
    Forwards requests to the auth server and returns the response.
    """

    def get(self, request):
        return CustomResponse(
            general_message="✅ Server is healthy and running 🚀"
        ).get_success_response()