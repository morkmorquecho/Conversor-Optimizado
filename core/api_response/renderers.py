# renderers.py
from rest_framework.renderers import JSONRenderer
from decouple import config

PROJECT_NAME = config('PROJECT_NAME')


class StandardJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context['response']
        view = renderer_context.get('view', None)

        source = None
        if view:
            source = f"{PROJECT_NAME}.{view.__class__.__module__}.{view.__class__.__name__}"

        if response.status_code >= 400:
            code = None
            context = data
            message = None

            if isinstance(data, dict) and 'code' in data:
                code = data.get('code')
                context = data.get('detail', data)
                if isinstance(context, str):
                    message = context

            formatted_data = {
                'success': False,
                'data': None,
                'message': message,
                'errors': {
                    'code': code,
                    'source': source,
                    'context': context,
                },
            }
        else:
            formatted_data = {
                'success': True,
                'data': data,
                'message': None,
                'errors': None,
            }

        return super().render(formatted_data, accepted_media_type, renderer_context)    