from django.core.management import BaseCommand
from iotrec_api.models import Thing
from iotrec_api.utils.similarity_reference import calculate_similarity_references


class Command(BaseCommand):
    help = 'Calculates the most similar reference_things for each thing'

    def handle(self, *args, **options):
        nr_of_things = Thing.objects.count()
        nr_of_sr_deleted, nr_of_sr_created = calculate_similarity_references()
        self.stdout.write(self.style.SUCCESS('Successfully calculated reference similarities. Number of things: %d. Number of reference similarities deleted: %d. Number of reference similarities created: %d.' % (nr_of_things, nr_of_sr_deleted, nr_of_sr_created)))
