from iotrec_api import models
from iotrec_api.utils.thing import get_thing_similarity
from training.models import ReferenceThing


def calculate_similarity_references():
    '''
    For each Thing, calculates the most similar ReferenceThings.
    The number of "most similar" ReferenceThings to be saved N is determined by the configuration.
    '''

    settings = models.IotRecSettings.load()
    nr_of_top_ref_things_to_save = settings.nr_of_reference_things_per_thing

    things = models.Thing.objects.all()
    ref_things = ReferenceThing.objects.filter(active=True)

    nr_of_sr_deleted = 0
    nr_of_sr_created = 0

    for thing in things:
        # calculate the similarity to all reference_things
        similarities = [
            (ref_thing, get_thing_similarity(thing, ref_thing))
            for ref_thing in ref_things
        ]

        # sort the results by score and truncate to N
        sorted(similarities, key=lambda elem: elem[1])
        top_similarities = similarities[:nr_of_top_ref_things_to_save]

        # clear all existing similarity_references for the given thing
        delete_result = models.SimilarityReference.objects.filter(thing=thing).delete()
        nr_of_sr_deleted += delete_result[0]

        # save the top N reference_things as new similarity_references
        for ref_thing, similarity in top_similarities:
            models.SimilarityReference.objects.create(reference_thing=ref_thing, thing=thing, similarity=similarity)
            nr_of_sr_created += 1

    return nr_of_sr_deleted, nr_of_sr_created


def calculate_similarity_references_per_thing(thing):
    '''
    Calculates the most similar ReferenceThings for a given Thing.
    Used when a new thing is created.
    The number of "most similar" ReferenceThings to be saved N is determined by the configuration.
    '''

    settings = models.IotRecSettings.load()
    nr_of_top_ref_things_to_save = settings.nr_of_reference_things_per_thing

    ref_things = ReferenceThing.objects.filter(active=True)

    nr_of_sr_deleted = 0
    nr_of_sr_created = 0

    # calculate the similarity to all reference_things
    similarities = [
        (ref_thing, get_thing_similarity(thing, ref_thing))
        for ref_thing in ref_things
    ]

    # sort the results by score and truncate to N
    sorted(similarities, key=lambda elem: elem[1])
    if thing.indoorsLocation is None:
        # go through all similarities and duplicate reference_things (by name)
        # we do this to avoid weighing the same ref_thing double, i.e. with "inside" AND "outside", even though we don't
        # know if the thing under consideration is inside or outside
        ref_thing_names_found = []
        unique_ref_things_found = 0
        for sim in similarities:
            if unique_ref_things_found >= nr_of_top_ref_things_to_save:
                break
            else:
                if sim[0].title in ref_thing_names_found:
                    similarities.remove(sim)
                else:
                    ref_thing_names_found.append(sim[0].title)
                    unique_ref_things_found += 1
    top_similarities = similarities[:nr_of_top_ref_things_to_save]
    print("top_similarities:")
    print(top_similarities)

    # clear all existing similarity_references for the given thing
    delete_result = models.SimilarityReference.objects.filter(thing=thing).delete()
    nr_of_sr_deleted += delete_result[0]

    # save the top N reference_things as new similarity_references
    for ref_thing, similarity in top_similarities:
        models.SimilarityReference.objects.create(reference_thing=ref_thing, thing=thing, similarity=similarity)
        nr_of_sr_created += 1

    return nr_of_sr_deleted, nr_of_sr_created