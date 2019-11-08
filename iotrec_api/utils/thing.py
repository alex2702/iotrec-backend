import math
from datetime import datetime, timedelta
from itertools import chain
from time import sleep

from django.db import connection
from django.db.models.signals import post_save, m2m_changed, post_delete
from django.dispatch import receiver
from django.utils import timezone
from enumchoicefield import ChoiceEnum
from mptt.utils import tree_item_iterator

from iotrec_api import models
from iotrec_api.utils.context import CrowdednessType
from django.apps import apps
from iotrec_api.utils import similarity_reference


class ThingType(ChoiceEnum):
    BCN_I = "Bluetooth iBeacon"
    BCN_EDDY = "Bluetooth Eddystone Beacon"


def get_thing_similarity(this_thing, ref_thing, *args, **kwargs):
    #print("get_thing_similarity - query marker 1: " + str(len(connection.queries)))

    '''
    # get all categories that "this_thing" is classified in
    this_thing_categories = this_thing.categories.all()
    this_thing_categories_count = this_thing.categories.count()

    this_thing_categories_all = set()
    for i in range(this_thing_categories_count):
        if this_thing_categories[i] not in this_thing_categories_all:
            this_thing_categories_all.add(this_thing_categories[i])
        i_ancestors = this_thing_categories[i].get_ancestors()
        for j in range(len(i_ancestors)):
            if i_ancestors[j] not in this_thing_categories_all:
                this_thing_categories_all.add(i_ancestors[j])

    # get all categories that "other" is classified in
    ref_thing_categories = ref_thing.categories.all()
    ref_thing_categories_count = ref_thing.categories.count()

    ref_thing_categories_all = set()
    for i in range(ref_thing_categories_count):
        if ref_thing_categories[i] not in ref_thing_categories_all:
            ref_thing_categories_all.add(ref_thing_categories[i])
        i_ancestors = ref_thing_categories[i].get_ancestors()
        for j in range(len(i_ancestors)):
            if i_ancestors[j] not in ref_thing_categories_all:
                ref_thing_categories_all.add(i_ancestors[j])

    # merge the category lists
    categories_all = this_thing_categories_all.union(ref_thing_categories_all)
    '''

    categories_all = set(models.Category.objects.all())
    this_thing_categories_immediate = models.Category.objects.filter(thing=this_thing)
    this_thing_categories_all = this_thing_categories_immediate
    ref_thing_categories_immediate = models.Category.objects.filter(referencething=ref_thing)
    ref_thing_categories_all = ref_thing_categories_immediate

    #print("get_thing_similarity - query marker 2: " + str(len(connection.queries)))

    for node, meta in tree_item_iterator(this_thing_categories_immediate):
        this_thing_categories_all = (this_thing_categories_all | node.get_ancestors())

    #print("get_thing_similarity - query marker 3: " + str(len(connection.queries)))

    for node, meta in tree_item_iterator(ref_thing_categories_immediate):
        ref_thing_categories_all = (ref_thing_categories_all | node.get_ancestors())

    #print("get_thing_similarity - query marker 4: " + str(len(connection.queries)))

    categories_of_both_all = (this_thing_categories_all | ref_thing_categories_all).distinct()

    this_thing_categories_all = this_thing_categories_all.distinct()
    ref_thing_categories_all = ref_thing_categories_all.distinct()

    #print("thing=" + str(this_thing))
    #print("ref_thing=" + str(ref_thing))
    #print("this_thing_categories_immediate=" + str(this_thing_categories_immediate))
    #print("this_thing_categories_all=" + str(this_thing_categories_all))
    #print("ref_thing_categories_immediate=" + str(ref_thing_categories_immediate))
    #print("ref_thing_categories_all=" + str(ref_thing_categories_all))
    #print("categories_all=" + str(categories_all))

    #print("get_thing_similarity - query marker 5: " + str(len(connection.queries)))

    divident = 0
    divisor_inner_this = 0
    divisor_inner_other = 0

    #print("get_thing_similarity - query marker 6: " + str(len(connection.queries)))
    #print(categories_all)

    # for each category i
    for cat in categories_of_both_all:
    #for cat in this_thing_categories_all:
    #for cat in categories_all:
        #print("get_thing_similarity - query marker 6.1: " + str(len(connection.queries)))
        #print("checking cat " + str(cat))
        #print("query marker 4.1: " + str(len(connection.queries)))
        # 1 if self has category i, 0 otherwise
        tf_this_i = 1 if (cat in this_thing_categories_all) else 0

        #print("get_thing_similarity - query marker 6.2: " + str(len(connection.queries)))

        # 1 if other has category i, 0 otherwise
        tf_other_i = 1 if (cat in ref_thing_categories_all) else 0

        #print("get_thing_similarity - query marker 6.3: " + str(len(connection.queries)))

        '''
        # number of items classified in subtree for which the parent of i is the root
        # (loop through all descendants of that category, including itself, and add up the things count)
        subtree_root = None
        if cat.is_root_node():
            subtree_root = cat
        else:
            subtree_root = cat.get_ancestors(ascending=True)[0]

        print("query marker 4.2: " + str(len(connection.queries)))

        n_p_i = 0
        n_p_i_things_counted = set()  # prevent counting a thing multiple times
        for sub_cat in subtree_root.get_descendants(include_self=True):
            print("query marker 4.3: " + str(len(connection.queries)))
            if sub_cat.thing_set.count() > 0:
                sub_cat_things = set(sub_cat.thing_set.all())
                n_p_i += len((sub_cat_things - n_p_i_things_counted))
                n_p_i_things_counted = n_p_i_things_counted.union(sub_cat_things)

        print("query marker 4.4: " + str(len(connection.queries)))

        # number of items classified in subtree for which i is the root
        # (loop through all descendants of that category, including itself, and add up the things count)
        n_i = 0
        n_i_things_counted = set()  # prevent counting a thing multiple times
        for sub_cat in cat.get_descendants(include_self=True):
            print("query marker 4.5: " + str(len(connection.queries)))
            if sub_cat.thing_set.count() > 0:
                sub_cat_things = set(sub_cat.thing_set.all())
                n_i += len((sub_cat_things - n_i_things_counted))
                n_i_things_counted = n_i_things_counted.union(sub_cat_things)
        '''

        #n_i = cat.nr_of_items_recursive + tf_other_i
        n_i = cat.nr_of_items_recursive
        #n_i = cat.nr_of_items_recursive + 1
        if cat.is_root_node():
            n_p_i = n_i
        else:
            #n_p_i = cat.parent.nr_of_items_recursive + tf_other_i
            n_p_i = cat.parent.nr_of_items_recursive
            #n_p_i = cat.parent.nr_of_items_recursive + 1

        #print("get_thing_similarity - query marker 6.4: " + str(len(connection.queries)))

        #print("query marker 4.6: " + str(len(connection.queries)))

        #print("cat=" + str(cat) + ", tf_this_i=" + str(tf_this_i) + ", tf_other_i=" + str(tf_other_i) + ", n_p_i=" + str(n_p_i) + ", n_i=" + str(n_i))

        #factor_this = tf_this_i * math.log(n_p_i / n_i)
        #factor_other = tf_other_i * math.log(n_p_i / n_i)
        factor_this = tf_this_i * (math.log(n_p_i / (n_i + 1)) + 1)
        factor_other = tf_other_i * (math.log(n_p_i / (n_i + 1)) + 1)

        divident += factor_this * factor_other
        divisor_inner_this += factor_this * factor_this
        divisor_inner_other += factor_other * factor_other

        #print("get_thing_similarity - query marker 6.5: " + str(len(connection.queries)))

    #print("get_thing_similarity - query marker 7: " + str(len(connection.queries)))

    if math.sqrt(divisor_inner_this) * math.sqrt(divisor_inner_other) != 0:
        category_result = divident / (math.sqrt(divisor_inner_this) * math.sqrt(divisor_inner_other))
    else:
        category_result = 0

    # normalize to interval [0, 1] (from [-1, 1])
    #result = (result + 1) / 2 # shouldn't be necessary because things don't have anti-preferences

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


def get_thing_user_similarity(this_thing, user, *args, **kwargs):
    #print("===================")
    #print(str(timezone.now()) + " get_thing_user_similarity started")

    '''
    print(str("timer 1: " + str(timezone.now())))

    # get all categories that "this_thing" is classified in (i.e. also children)
    #this_thing_categories = this_thing.categories.all()
    this_thing_categories = models.Category.objects.filter(thing=this_thing)
    this_thing_categories_count = this_thing_categories.count()
    this_thing_categories_all = set()
    for i in range(this_thing_categories_count):
        if this_thing_categories[i] not in this_thing_categories_all:
            this_thing_categories_all.add(this_thing_categories[i])
        i_ancestors = this_thing_categories[i].get_ancestors()
        for j in range(len(i_ancestors)):
            if i_ancestors[j] not in this_thing_categories_all:
                this_thing_categories_all.add(i_ancestors[j])

    print("length of this_thing_categories_all is " + str(this_thing_categories_all))
    print(str(timezone.now()) + " get_thing_user_similarity - marker 1")

    # get all categories that "user" is classified in (from their preferences)
    #user_preferences = user.preferences.all()
    #user_categories = Category.objects.filter()

    user_categories = set(models.Category.objects.filter(preferences__user=user).exclude(preferences__value=0))
    #user_categories = set()
    #for i in user_preferences:
    #    if i.value != 0:
    #        user_categories.add(i.category)
    #        print(str(i.category.preferences.filter(user=user).exclude(value=0)))

    print(str(timezone.now()) + " get_thing_user_similarity - marker 2")

    # get children of those categories
    user_categories_all = set()
    for i in user_categories:
        if i not in user_categories_all:
            user_categories_all.add(i)
        i_ancestors = i.get_ancestors()
        for j in range(len(i_ancestors)):
            if i_ancestors[j] not in user_categories_all:
                user_categories_all.add(i_ancestors[j])

    #print("user.categories")
    #print(str(this_thing.categories))
    #print(tree_item_iterator(this_thing.categories))
    print("length of user_categories_all is " + str(user_categories_all))
    
    # merge the category lists
    categories_all = this_thing_categories_all.union(user_categories_all)

    print(str("timer 2: " + str(timezone.now())))
    '''

    #print(str(timezone.now()) + " get_thing_user_similarity - marker 1")

    preferences_user = models.Preference.objects.filter(user=user)
    #print("query marker 1: " + str(len(connection.queries)))

    categories_thing_immediate = models.Category.objects.filter(thing=this_thing)
    categories_thing = categories_thing_immediate
    categories_user_immediate = models.Category.objects.filter(preferences__user=user).exclude(preferences__value=0)
    categories_user = categories_user_immediate

    for node, meta in tree_item_iterator(categories_thing):
        categories_thing = (categories_thing | node.get_ancestors())

    for node, meta in tree_item_iterator(categories_user):
        categories_user = (categories_user | node.get_ancestors())

    categories_all = (categories_thing | categories_user).distinct()

    categories_thing = categories_thing.distinct()
    categories_user = categories_user.distinct()

    #print(str(timezone.now()) + " get_thing_user_similarity - marker 2")

    #print(str(categories_thing_immediate))
    #print(str(categories_thing))
    #print(str(categories_user_immediate))
    #print(str(categories_user))
    #print(str(categories_all))

    #print(str(timezone.now()) + " get_thing_user_similarity - marker 4")

    divident = 0
    divisor_inner_this = 0
    divisor_inner_other = 0

    # for each category i
    #for cat in categories_all:
    for cat in categories_thing:
        #print("query marker 2: " + str(len(connection.queries)))
        # 1 if thing has category i, 0 otherwise
        tf_this_i = 1 if (cat in categories_thing) else 0
        # 1 or -1 if user has category i, 0 otherwise
        # get frequency of category in user preferences
        if cat in categories_user_immediate:
            cat_preference_value = preferences_user.get(category=cat).value
            if cat_preference_value != 0:
                # check if category is directly part of a user preference and if yes, get the value
                tf_user_i = cat_preference_value
        else:
            # check if a child category is a preference and...
            user_prefs_below_cat = set(cat.get_descendants(include_self=False).all()).intersection(categories_user_immediate)
            if len(user_prefs_below_cat) > 0:
                # ...if yes, build an average of the childrens' preferences values
                nr_of_user_prefs_below_cat = len(user_prefs_below_cat)
                values_of_user_prefs_below_cat = 0
                for i in user_prefs_below_cat:
                    # get the corresponding preference
                    pref = preferences_user.get(category=i)
                    # add up the value
                    values_of_user_prefs_below_cat += pref.value
                tf_user_i = values_of_user_prefs_below_cat / nr_of_user_prefs_below_cat
            else:
                tf_user_i = 0

        # number of items classified in subtree for which the parent of i is the root
        # (loop through all descendants of that category, including itself, and add up the things count)
        n_i = cat.nr_of_items_recursive
        #if ((cat.get_descendants(include_self=True).distinct() & categories_user.distinct())).count() > 0:
        #    n_i += 1 # increase because user has one of the categories

        if cat.is_root_node():
            n_p_i = n_i
        else:
            parent = cat.parent
            n_p_i = parent.nr_of_items_recursive
            #if ((parent.get_descendants(include_self=True).distinct() & categories_user.distinct())).count() > 0:
            #    n_p_i += 1  # increase because user has one of the categories

        #print("cat=" + str(cat) + ", tf_this_i=" + str(tf_this_i) + ", tf_user_i=" + str(tf_user_i) + ", n_p_i=" + str(n_p_i) + ", n_i=" + str(n_i))

        #factor_this = tf_this_i * math.log(n_p_i / n_i)
        #factor_other = tf_user_i * math.log(n_p_i / n_i)
        factor_this = tf_this_i * (math.log(n_p_i / (n_i + 1)) + 1)
        factor_other = tf_user_i * (math.log(n_p_i / (n_i + 1)) + 1)

        divident += factor_this * factor_other
        divisor_inner_this += factor_this * factor_this
        divisor_inner_other += factor_other * factor_other

        #print("divident is now " + str(divident))
        #print("divisor_inner_this is now " + str(divisor_inner_this))
        #print("divisor_inner_other is now " + str(divisor_inner_other))

        #print("get_thing_user_similarity: tf_thing_i=" + str(tf_this_i) + ", tf_user_i=" + str(
        #    tf_user_i) + ", factor_thing=" + str(factor_this) + ", factor_user=" + str(factor_other))

    #print("query marker 8: " + str(len(connection.queries)))
    #print(str(timezone.now()) + " get_thing_user_similarity - marker 5")

    if math.sqrt(divisor_inner_this) * math.sqrt(divisor_inner_other) != 0:
        result = divident / (math.sqrt(divisor_inner_this) * math.sqrt(divisor_inner_other))
        #print("get_thing_user_similarity end: divident=" + str(divident) + ", divisor_inner_this=" + str(
        #    divisor_inner_this) + ", divisor_inner_other=" + str(divisor_inner_other) + ", result=" + str((result + 1) / 2))
    else:
        result = 0

    #print(str(timezone.now()) + " get_thing_user_similarity - marker 6")

    # normalize to interval [0, 1] (from [-1, 1])
    result = (result + 1) / 2
    #print("===================")
    return result


def get_context_fit(thing, context):
    #print(str(timezone.now()) + " get_context_fit started")
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

    #print("get_context_fit: reference_similarities = " + str(reference_similarities))

    # needed for weighing predictions
    sum_of_reference_similarities = 0
    for rs in reference_similarities:
        sum_of_reference_similarities += rs.similarity

    #print("get_context_fit: sum_of_reference_similarities = " + str(sum_of_reference_similarities))

    if sum_of_reference_similarities > 0:
        weight_multiplicator = 1 / sum_of_reference_similarities
    else:
        weight_multiplicator = 0

    # for every reference similarity element, get the predicted rating and sum up the result with the correct weight
    for rs in reference_similarities:
        thing_baseline = ThingBaseline.objects.get(reference_thing=rs.reference_thing).value
        #print("get_context_fit: thing_baseline(" + str(rs.reference_thing.title) + ") = " + str(thing_baseline))

        #print("get_context_fit: context_factors(" + str(rs.reference_thing.title) + ") = " + str(context_factors))

        sum_of_context_baselines = 0
        for cf in context_factors:
            sum_of_context_baselines += ContextBaseline.objects.get(
                context_factor=cf.context_factor,
                context_factor_value=cf,
                reference_thing=rs.reference_thing
            ).value

        #print("get_context_fit: sum_of_context_baselines(" + str(rs.reference_thing.title) + ") = " + str(sum_of_context_baselines))

        prediction = thing_baseline + sum_of_context_baselines

        #print("get_context_fit: prediction(" + str(rs.reference_thing.title) + ") = " + str(prediction))

        # normalize prediction according to number of context factors
        #minimum_rating = -1 * len(context_factors)
        #maximum_rating = len(context_factors)
        #normalized_rating = (prediction - minimum_rating) / (maximum_rating - minimum_rating)
        normalized_prediction = (prediction + 1) / 2

        #print("get_context_fit: minimum_rating(" + str(rs.reference_thing.title) + ") = " + str(minimum_rating))
        #print("get_context_fit: maximum_rating(" + str(rs.reference_thing.title) + ") = " + str(maximum_rating))
        #print("get_context_fit: normalized_prediction(" + str(rs.reference_thing.title) + ") = " + str(normalized_prediction))

        # calculate weight of this reference_similarity
        weight = rs.similarity * weight_multiplicator

        # add weighted contribution to context_fit
        context_fit += weight * normalized_prediction

    #print("get_context_fit end: context_fit = " + str(context_fit))

    return context_fit


def get_utility(thing, user, context):
    #print(str(timezone.now()) + " get_utility started")
    thing_user_similarity = get_thing_user_similarity(thing, user)
    #print("thing_user_similarity: " + str(thing_user_similarity))
    #print(str(timezone.now()) + " thing_user_similarity returned")
    context_fit = get_context_fit(thing, context)
    #print("context_fit: " + str(context_fit))
    #print(str(timezone.now()) + " context_fit returned")

    settings = models.IotRecSettings.load()
    prediction_weight = settings.prediction_weight
    context_weight = settings.context_weight

    if thing_user_similarity >= 0 and context_fit >= 0:
        #print(str(timezone.now()) + " get_utility returned")
        return thing_user_similarity, context_fit, (prediction_weight * thing_user_similarity + context_weight * context_fit)
    elif thing_user_similarity >= 0:
        #print(str(timezone.now()) + " get_utility returned")
        return thing_user_similarity, 0, (prediction_weight * thing_user_similarity)
    elif context_fit >= 0:
        #print(str(timezone.now()) + " get_utility returned")
        return 0, context_fit, (context_weight * context_fit)
    else:
        #print(str(timezone.now()) + " get_utility returned")
        return 0, 0, 0



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