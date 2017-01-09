from celery.task import PeriodicTask
from celery.schedules import crontab
from celery import group
from azure.storage.blob import BlockBlobService
from azure.storage.blob import PublicAccess
from azure.storage import CloudStorageAccount
from azure.storage.blob.models import ContentSettings
from stump.celery_app import app
from django.conf import settings
from .models import FileUploadMessage, ImageUploadMessage, WebhookLog, FailedTask
from celery.utils.log import get_task_logger
from celery import Task
from django.db import models
import time
import json


logger = get_task_logger(__name__)


class LogErrorsTask(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        self.save_failed_task(exc, task_id, args, kwargs, einfo)
        super(LogErrorsTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    def save_failed_task(self, exc, task_id, args, kwargs, traceback):
        """
        :type exc: Exception
        """
        task = FailedTask()
        task.celery_task_id = task_id
        task.full_name = self.name
        task.name = self.name.split('.')[-1]
        task.exception_class = exc.__class__.__name__
        task.exception_msg = unicode(exc).strip()
        task.traceback = unicode(traceback).strip()
        task.updated_at = timezone.now()

        if args:
            task.args = json.dumps(list(args))
        if kwargs:
            task.kwargs = json.dumps(kwargs)

        # Find if task with same args, name and exception already exists
        # If it does, update failures count and last updated_at
        #: :type: FailedTask
        existing_task = FailedTask.objects.filter(
            args=task.args,
            kwargs=task.kwargs,
            full_name=task.full_name,
            exception_class=task.exception_class,
            exception_msg=task.exception_msg,
        )

        if len(existing_task):
            existing_task = existing_task[0]
            existing_task.failures += 1
            existing_task.updated_at = task.updated_at
            existing_task.save(force_update=True,
                               update_fields=('updated_at', 'failures'))
        else:
            task.save(force_insert=True)


class TransferAzure():

    transaction = None
    CDN_BASE = 'https://ucarecdn.com/'
    account = None
    service = None
    file_uuid = None
    filename = None
    make_public = None

    def __init__(self, make_public=False, transaction=None):
        account_name = settings.AZURE['account_name']
        account_key = settings.AZURE['account_key']
        sas = settings.AZURE['sas']
        self.transaction = transaction
        self.transaction_body = json.loads(transaction.body)['data']
        logger.info('copying uuid: ' + self.transaction_body['uuid'])
        self.file_uuid = self.transaction_body['uuid']
        self.filename = self.transaction_body['original_filename']
        self.make_public = make_public
        self.account = CloudStorageAccount(account_name=account_name, account_key=account_key, sas_token=sas)
        self.service = self.account.create_block_blob_service()

    def save_message_object(self):
        kwargs = {
            prop: self.transaction_body[prop]
            for prop in [
                'uuid', 'filename', 'is_stored',
                'done', 'file_id', 'original_filename',
                'is_ready', 'total', 'mime_type', 'size']
        }

        if self.transaction_body['is_image']:
            MessageClass = ImageUploadMessage
            kwargs['imgformat'] = self.transaction_body['image_info']['format']
            for prop in ['orientation', 'height', 'width',
                         'geo_location', 'datetime_original', 'dpi']:
                kwargs[prop] = self.transaction_body['image_info'][prop]
        else:
            MessageClass = FileUploadMessage
        return MessageClass.objects.create(
            webhook_transaction=self.transaction, **kwargs)

    def _blob_exists(self, container_name, blob_name):
        exists = self.service.exists(container_name, blob_name)

    def _get_resource_reference(self):
        return '{}'.format(self.file_uuid)

    def run_copy(self):
        try:
            logger.info('creating container name')
            container_name = self._get_resource_reference()
            logger.info('container name: ' + container_name)
            self.service.create_container(container_name)
            logger.info('set permission public')
            self.service.set_container_acl(container_name, public_access=PublicAccess.Container)
            count = 0
            source = self.CDN_BASE + self.file_uuid + '/'
            logger.info('copying the file from source: ' + source)
            copy = self.service.copy_blob(container_name, self.filename, source)
            # Poll for copy completion
            logger.info('checking status')
            while copy.status != 'success':
                count = count + 1
                if count > 20:
                    logger.info('Timed out waiting for async copy to complete on %i count' % count)
                    raise Exception('Timed out waiting for async copy to complete.')
                time.sleep(3 * count)
                logger.info('get blob properties')
                copy = self.service.get_blob_properties(container_name, self.filename).properties.copy
            logger.info('saved mesg object')
            return True
        except Exception, e:
            print(e.message)
            self.service.delete_container(container_name)
        else:
          pass
        finally:
          pass


@app.task(name='stamper.tasks.ProcessFileUploadMessages', base=LogErrorsTask)
class ProcessFileUploadMessages(PeriodicTask):

    def get_transactions_to_process(self):
        logger.info("getting transactions to process")
        return WebhookLog.objects.filter(
            status=WebhookLog.UNPROCESSED
        ).values_list('id', flat=True)

    @app.task
    def process_trans(self, transaction_id):
        try:
            transaction = WebhookLog.objects.get(id__exact=transaction_id)
            transferAzure = TransferAzure(make_public=False, transaction=transaction)
            if (transferAzure.run_copy() is False):
                raise Exception("Copy to Azure failed")
            transaction.status = WebhookLog.PROCESSED
            transaction.save()
            return True
        except Exception, e:
            transaction.status = WebhookLog.ERROR
            transaction.save()
            logger.error("Error while saving transaction " + str(e))
            raise Exception('Azure copy exception: ')
        finally:
            logger.info("Just saved uploadMessageObject ")

    run_every = crontab(minute='*', hour='*', day_of_week="*")
    
    def run(self, **kwargs):
        try:
            unprocessed_transactions_ids = self.get_transactions_to_process()
            copy_jobs = group(self.process_trans.s(self, transaction_id) for transaction_id in unprocessed_transactions_ids)
            result = copy_jobs.apply_async()
        except Exception, e:
                logger.error("Error while processing transaction: " + str(e))
                raise self.retry(exc=e, countdown=10)
