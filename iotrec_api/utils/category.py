from django.db import connection
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from django.utils import timezone

from iotrec_api import models


def calc_items_in_cat_full():
    #print("calc_items_in_cat_full")
    categories_saved = 0
    for cat in models.Category.objects.all():
        calc_items_in_cat_from_cat(cat)

        try:
            cat._dirty = True
            cat.save()
            categories_saved += 1
        finally:
            del cat._dirty

    return categories_saved

def calc_items_in_cat_list(list):
    cats_to_recalc = set()
    for cat in list:
        # add ancestors and descendants to recalc list
        cats_to_recalc = (cats_to_recalc | set(cat.get_ancestors()) | set(cat.get_descendants(include_self=True)))

    # do recalculation
    for cat in cats_to_recalc:
        calc_items_in_cat_from_cat(cat)
        try:
            cat._dirty = True
            cat.save()
        finally:
            del cat._dirty

def calc_items_in_cat_from_cat(category):
    #print(str(timezone.now()) + " - started calc_items_in_cat_from_cat for " + str(category))
    #print("query marker 1: " + str(len(connection.queries)))

    n_i_things_counted = set()  # prevent counting a thing multiple times
    for sub_cat in category.get_descendants(include_self=True):
        if sub_cat.thing_set.count() > 0:
            sub_cat_things = set(sub_cat.thing_set.all())
            n_i_things_counted = n_i_things_counted.union(sub_cat_things)

    category.nr_of_items_recursive = len(n_i_things_counted)
    #print("calc_items_in_cat_from_cat: " + str(category) + " - " + str(len(n_i_things_counted)) + " - " + str(n_i_things_counted))

    #print(str(timezone.now()) + " - completed calc_items_in_cat_from_cat")
    #print("query marker 2: " + str(len(connection.queries)))


'''
def calc_items_in_cat_from_thing(thing):
    print("calc_items_in_cat_from_thing")
    print(thing.categories.all())
    print(models.Thing.objects.get(id=thing.id).categories.all())

    # re-calculate n_i for all of the thing's categories, all their ancestors and all their descendants
    for category in thing.categories.all():
        # get ancestors of the category
        ancestors = category.get_ancestors()
        print("ancestors" + str(ancestors))

        # get descendants of the category, includes this category
        descendants = category.get_descendants(include_self=True)
        print("descendants" + str(descendants))

        # re-calculate n_i for this category, all ancestors and all descendants
        for cat in (ancestors | descendants):
            calc_items_in_cat_from_cat(cat)

            try:
                cat._dirty = True
                cat.save()
            finally:
                del cat._dirty



    print("end of calc_items_in_cat_from_thing")
'''


@receiver(post_save, sender='iotrec_api.Category')
def my_handler(sender, instance, **kwargs):
    # prevent recursion because this function itself modifies Category
    if hasattr(instance, '_dirty'):
        return

    # get ancestors of the category
    ancestors = instance.get_ancestors()

    # get descendants of the category, includes this category
    descendants = instance.get_descendants(include_self=True)

    # re-calculate n_i for this category, all ancestors and all descendants
    for cat in (ancestors | descendants).distinct():
        calc_items_in_cat_from_cat(cat)

        try:
            cat._dirty = True
            cat.save()
        finally:
            del cat._dirty