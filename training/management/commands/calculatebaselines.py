from django.core.management import BaseCommand

from training.utils.baseline import calculate_baselines


class Command(BaseCommand):
    help = 'Calculates the reference_item/context_factor_value baselines'

    def handle(self, *args, **options):
        calculate_baselines()
        self.stdout.write(self.style.SUCCESS('Successfully calculated baselines'))