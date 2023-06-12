from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from user_agents import parse

from user_app.models.device import Device


class ActiveDeviceMiddleware(MiddlewareMixin):

    def process_response(self, request, response):
        try:
            user = request.user
            if user.is_authenticated:
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[0]
                else:
                    ip = request.META.get('REMOTE_ADDR')

                user_agent = parse(request.META['HTTP_USER_AGENT'])
                os = f'{user_agent.os.family} {user_agent.os.version_string}'
                browser = user_agent.browser.family
                device_family = user_agent.device.family

                device = Device.objects.get(user_id=user.id, ip=ip, os=os, browser=browser, device=device_family)

                cache.set('seen_%s_%s' % (user.id, device.id), timezone.now(), settings.DEVICE_TRACK_TIMEOUT)

        except:
            pass

        return response


class HeaderMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response
