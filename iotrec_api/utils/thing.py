import math
from datetime import datetime, timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from enumchoicefield import ChoiceEnum

from iotrec_api import models
from iotrec_api.utils.context import CrowdednessType
from django.apps import apps
from iotrec_api.utils import similarity_reference


class ThingType(ChoiceEnum):
    BCN_I = "Bluetooth iBeacon"
    BCN_EDDY = "Bluetooth Eddystone Beacon"


def get_thing_similarity(this_thing, other_thing, *args, **kwargs):
    # get all categories that "this_thing" is classified in
    this_thing_categories = this_thing.categories.all()
    this_thing_categories_all = set()
    for i in range(len(this_thing_categories)):
        if this_thing_categories[i] not in this_thing_categories_all:
            this_thing_categories_all.add(this_thing_categories[i])
        i_ancestors = this_thing_categories[i].get_ancestors()
        for j in range(len(i_ancestors)):
            if i_ancestors[j] not in this_thing_categories_all:
                this_thing_categories_all.add(i_ancestors[j])

    # get all categories that "other" is classified in
    other_thing_categories = other_thing.categories.all()

    other_thing_categories_all = set()
    for i in range(len(other_thing_categories)):
        if other_thing_categories[i] not in other_thing_categories_all:
            other_thing_categories_all.add(other_thing_categories[i])
        i_ancestors = other_thing_categories[i].get_ancestors()
        for j in range(len(i_ancestors)):
            if i_ancestors[j] not in other_thing_categories_all:
                other_thing_categories_all.add(i_ancestors[j])

    # merge the category lists
    categories_all = this_thing_categories_all.union(other_thing_categories_all)

    divident = 0
    divisor_inner_this = 0
    divisor_inner_other = 0

    # for each category i
    for cat in categories_all:
        # 1 if self has category i, 0 otherwise
        tf_this_i = 1 if (cat in this_thing_categories_all) else 0

        # 1 if other has category i, 0 otherwise
        tf_other_i = 1 if (cat in other_thing_categories_all) else 0

        # number of items classified in subtree for which the parent of i is the root
        # (loop through all descendants of that category, including itself, and add up the things count)
        subtree_root = None
        if cat.is_root_node():
            subtree_root = cat
        else:
            subtree_root = cat.get_ancestors(ascending=True)[0]

        n_p_i = 0
        n_p_i_things_counted = set()  # prevent counting a thing multiple times
        for sub_cat in subtree_root.get_descendants(include_self=True):
            n_p_i += len((set(sub_cat.thing_set.all()) - n_p_i_things_counted))
            n_p_i_things_counted = n_p_i_things_counted.union(set(sub_cat.thing_set.all()))

        # number of items classified in subtree for which i is the root
        # (loop through all descendants of that category, including itself, and add up the things count)
        n_i = 0
        n_i_things_counted = set()  # prevent counting a thing multiple times
        for sub_cat in cat.get_descendants(include_self=True):
            n_i += len((set(sub_cat.thing_set.all()) - n_i_things_counted))
            n_i_things_counted = n_i_things_counted.union(set(sub_cat.thing_set.all()))

        factor_this = tf_this_i * math.log(n_p_i / n_i)
        factor_other = tf_other_i * math.log(n_p_i / n_i)

        divident += factor_this * factor_other
        divisor_inner_this += factor_this * factor_this
        divisor_inner_other += factor_other * factor_other

    if math.sqrt(divisor_inner_this) * math.sqrt(divisor_inner_other) != 0:
        category_result = divident / (math.sqrt(divisor_inner_this) * math.sqrt(divisor_inner_other))
    else:
        category_result = 0

    # normalize to interval [0, 1] (from [-1, 1])
    #result = (result + 1) / 2 # shouldn't be necessary because things don't have anti-preferences

    locality_result = -1
    if this_thing.indoorsLocation is not None and other_thing.indoorsLocation is not None:
        if this_thing.indoorsLocation == other_thing.indoorsLocation:
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


def get_thing_user_similarity(this_thing, user, *args, **kwargs):
    print(str(timezone.now()) + " get_thing_user_similarity started")

    # get all categories that "this_thing" is classified in (i.e. also children)
    this_thing_categories = this_thing.categories.all()
    this_thing_categories_all = set()
    for i in range(len(this_thing_categories)):
        if this_thing_categories[i] not in this_thing_categories_all:
            this_thing_categories_all.add(this_thing_categories[i])
        i_ancestors = this_thing_categories[i].get_ancestors()
        for j in range(len(i_ancestors)):
            if i_ancestors[j] not in this_thing_categories_all:
                this_thing_categories_all.add(i_ancestors[j])

    # get all categories that "user" is classified in (from their preferences)
    user_preferences = user.preferences.all()
    user_categories = set()
    for i in user_preferences:
        if i.value != 0:
            user_categories.add(i.category)

    # get children of those categories
    user_categories_all = set()
    for i in user_categories:
        if i not in user_categories_all:
            user_categories_all.add(i)
        i_ancestors = i.get_ancestors()
        for j in range(len(i_ancestors)):
            if i_ancestors[j] not in user_categories_all:
                user_categories_all.add(i_ancestors[j])

    # merge the category lists
    categories_all = this_thing_categories_all.union(user_categories_all)

    divident = 0
    divisor_inner_this = 0
    divisor_inner_other = 0

    # for each category i
    for cat in categories_all:
        # 1 if self has category i, 0 otherwise
        tf_this_i = 1 if (cat in this_thing_categories_all) else 0

        # 1 or -1 if user has category i, 0 otherwise
        # get frequency of category in user preferences
        if len(user.preferences.filter(category=cat)) > 0 and user.preferences.get(category=cat).value != 0:
            # check if category is directly part of a user preference and if yes, get the value
            tf_user_i = user.preferences.get(category=cat).value
            # print(cat)
            # print(tf_user_i)
        else:
            # check if a child category is a preference and
            user_prefs_below_cat = set(cat.get_descendants(include_self=False).all()).intersection(user_categories)
            if len(user_prefs_below_cat) > 0:
                # if yes, build an average of the childrens' preferences values
                # print(str(user_prefs_below_cat))
                nr_of_user_prefs_below_cat = len(user_prefs_below_cat)
                values_of_user_prefs_below_cat = 0
                for i in user_prefs_below_cat:
                    # get the corresponding preference
                    pref = user.preferences.get(category=i)
                    # add up the value
                    values_of_user_prefs_below_cat += pref.value
                tf_user_i = values_of_user_prefs_below_cat / nr_of_user_prefs_below_cat
            else:
                tf_user_i = 0

        # TODO is this true?
        # this approach is missing tf_user_i for the parents of preferences
        # because parents are not selected in the profile
        # idea: on every category, check if a child category is a preference
        # if yes, build an average of the childrens' preferences values

        # number of items classified in subtree for which the parent of i is the root
        # (loop through all descendants of that category, including itself, and add up the things count)
        subtree_root = None
        if cat.is_root_node():
            subtree_root = cat
        else:
            subtree_root = cat.get_ancestors(ascending=True)[0]
        # if cat.text_id != "Root":
        #    subtree_root = cat.get_ancestors(ascending=True)[0]
        # else:
        #    subtree_root = cat

        n_p_i = 0
        user_flag = 0  # prevent counting the user multiple times
        n_p_i_things_counted = set()  # prevent counting a thing multiple times
        for sub_cat in subtree_root.get_descendants(include_self=True):
            # check if user has that preference
            if sub_cat in user_categories:
                user_flag = 1
            n_p_i += len((set(sub_cat.thing_set.all()) - n_p_i_things_counted))
            n_p_i_things_counted = n_p_i_things_counted.union(set(sub_cat.thing_set.all()))

        if user_flag == 1:
            n_p_i += 1

        # number of items classified in subtree for which i is the root
        # (loop through all descendants of that category, including itself, and add up the things count)
        n_i = 0
        user_flag = 0  # prevent counting the user multiple times
        n_i_things_counted = set()  # prevent counting a thing multiple times
        for sub_cat in cat.get_descendants(include_self=True):
            # check if user has that preference
            if sub_cat in user_categories:
                user_flag = 1
            n_i += len((set(sub_cat.thing_set.all()) - n_i_things_counted))
            n_i_things_counted = n_i_things_counted.union(set(sub_cat.thing_set.all()))

        if user_flag == 1:
            n_i += 1

        factor_this = tf_this_i * math.log(n_p_i / n_i)
        factor_other = tf_user_i * math.log(n_p_i / n_i)

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
    print(str(timezone.now()) + " get_context_fit started")
    ThingBaseline = apps.get_model('training.ThingBaseline')
    ContextBaseline = apps.get_model('training.ContextBaseline')

    # get the context factors
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

    # variable hold the overall context fit
    context_fit = 0

    # get the reference similarities of the given thing
    reference_similarities = models.SimilarityReference.objects.filter(thing=thing)

    # needed for weighing predictions
    sum_of_reference_similarities = 0
    for rs in reference_similarities:
        sum_of_reference_similarities += rs.similarity

    if sum_of_reference_similarities > 0:
        weight_multiplicator = 1 / sum_of_reference_similarities
    else:
        weight_multiplicator = 0

    # for every reference similarity element, get the predicted rating and sum up the result with the correct weight
    for rs in reference_similarities:
        thing_baseline = ThingBaseline.objects.get(reference_thing=rs.reference_thing).value

        sum_of_context_baselines = 0
        for cf in context_factors:
            sum_of_context_baselines += ContextBaseline.objects.get(
                context_factor=cf.context_factor,
                context_factor_value=cf,
                reference_thing=rs.reference_thing
            ).value

        prediction = thing_baseline + sum_of_context_baselines

        # normalize prediction according to number of context factors
        minimum_rating = -1 * len(context_factors)
        maximum_rating = len(context_factors)
        normalized_rating = (prediction - minimum_rating) / (maximum_rating - minimum_rating)

        # calculate weight of this reference_similarity
        weight = rs.similarity * weight_multiplicator

        # add weighted contribution to context_fit
        context_fit += weight * normalized_rating

    return context_fit


def get_utility(thing, user, context):
    print(str(timezone.now()) + " get_utility started")
    thing_user_similarity = get_thing_user_similarity(thing, user)
    print(str(timezone.now()) + " thing_user_similarity returned")
    context_fit = get_context_fit(thing, context)
    print(str(timezone.now()) + " context_fit returned")

    settings = models.IotRecSettings.load()
    prediction_weight = settings.prediction_weight
    context_weight = settings.context_weight

    if thing_user_similarity >= 0 and context_fit >= 0:
        print(str(timezone.now()) + " get_utility returned")
        return prediction_weight * thing_user_similarity + context_weight * context_fit
    elif thing_user_similarity >= 0:
        print(str(timezone.now()) + " get_utility returned")
        return prediction_weight * thing_user_similarity
    elif context_fit >= 0:
        print(str(timezone.now()) + " get_utility returned")
        return context_weight * context_fit
    else:
        print(str(timezone.now()) + " get_utility returned")
        return 0



def get_crowdedness(thing):
    def get_overlap_times_of_things(thing1, thing2):
        # overlap start is the later start time of the two stays
        if thing1.start > thing2.start:
            start = thing1.start
        else:
            start = thing2.start

        # overlap end is the earlier end time of the two stays
        if thing1.last_checkin < thing2.last_checkin:
            end = thing1.last_checkin
        else:
            end = thing2.last_checkin

        return start, end

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
    past_stays_without_i = past_stays_list.copy()

    # collect all overlaps
    overlaps = []
    for i in past_stays_list:
        past_stays_without_i.remove(i)
        for j in past_stays_without_i:
            # print("j is now " + str(j))
            # if overlap
            if i.start <= j.last_checkin and j.start <= i.last_checkin: #and i != j and (j, i) not in overlaps:
                overlaps.append((i, j))

    max_counter = 0

    for i, j in overlaps:
        # continue with overlaps set that doesn't include (i, j) itself
        o = overlaps.copy()
        o.remove((i, j))
        # get the time period that the items actually overlap for
        o_start, o_end = get_overlap_times_of_things(i, j)
        overlaps_counter = find_overlaps(o_start, o_end, o, 1)
        if overlaps_counter > max_counter:
            max_counter = overlaps_counter

    nr_of_overlaps = max_counter
    nr_of_concurrent_stays = ((math.sqrt(8 * nr_of_overlaps + 1) - 1) / 2) + 1

    #return nr_of_overlaps, nr_of_concurrent_stays

    if nr_of_active_stays < (0.2 * nr_of_concurrent_stays):
        return CrowdednessType.EMPTY
    elif (0.2 * nr_of_concurrent_stays) <= nr_of_active_stays < (0.8 * nr_of_concurrent_stays):
        return CrowdednessType.MEDIUM_CROWDED
    else:
        return CrowdednessType.VERY_CROWDED


@receiver(post_save, sender='iotrec_api.Thing')
def my_handler(sender, instance, **kwargs):
    similarity_reference.calculate_similarity_references_per_thing(instance)
