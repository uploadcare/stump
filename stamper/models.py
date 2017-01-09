from __future__ import unicode_literals
from django.db import models
from django.db import models
from django.utils import timezone

class FailedTask(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    name = models.CharField(max_length=125)
    full_name = models.TextField()
    args = models.TextField(null=True, blank=True)
    kwargs = models.TextField(null=True, blank=True)
    exception_class = models.TextField()
    exception_msg = models.TextField()
    traceback = models.TextField(null=True, blank=True)
    celery_task_id = models.CharField(max_length=36)
    failures = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ('-updated_at',)

    def __unicode__(self):
        return '%s %s [%s]' % (self.name, self.args, self.exception_class)

    def retry_and_delete(self, inline=False):
        import importlib
        # Import real module and function
        mod_name, func_name = self.full_name.rsplit('.', 1)
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)

        args = json.loads(self.args) if self.args else ()
        kwargs = json.loads(self.kwargs) if self.kwargs else {}
        if inline:
            try:
                res = func(*args, **kwargs)
                self.delete()
                return res
            except Exception as e:
                raise e

        self.delete()
        return func.delay(*args, **kwargs)

class WebhookLogManager(models.Model):

    def create(self, _request_meta, _body, _status, _date_generated):
        whObject = self.create(request_meta=_request_meta, body = _body, status = _status, date_generated = _date_generated)
        return whObject

class WebhookLog(models.Model):
    UNPROCESSED = 1
    PROCESSED = 2
    ERROR = 3

    STATUSES = (
        (UNPROCESSED, 'Unprocessed'),
        (PROCESSED, 'Processed'),
        (ERROR, 'Error'),
    )

    date_generated = models.DateTimeField()
    date_received = models.DateTimeField(default=timezone.now)
    body = models.CharField(max_length=4096, default='')
    request_meta = models.CharField(max_length=4096, default='')
    status = models.CharField(max_length=250, choices=STATUSES, default=UNPROCESSED)
    is_image = models.BooleanField(default=False)
    objects = WebhookLogManager()

    # def __unicode__(self):
    #     return u'{0}'.format(self.date_event_generated)
class UploadMessage(models.Model):

    webhook_transaction = models.OneToOneField(WebhookLog)
    date_processed = models.DateTimeField(default=timezone.now)
    uuid = models.CharField(max_length=255)
    original_file_url = models.CharField(max_length=255)
    filename = models.CharField(max_length=250)
    is_stored = models.BooleanField()
    done = models.BigIntegerField()
    file_id = models.CharField(max_length=250)
    original_filename = models.CharField(max_length=255)
    is_ready = models.BooleanField()
    total = models.CharField(max_length=255)
    mime_type = models.CharField(max_length=255)
    size = models.BigIntegerField()
    

    class Meta:
        abstract = True

    def __unicode__(self):
        return u'{}'.format(self.uuid)

class FileUploadMessage(UploadMessage):
    pass

class ImageUploadMessage(UploadMessage):
    orientation = models.CharField(max_length=255,null = True, default = None)
    imgformat =  models.CharField(max_length=255,null = True, default = None)
    height = models.IntegerField()
    width = models.IntegerField()
    geo_location =  models.CharField(max_length=255, null = True, default = None)
    datetime_original = models.DateTimeField(null = True, default = None)
    dpi = models.IntegerField(null = True, default = None)
