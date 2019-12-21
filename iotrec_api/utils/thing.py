import math
from datetime import datetime, timedelta
from enumchoicefield import ChoiceEnum
from mptt.utils import tree_item_iterator
from iotrec_api import models
from iotrec_api.utils.context import CrowdednessType
from django.apps import apps


class ThingType(ChoiceEnum):
    BCN_I = "Bluetooth iBeacon"
    BCN_EDDY = "Bluetooth Eddystone Beacon"


def get_thing_similarity(this_thing, ref_thing):
    # get all categories in the system
    categories_all = set(models.Category.objects.all())

    # get the categories that this_thing has directly assigned to it
    this_thing_categories_immediate = models.Category.objects.filter(thing=this_thing)
    this_thing_categories_all = this_thing_categories_immediate

    # get the categories that ref_thing has directly assigned to it
    ref_thing_categories_immediate = models.Category.objects.filter(referencething=ref_thing)
    ref_thing_categories_all = ref_thing_categories_immediate

    # get the ancestor categories of this_thing's immediate categories
    for node, meta in tree_item_iterator(this_thing_categories_immediate):
        this_thing_categories_all = (this_thing_categories_all | node.get_ancestors())

    # get the ancestor categories of ref_thing's immediate categories
    for node, meta in tree_item_iterator(ref_thing_categories_immediate):
        ref_thing_categories_all = (ref_thing_categories_all | node.get_ancestors())

    # merge category sets
    categories_of_both_all = (this_thing_categories_all | ref_thing_categories_all).distinct()

    # get distinct sets
    this_thing_categories_all = this_thing_categories_all.distinct()
    ref_thing_categories_all = ref_thing_categories_all.distinct()

    # coefficients for similarity measure
    divident = 0
    divisor_inner_this = 0
    divisor_inner_other = 0

    # for each category i
    for cat in categories_of_both_all:
        # term frequency is 1 if this_thing has category i, 0 otherwise
        tf_this_i = 1 if (cat in this_thing_categories_all) else 0

        # term frequency is 1 if ref_thing has category i, 0 otherwise
        tf_other_i = 1 if (cat in ref_thing_categories_all) else 0

        n_i = cat.nr_of_items_recursive
        if cat.is_root_node():
            n_p_i = n_i
        else:
            n_p_i = cat.parent.nr_of_items_recursive

        factor_this = tf_this_i * (math.log(n_p_i / (n_i + 1)) + 1)
        factor_other = tf_other_i * (math.log(n_p_i / (n_i + 1)) + 1)

        divident += factor_this * factor_other
        divisor_inner_this += factor_this * factor_this
        divisor_inner_other += factor_other * factor_other

    if math.sqrt(divisor_inner_this) * math.sqrt(divisor_inner_other) != 0:
        category_result = divident / (math.sqrt(divisor_inner_this) * math.sqrt(divisor_inner_other))
    else:
        category_result = 0

    locality_result = -1
    if this_thing.indoorsLocation is not None and ref_thing.indoorsLocation is not None:
        if this_thing.indoorsLocation == ref_thing.indoorsLocation:
            locality_result = 1
        else:
            locality_result = 0

    # calculate overall result using weights from settings
    if locality_result >= 0:
        settings = models.IotRecSettings.load()
        category_weight = settings.category_weight
        locality_weight = settings.locality_weight

        return category_weight * category_result + locality_weight * locality_result
    else:
        return category_result


def get_thing_user_similarity(this_thing, user):
    # get the preferences that the user has selected
    preferences_user = models.Preference.objects.filter(user=user)

    # get the categories that the thing has directly assigned to it
    categories_thing_immediate = models.Category.objects.filter(thing=this_thing)
    categories_thing = categories_thing_immediate
    # get the categories of the user's preferences
    categories_user_immediate = models.Category.objects.filter(preferences__user=user).exclude(preferences__value=0)
    categories_user = categories_user_immediate

    # get the ancestor categories of the thing's immediate categories
    for node, meta in tree_item_iterator(categories_thing):
        categories_thing = (categories_thing | node.get_ancestors())

    # get the ancestor categories of the user preferences' immediate categories
    for node, meta in tree_item_iterator(categories_user):
        categories_user = (categories_user | node.get_ancestors())

    categories_all = (categories_thing | categories_user).distinct()

    categories_thing = categories_thing.distinct()
    categories_user = categories_user.distinct()

    divident = 0
    divisor_inner_this = 0
    divisor_inner_other = 0

    # for each category i
    for cat in categories_thing:
        # term frequency is 1 if thing has category i, 0 otherwise
        tf_this_i = 1 if (cat in categories_thing) else 0
        # get term frequency of category in user preferences (1, -1 or 0)
        if cat in categories_user_immediate:
            # fetch the value from the preferences object
            cat_preference_value = preferences_user.filter(category=cat)[:1].get().value
            if cat_preference_value != 0:
                # check if category is directly part of a user preference and if yes, get the value
                tf_user_i = cat_preference_value
            else:
                tf_user_i = 0
        else:
            # check if a child category is a preference and...
            user_prefs_below_cat = set(cat.get_descendants(include_self=False).all()).intersection(categories_user_immediate)
            if len(user_prefs_below_cat) > 0:
                # ...if yes, build an average of the childrens' preferences values
                nr_of_user_prefs_below_cat = len(user_prefs_below_cat)
                values_of_user_prefs_below_cat = 0
                for i in user_prefs_below_cat:
                    # get the corresponding preference
                    pref = preferences_user.filter(category=i)[:1].get()
                    # add up the value
                    values_of_user_prefs_below_cat += pref.value
                tf_user_i = values_of_user_prefs_below_cat / nr_of_user_prefs_below_cat
            else:
                tf_user_i = 0

        # number of items classified in subtree for which the parent of i is the root
        # (loop through all descendants of that category, including itself, and add up the things count)
        n_i = cat.nr_of_items_recursive

        # if cat is the root node if the entire category tree, n_p_i equals n_i
        if cat.is_root_node():
            n_p_i = n_i
        else:
            # if not, use the parent's nr_of_items_recursive
            parent = cat.parent
            n_p_i = parent.nr_of_items_recursive

        # implement calculation of similarity measure
        factor_this = tf_this_i * (math.log(n_p_i / (n_i + 1)) + 1)
        factor_other = tf_user_i * (math.log(n_p_i / (n_i + 1)) + 1)

        divident += factor_this * factor_other
        divisor_inner_this += factor_this * factor_this
        divisor_inner_other += factor_other * factor_other

    if math.sqrt(divisor_inner_this) * math.sqrt(divisor_inner_other) != 0:
        result = divident / (math.sqrt(divisor_inner_this) * math.sqrt(divisor_inner_other))
    else:
        result = 0

    # normalize to interval [0, 1] (from [-1, 1])
    result = (result + 1) / 2
    return result


def get_context_fit(thing, context):
    ThingBaseline = apps.get_model('training.ThingBaseline')
    ContextBaseline = apps.get_model('training.ContextBaseline')

    # get the context factors that apply in given context object
    context_factors = []
    if context.crowdedness is not None and context.crowdedness.active_in_prediction:
        context_factors.append(context.crowdedness)
    if context.time_of_day is not None and context.time_of_day.active_in_prediction:
        context_factors.append(context.time_of_day)
    if context.temperature is not None and context.temperature.active_in_prediction:
        context_factors.append(context.temperature)
    if context.weather is not None and context.weather.active_in_prediction:
        context_factors.append(context.weather)
    if context.length_of_trip is not None and context.length_of_trip.active_in_prediction:
        context_factors.append(context.length_of_trip)

    # if no context is given, return -1, so context gets no weight
    if len(context_factors) == 0:
        return -1

    # variable to hold the overall context fit
    context_fit = 0

    # get the reference similarities of the given thing
    reference_similarities = models.SimilarityReference.objects.filter(thing=thing)

    # get sum of all reference similarities; needed for weighing the predictions later
    sum_of_reference_similarities = 0
    for rs in reference_similarities:
        sum_of_reference_similarities += rs.similarity

    if sum_of_reference_similarities > 0:
        weight_multiplicator = 1 / sum_of_reference_similarities
    else:
        weight_multiplicator = 0

    # for every reference similarity element, get the predicted rating and sum up the result with the correct weight
    for rs in reference_similarities:
        # get the thing baseline for the reference thing
        thing_baseline = ThingBaseline.objects.filter(reference_thing=rs.reference_thing)[:1].get().value

        # get all context baselines for the reference thing that apply (according to given context object)
        sum_of_context_baselines = 0
        for cf in context_factors:
            sum_of_context_baselines += ContextBaseline.objects.filter(
                context_factor=cf.context_factor,
                context_factor_value=cf,
                reference_thing=rs.reference_thing
            )[:1].get().value

        # sum up all baselines
        prediction = thing_baseline + sum_of_context_baselines

        # normalize prediction according to number of context factors
        normalized_prediction = (prediction + 1) / 2

        # calculate weight of this reference_similarity
        weight = rs.similarity * weight_multiplicator

        # add weighted contribution to context_fit
        context_fit += weight * normalized_prediction

    return context_fit


def get_utility(thing, user, context, context_active, preferences_active):
    if context_active:
        context_fit = get_context_fit(thing, context)
    else:
        context_fit = -1

    if preferences_active:
        thing_user_similarity = get_thing_user_similarity(thing, user)
    else:
        thing_user_similarity = -1

    settings = models.IotRecSettings.load()
    prediction_weight = settings.prediction_weight
    context_weight = settings.context_weight

    if thing_user_similarity >= 0 and context_fit >= 0:
        return thing_user_similarity, context_fit, (prediction_weight * thing_user_similarity + context_weight * context_fit)
    elif thing_user_similarity >= 0:
        return thing_user_similarity, 0, thing_user_similarity
    elif context_fit >= 0:
        return 0, context_fit, context_fit
    else:
        return 0, 0, 0


def get_crowdedness(thing):
    # calculate the time that (start, end) tuples of two things overlap
    def get_overlap_times_of_things(thing1, thing2):
        return get_overlap_times_of_times(thing1.start, thing2.start, thing1.last_checkin, thing2.last_checkin)

    def get_overlap_times_of_times(start1, start2, end1, end2):
        # overlap start is the later start time of the two times
        if start1 > start2:
            start = start1
        else:
            start = start2

        # overlap end is the earlier end time of the two times
        if end1 < end2:
            end = end1
        else:
            end = end2

        return start, end

    def find_overlaps(start, end, remaining_overlaps, counter):
        # recursively find overlaps within a given overlap
        for (i, j) in remaining_overlaps:
            ij_start, ij_end = get_overlap_times_of_things(i, j)
            # if overlap
            if ij_start <= end and start <= ij_end:
                remaining_overlaps.remove((i, j))
                if len(remaining_overlaps) > 0:
                    new_start, new_end = get_overlap_times_of_times(start, ij_start, end, ij_end)
                    return find_overlaps(new_start, new_end, o, counter + 1)
        return counter

    # get number of current stays
    nr_of_active_stays = models.Stay.objects.filter(thing=thing, end=None).count()

    # if there are no stays, return EMPTY
    if nr_of_active_stays == 0:
        return CrowdednessType.EMPTY

    # get the peak occupation (of the last 7 days)
    past_week = datetime.now() - timedelta(days=7)
    past_stays = models.Stay.objects.filter(thing=thing, start__gte=past_week).all()
    past_stays_list = list(past_stays)
    # keep a copy of the "original" list because past_stays_list will be modified
    past_stays_without_i = past_stays_list.copy()

    # collect all overlaps
    overlaps = []
    for i in past_stays_list:
        # remove a stay when it was checked
        past_stays_without_i.remove(i)
        for j in past_stays_without_i:
            # if overlap, add to overlaps set
            if i.start <= j.last_checkin and j.start <= i.last_checkin:
                overlaps.append((i, j))

    max_counter = 0

    # loop all overlaps found
    for i, j in overlaps:
        # continue with overlaps set that doesn't include (i, j) itself
        o = overlaps.copy()
        o.remove((i, j))
        # get the time period that the items actually overlap for
        o_start, o_end = get_overlap_times_of_things(i, j)
        # start recursive run that finds total number of overlaps within o_start and o_end
        overlaps_counter = find_overlaps(o_start, o_end, o, 1)
        # if a new maximum was found, save it
        if overlaps_counter > max_counter:
            max_counter = overlaps_counter

    nr_of_overlaps = max_counter
    nr_of_concurrent_stays = ((math.sqrt(8 * nr_of_overlaps + 1) - 1) / 2) + 1

    if nr_of_active_stays < (0.2 * nr_of_concurrent_stays):
        return CrowdednessType.EMPTY
    elif (0.2 * nr_of_concurrent_stays) <= nr_of_active_stays < (0.8 * nr_of_concurrent_stays):
        return CrowdednessType.MEDIUM_CROWDED
    else:
        return CrowdednessType.VERY_CROWDED