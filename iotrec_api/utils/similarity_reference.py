from django.db import connection
from django.utils import timezone

from iotrec_api import models
from iotrec_api.utils import thing
#from training.models import ReferenceThing
from django.apps import apps



def calculate_similarity_references():
    '''
    For each Thing, calculates the most similar ReferenceThings.
    The number of "most similar" ReferenceThings to be saved N is determined by the configuration.
    '''

    settings = models.IotRecSettings.load()
    nr_of_top_ref_things_to_save = settings.nr_of_reference_things_per_thing

    things = models.Thing.objects.all()
    ReferenceThing = apps.get_model('training.ReferenceThing')
    ref_things = ReferenceThing.objects.filter(active=True)

    nr_of_sr_deleted = 0
    nr_of_sr_created = 0

    for t in things:
        # calculate the similarity to all reference_things
        similarities = [
            (ref_thing, thing.get_thing_similarity(t, ref_thing))
            for ref_thing in ref_things
        ]

        # sort the results by score and truncate to N
        sorted_similarities = sorted(similarities, key=lambda elem: elem[1])
        top_similarities = sorted_similarities[:nr_of_top_ref_things_to_save]

        # clear all existing similarity_references for the given thing
        delete_result = models.SimilarityReference.objects.filter(thing=t).delete()
        nr_of_sr_deleted += delete_result[0]

        # save the top N reference_things as new similarity_references
        for ref_thing, similarity in top_similarities:
            models.SimilarityReference.objects.create(reference_thing=ref_thing, thing=t, similarity=similarity)
            nr_of_sr_created += 1

    return nr_of_sr_deleted, nr_of_sr_created


def calculate_similarity_references_per_thing(t):
    '''
    Calculates the most similar ReferenceThings for a given Thing.
    Used when a new thing is created.
    The number of "most similar" ReferenceThings to be saved N is determined by the configuration.
    '''

    #print("query marker 1: " + str(len(connection.queries)))
    #print(str(timezone.now()) + " - started calculating reference similarities")

    settings = models.IotRecSettings.load()
    nr_of_top_ref_things_to_save = settings.nr_of_reference_things_per_thing

    ReferenceThing = apps.get_model('training.ReferenceThing')
    ref_things = ReferenceThing.objects.filter(active=True)

    #print("query marker 2: " + str(len(connection.queries)))
    #print(str(timezone.now()) + " - got the reference things")

    nr_of_sr_deleted = 0
    nr_of_sr_created = 0

    # calculate the similarity to all reference_things
    similarities = [
        (ref_thing, thing.get_thing_similarity(t, ref_thing))
        for ref_thing in ref_things
    ]

    #print("query marker 3: " + str(len(connection.queries)))
    #print(str(timezone.now()) + " - got the similarities")

    # sort the results by score and truncate to N
    similarities_sorted = sorted(similarities, key=lambda elem: elem[1])

    # if the thing's locality is not given, eliminate duplicate reference_similarities (that only vary by locality)
    if t.indoorsLocation is None:
        # go through all similarities and find duplicate reference_things (by name)
        # we do this to avoid weighing the same ref_thing double, i.e. with "inside" AND "outside", even though we don't
        # know if the thing under consideration is inside or outside
        ref_thing_names_found = []
        unique_ref_things_found = 0
        for sim in similarities_sorted:
            if unique_ref_things_found >= nr_of_top_ref_things_to_save:
                break
            else:
                if sim[0].title in ref_thing_names_found:
                    similarities_sorted.remove(sim)
                else:
                    ref_thing_names_found.append(sim[0].title)
                    unique_ref_things_found += 1

    top_similarities = similarities_sorted[:nr_of_top_ref_things_to_save]

    #print("query marker 4: " + str(len(connection.queries)))
    #print(str(timezone.now()) + " - got the top similarities")

    # clear all existing similarity_references for the given thing
    delete_result = models.SimilarityReference.objects.filter(thing=t).delete()
    nr_of_sr_deleted += delete_result[0]

    # save the top N reference_things as new similarity_references
    for ref_thing, similarity in top_similarities:
        models.SimilarityReference.objects.create(reference_thing=ref_thing, thing=t, similarity=similarity)
        nr_of_sr_created += 1

    #print("query marker 5: " + str(len(connection.queries)))
    #print(str(timezone.now()) + " - created reference similarities")

    return nr_of_sr_deleted, nr_of_sr_created