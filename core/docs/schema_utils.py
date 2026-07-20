from drf_spectacular.utils import extend_schema, extend_schema_view
import copy


def auto_schema(**schema_kwargs):
    def decorator(cls):
        kwargs = copy.deepcopy(schema_kwargs)

        full_source = f"{cls.__module__}.{cls.__qualname__}"

        description = kwargs.get('description', '')
        kwargs['description'] = f"{description}\n\n**Source:** `{full_source}`"

        responses = kwargs.get('responses', {})
        kwargs['responses'] = {
            status_code: (response(source=full_source) if callable(response) else response)
            for status_code, response in responses.items()
        }

        return extend_schema(**kwargs)(cls)
    return decorator


def _build_extend_schema(schema_kwargs, full_source):
    kwargs = copy.deepcopy(schema_kwargs)

    description = kwargs.get('description', '')
    kwargs['description'] = f"{description}\n\n**Source:** `{full_source}`"

    responses = kwargs.get('responses', {})
    kwargs['responses'] = {
        status_code: (response(source=full_source) if callable(response) else response)
        for status_code, response in responses.items()
    }

    return extend_schema(**kwargs)


def auto_schema_view(**action_schemas):
    """
    Igual que auto_schema, pero para ViewSets con varias acciones.
    Uso: auto_schema_view(list=SCHEMA_A, create=SCHEMA_B, upload=SCHEMA_C, ...)
    """
    def decorator(cls):
        full_source = f"{cls.__module__}.{cls.__qualname__}"

        extend_kwargs = {
            action_name: _build_extend_schema(schema_kwargs, full_source)
            for action_name, schema_kwargs in action_schemas.items()
        }

        return extend_schema_view(**extend_kwargs)(cls)
    return decorator