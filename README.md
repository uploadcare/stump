# Stump: transfer your files to Azure


We are often asked how to move files between Uploadcare and other storages. 
Uploadcare supports automatic transfer to S3 and Selectel  on our premium plans. 
Other cloud storages (Google, Azure) are not supported out-of-box. 
We advise our clients to use our REST API to move files. 
This project aims at providing you a base for transferring files from our storage to Azure. 
It is based on Django and Celery, which gives you great flexibility 
to further customize your workflow that fits your needs.


#### Before we start.

Install Heroku CLI on your local PC.

#### Installation.

1. In your terminal:
    `git clone https://github.com/uploadcare/stump` && `cd stump`
2. Create your app:
`heroku create example`
3. Log-in to your Uploadcare project. 
Click on webhooks menu item and add webhook URL to your project dashboard in Uploadcare. 
It should look like this: https://example.herokuapp.com/stamper/webhook/
4. Install rabbit-mq broker add-on:
  `heroku addons:create rabbitmq-bigwig:pipkin`
5. Update your credentials in settings.py:

    ~~~~

    SECRET_KEY = 'YOUR_DJANGO_SECRET_KEY'
    ...
    UPLOADCARE = {
        'pub_key': 'YOUR_PUBLIC_KEY',
        'secret': 'YOUR_UPLOADCARE_SECRET',
    }
    ...
    AZURE = {
        'account_name':'YOUR_AZURE_ACCOUNT_NAME',
        'account_key':'YOUR_AZURE_ACCOUNT_KEY',
        'sas':'YOUR_CONNECTION_STRING'
    }
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'YOUR_DB_NAME',
        'USER':'YOUR_USERNAME',
	    'HOST':'YOUR_DB_HOST',
        'PORT':'5432',
        'PASSWORD': 'YOUR_DB_PASSWORD'
    },
	}
    ~~~~

    Also don't forget to change DEBUG to False

6. Apply migrations to your database:

`heroku run python manage.py migrate`

#### Optional.
Heroku provides PostgreSQL add-on by default. 
Obviously you are free to change it
to your own DB instance. Celery sets up the broker URL from environment variables  
RABBITMQ_BIGWIG_RX_URL and RABBITMQ_BIGWIG_TX_URL. 
If you have followed installation steps nothing should be changed. 
If you have your own broker set up, just add configuration lines to settings file:

```
broker_read_url = 'amqp://user:pass@broker.example.com:56721'
broker_write_url = 'amqp://user:pass@broker.example.com:56722'
```
Setting timezone will help you a lot when plowing through logs.

#### Testing
No tests yet.