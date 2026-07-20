# exceptions.py
from rest_framework.views import exception_handler as drf_exception_handler
from .error_codes import DEFAULT_CODE_MAP, ErrorCodes

def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is not None:
        # Si la excepción define su propio code (custom), úsalo.
        # Si no, cae al default_code de DRF, y si tampoco existe, UNKNOWN.
        raw_code = getattr(exc, "code", None) or getattr(exc, "default_code", None)
        code = DEFAULT_CODE_MAP.get(raw_code, raw_code.upper() if raw_code else ErrorCodes.UNKNOWN)

        response.data = {
            "code": code,
            "detail": response.data,
        }

    return response