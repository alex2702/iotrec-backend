from .models import IotRecSettings

def iotrec_settings(request):
    return {'settings': IotRecSettings.load()}