from django.core.management import call_command
from django.core.management.base import BaseCommand

from configservice.models import AppSpace


class Command(BaseCommand):
    help = 'VSolv Data Migration'

    def handle(self, *args, **options):
        app_arr = AppSpace.objects.all()
        for app in app_arr:
            prnt_str = 'Application ' + app.application.namespace + ' successfully migrated to ' + app.schema.name + '.'
            call_command('migrate', app.application.namespace, database=app.schema.name, verbosity=3, interactive=True)
            self.stdout.write(self.style.SUCCESS(prnt_str))