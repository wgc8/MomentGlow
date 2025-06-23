from rest_framework.views import APIView
from .response import CustomResponse

class CustomAPIView(APIView):
    def finalize_response(self, request, response, *args, **kwargs):
        # 只包裹普通Response，避免二次包裹
        if not isinstance(response, CustomResponse) and hasattr(response, 'data'):
            code = 0 if response.status_code < 400 else response.status_code
            errMsg = "" if response.status_code < 400 else response.data.get('detail', 'error')
            response = CustomResponse(data=response.data, code=code, errMsg=errMsg, status=response.status_code)
        return super().finalize_response(request, response, *args, **kwargs) 