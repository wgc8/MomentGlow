from rest_framework.response import Response

class CustomResponse(Response):
    def __init__(self, data=None, code=0, errMsg="", status=None, headers=None, content_type=None, **kwargs):
        response_data = {
            "code": code,
            "errMsg": errMsg,
            "data": data
        }
        super().__init__(response_data, status=status, headers=headers, content_type=content_type)