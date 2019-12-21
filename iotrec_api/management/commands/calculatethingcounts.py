from django.core.management import BaseCommand
from iotrec_api.models import Category
from iotrec_api.utils.category import calc_items_in_cat_full


class Command(BaseCommand):
    help = 'Calculates the thing counts for each category'

    def handle(self, *args, **options):
        nr_of_categories = Category.objects.count()
        nr_of_calcs = calc_items_in_cat_full()
        self.stdout.write(self.style.SUCCESS('Successfully calculated the thing counts. Number of categories: %d. Number of calculations performed: %d.' % (nr_of_categories, nr_of_calcs)))
