from django.db.models.signals import post_save
from django.dispatch import receiver
from iotrec_api import models


def calc_items_in_cat_full():
    """
    Loops through all categories in the database.
    For each category, calculate the number of Things categorized in the tree for which the current category is the
    parent.
    Return the number of categories for which the calculation was performed. Useful for logging and to check if all
    categories were calculated.

    Returns
    -------
    categories_saved : int
    """
    categories_saved = 0
    for cat in models.Category.objects.all():
        calc_items_in_cat_from_cat(cat)

        # mark processed categories as dirty, so they are not processed again
        try:
            cat._dirty = True
            cat.save()
            categories_saved += 1
        finally:
            del cat._dirty

    return categories_saved


def calc_items_in_cat_list(list):
    """
    For every category in list, calculate the number of Things categorized in the tree for which the respective category
    is the parent.

    Parameters
    ----------
    list : list of category
    """
    cats_to_recalc = set()
    for cat in list:
        # add ancestors and descendants to recalc list
        cats_to_recalc = (cats_to_recalc | set(cat.get_ancestors()) | set(cat.get_descendants(include_self=True)))

    # do recalculation
    for cat in cats_to_recalc:
        calc_items_in_cat_from_cat(cat)

        # mark processed categories as dirty, so they are not processed again
        try:
            cat._dirty = True
            cat.save()
        finally:
            del cat._dirty


def calc_items_in_cat_from_cat(category):
    """
    For a given category, get all categories that descend from it (including the category itself).
    Then loop all categories and find the Things that are contained in this category tree.
    For the given category, set the number of Things that are categorized in the tree of which category is the parent

    Parameters
    ----------
    category : Category
    """
    n_i_things_counted = set()  # keep track of things counted and prevent counting a thing multiple times
    for sub_cat in category.get_descendants(include_self=True):
        # only go on if the sub_cat has things at all, saves time
        if sub_cat.thing_set.count() > 0:
            sub_cat_things = set(sub_cat.thing_set.all())
            # merge Things counted so far and newly found Things
            n_i_things_counted = n_i_things_counted.union(sub_cat_things)

    # set the number of Things that are categorized in the tree of which category is the parent
    category.nr_of_items_recursive = len(n_i_things_counted)


# whenever a Category is saved, run this
@receiver(post_save, sender='iotrec_api.Category')
def my_handler(sender, instance, **kwargs):
    # prevent recursion because this function itself modifies the Category again
    # instances that have the _dirty attribute set won't be processed again
    if hasattr(instance, '_dirty'):
        return

    # get ancestors of the category
    ancestors = instance.get_ancestors()

    # get descendants of the category, includes this category
    descendants = instance.get_descendants(include_self=True)

    # re-calculate n_i for this category, all ancestors and all descendants
    for cat in (ancestors | descendants).distinct():
        calc_items_in_cat_from_cat(cat)

        # remove _dirty flag
        try:
            cat._dirty = True
            cat.save()
        finally:
            del cat._dirty