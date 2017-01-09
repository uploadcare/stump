from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.views.generic import View
from django.utils import timezone
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import WebhookLog
import copy
import json
import datetime


@csrf_exempt
@require_POST
def webhook(request):
  try:
    jsondata = request.body
    data = json.loads(jsondata)
    meta = copy.copy(request.META)
    for k, v in meta.items():
        if not isinstance(v, basestring):
            del meta[k]
    WebhookLog.objects.create(date_generated=timezone.now(),
                              body=jsondata,
                              request_meta=json.dumps(meta),
                              is_image=data['data']['is_image'])
    return HttpResponse(status=200)
  except Exception, e:
         print(e.message)
  else:
        pass
  finally:
        pass
