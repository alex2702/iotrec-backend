#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    #os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iotrec.settings.development')
    try:
        from django.core.management import execute_from_command_line

        # use PyMySQL as MySQL driver
        #if os.environ.get('DJANGO_SETTINGS_MODULE') == 'iotrec.settings.production':
        #    import pymysql
        #    pymysql.install_as_MySQLdb()
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
