# iotrec-backend

## Setup & Deployment

TODO explain DMOZ and parser

### Development

Make sure to set environment variable `DJANGO_SETTINGS_MODULE` to `iotrec.settings.development`.

### Production

Install required packages

```
sudo apt-get install libmysqlclient-dev
sudo -H pip3 install mysqlclient
```

Clone repository, e.g. in `/var/www`

Enter project directory and install dependencies

```
sudo pip3 install -r requirements.txt
```

Set up a sub-domain

Create Apache virtual hosts

`iotrec-le-ssl.conf`

```
<IfModule mod_ssl.c>
        <VirtualHost *:443>
                WSGIPassAuthorization On

                WSGIDaemonProcess iotrec python-path=/var/www/iotrec-backend:/usr/lib/python3/dist-packages
                WSGIProcessGroup iotrec
                WSGIScriptAlias / /var/www/iotrec-backend/iotrec/wsgi.py
        
                DocumentRoot /var/www/iotrec-backend
                ServerName example.com
        
                Protocols h2 http:/1.1
        
                <Directory /var/www/iotrec-backend/iotrec>
                        <Files wsgi.py>
                                Require all granted
                        </Files>
                </Directory>
        
                Alias /static/ /var/www/iotrec-backend/iotrec/static/
                <Directory /var/www/iotrec-backend/iotrec/static>
                        Require all granted
                </Directory>

                Alias /training/media/ /var/www/iotrec-backend/iotrec/media/
                <Directory /var/www/iotrec-backend/iotrec/media>
                        Require all granted
                </Directory>

                Alias /favicon.ico /var/www/iotrec-backend/favicon.ico
        
                SSLCertificateFile /etc/letsencrypt/live/example.com/fullchain.pem
                SSLCertificateKeyFile /etc/letsencrypt/live/example.com/privkey.pem
                SSLCertificateChainFile /etc/letsencrypt/live/example.com/chain.pem
                Include /etc/letsencrypt/options-ssl-apache.conf

                CustomLog /var/log/apache2/example.com-access.log combined
                ErrorLog  /var/log/apache2/example.com-error.log
        </VirtualHost>
</IfModule>
```

`iotrec.conf`
```
<VirtualHost *:80>
        DocumentRoot /var/www/iotrec-backend
        ServerName example.com

        RewriteEngine On
        RewriteCond %{SERVER_NAME} =example.com
        RewriteRule ^ https://%{SERVER_NAME}%{REQUEST_URI} [END,QSA,R=permanent]

        CustomLog /var/log/apache2/example.com-access.log combined
        ErrorLog  /var/log/apache2/example.com-error.log
</VirtualHost>
```

Customize production settings in `iotrec-backend/iotrec/settings/production.py`

* add a `SECRET_KEY`
* add your domain to `ALLOWED_HOSTS`
* add database credentials

Generate static files (run in project root directory)

```
sudo python3 manage.py collectstatic --settings=iotrec.settings.production
```

Run migrations

```
sudo python3 manage.py migrate --settings=iotrec.settings.production
```

Optionally, flush the database

```
sudo python3 manage.py flush --settings=iotrec.settings.production
```

Optionally, create a super user account (required when setting up for the first time)

```
sudo python3 manage.py createsuperuser --settings=iotrec.settings.production
```

Restart web server

```
sudo systemctl restart apache2
```

Open the system crontab

```
sudo nano /etc/crontab
```

Add the following line to enable the jobs to run regularly

```
* * * * * www-data cd /var/www/iotrec-backend && sudo python3 manage.py cron --settings=iotrec.settings.production
```

## Creating fixtures

Fixtures, i.e. files with initial data that can be imported into the database, can be created either manually or by dumping an existing database model into a JSON file:

```
python3 manage.py dumpdata iotrec_api.category --settings=iotrec.settings.development > categories.json
```

## Importing fixtures (initial data)

Import Sites by running

```
sudo python3 manage.py loaddata sites.json --settings=iotrec.settings.production
```

To set up the categories dataset, access the Django Console via `sudo python3 manage.py shell --settings=iotrec.settings.production` and run

```
from iotrec_api.models import Category; Category.objects.all().delete(); exit()
```

Back on the system command line, load the Categories from the fixture.
Note: The `post_save` receiver in `iotrec_api/utils/category.py` should be disabled/commented before doing this.

```
sudo python3 manage.py loaddata categories.json --settings=iotrec.settings.production
```

Access Django Console via `sudo python3 manage.py shell --settings=iotrec.settings.production` and run

```
from iotrec_api.models import Category; Category.objects.rebuild(); exit()
```

To set up training data, access the Django Console via `sudo python3 manage.py shell` and run

```
from training.models import ContextFactor; ContextFactor.objects.all().delete(); exit()
```

This will also delete all ContextFactorValues and all Samples (due to cascading delete strategy).

Import ContextFactors, ContextFactorValues and ReferenceThings by running

```
sudo python3 manage.py loaddata context_factors.json reference_things.json --settings=iotrec.settings.production
```

Import Scenarios, Things and Questions for experiment by running

```
sudo python3 manage.py loaddata scenarios.json things.json questions.json --settings=iotrec.settings.production
```

Import the Chroniker jobs that periodically recalculate baselines by running

```
sudo python3 manage.py loaddata jobs.json --settings=iotrec.settings.production
```

Restart web server

```
sudo systemctl restart apache2
```

## Transfering data between servers

Log in as super user

```
sudo -s
```

Dump the data

```
python3 manage.py dumpdata --natural-foreign --exclude auth.permission --exclude contenttypes --indent 4 --settings=iotrec.settings.production > dumpdata.json
```

Transfer the resulting json file to the other machine

Load the data

```
python3 manage.py loaddata dumpdata.json --settings=iotrec.settings.production
```
