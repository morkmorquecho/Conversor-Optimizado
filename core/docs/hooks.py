from core.docs.response import INFRA_RESPONSES
from drf_spectacular.plumbing import ResolvedComponent
from drf_spectacular.utils import OpenApiResponse


def add_global_error_responses(result, generator, request, public):
    for path, methods in result.get("paths", {}).items():
        for method, operation in methods.items():
            responses = operation.setdefault("responses", {})
            for status_code, response in INFRA_RESPONSES.items():
                if status_code not in responses:
                    responses[status_code] = response
    return result