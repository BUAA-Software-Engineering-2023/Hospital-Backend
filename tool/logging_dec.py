import jwt
from django.http import JsonResponse
from django.conf import settings


def logging_check(func):
    def wrap(request, *args, **kwargs):

        token = request.META.get('HTTP_AUTHORIZATION')
        if token is not None:
            try:
                jwt_token = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms='HS256')
            except:
                response = {
                    "result": "0",
                    "reason": "token error"
                }
                return JsonResponse(response, status=401)
        else:
            return JsonResponse({"result":"0","message":"用户未登录"})
        return func(request, *args, **kwargs)

    return wrap
