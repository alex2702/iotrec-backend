import datetime
import random

import scipy.stats
from django.contrib import messages
from django.db.models import Avg
from django.forms import model_to_dict
from django.shortcuts import render, redirect

from training.forms import SampleForm
from training.models import TrainingUser, ReferenceThing, ContextFactor, Sample


def is_combination_unambiguous(thing, context_factor, context_factor_value, min_nr_of_samples):
    # check if we already have an unambiguous influence on the given thing/context_factor/cf_value combination
    samples = Sample.objects.filter(thing=thing, context_factor=context_factor,
                                    context_factor_value=context_factor_value)
    # we need at least min_nr_of_samples samples
    if len(samples) >= min_nr_of_samples:
        # check if all values in the samples are identical
        all_values_identical = True
        value_of_sample_1 = samples[0].value
        for sample in samples:
            if sample.value != value_of_sample_1:
                all_values_identical = False
                break
        return all_values_identical
    return False


# do a one-sample two-tailed t-test
def is_combination_significant(thing, context_factor, context_factor_value, min_nr_of_samples):
    # check if we already have a significant influence on the given thing/context_factor/cf_value combination
    samples = Sample.objects.filter(thing=thing, context_factor=context_factor,
                                    context_factor_value=context_factor_value)

    # we need at least min_nr_of_samples samples
    if len(samples) >= min_nr_of_samples:
        # get the values from all samples
        values = []
        for sample in samples:
            values.append(sample.value)

        # do the t-test
        ttest_results = scipy.stats.ttest_1samp(values, 0)
        p_value = ttest_results[1]

        # check if significant and return
        return p_value
        #return p_value <= 0.05
    return -1
    #return False


# checks if a combination should be asked to the given user, depending on three criteria
# - combination should not be ambiguous already
# - combination should not be significant already
# - combination should not be answered by the same user already
def is_combination_qualified(user, thing, context_factor, context_factor_value):
    # has the user answered that combination already?
    samples = Sample.objects.filter(user=user, thing=thing, context_factor=context_factor,
                                    context_factor_value=context_factor_value)

    if len(samples) > 0:
        return False

    if is_combination_unambiguous(thing, context_factor, context_factor_value):
        return False

    if 0 <= is_combination_significant(thing, context_factor, context_factor_value, 6) <= 0.1:
        return False

    return True


def add_sample(request, context_factor=None):
    if request.method == "POST":
        form = SampleForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            print(form_data)
            sample_1 = Sample(
                thing_id=form_data['thing'],
                context_factor_id=form_data['context_factor_1'],
                context_factor_value_id=form_data['context_factor_value_1'],
                value=form_data['value_1'],
                user_id=form_data['user']
            )
            sample_2 = Sample(
                thing_id=form_data['thing'],
                context_factor_id=form_data['context_factor_2'],
                context_factor_value_id=form_data['context_factor_value_2'],
                value=form_data['value_2'],
                user_id=form_data['user']
            )
            sample_3 = Sample(
                thing_id=form_data['thing'],
                context_factor_id=form_data['context_factor_3'],
                context_factor_value_id=form_data['context_factor_value_3'],
                value=form_data['value_3'],
                user_id=form_data['user']
            )
            sample_4 = Sample(
                thing_id=form_data['thing'],
                context_factor_id=form_data['context_factor_4'],
                context_factor_value_id=form_data['context_factor_value_4'],
                value=form_data['value_4'],
                user_id=form_data['user']
            )
            sample_5 = Sample(
                thing_id=form_data['thing'],
                context_factor_id=form_data['context_factor_5'],
                context_factor_value_id=form_data['context_factor_value_5'],
                value=form_data['value_5'],
                user_id=form_data['user']
            )
            sample_1.save()
            sample_2.save()
            sample_3.save()
            sample_4.save()
            sample_5.save()
            messages.success(request, 'Your ratings were submitted, thank you very much! Want to submit another one?')
            return redirect('add_sample')
        else:
            print(form.errors)
            # return redirect('add_sample')
    else:
        # create user if needed
        if 'iotrec_training_user' in request.COOKIES:
            try:
                user = TrainingUser.objects.get(identifier=request.COOKIES['iotrec_training_user'])
            except TrainingUser.DoesNotExist:
                user = TrainingUser.objects.create()
        else:
            user = TrainingUser.objects.create()

        # get random thing, context factor and context factor value
        random_thing = random.choice(ReferenceThing.objects.filter(active=True))




        random_context_factor_1 = random.choice(ContextFactor.objects.filter(active=True))
        random_context_factor_2 = random.choice(ContextFactor.objects.filter(active=True)
                                                .exclude(pk=random_context_factor_1.pk))
        random_context_factor_3 = random.choice(ContextFactor.objects.filter(active=True)
                                                .exclude(pk=random_context_factor_1.pk)
                                                .exclude(pk=random_context_factor_2.pk))
        random_context_factor_4 = random.choice(ContextFactor.objects.filter(active=True)
                                                .exclude(pk=random_context_factor_1.pk)
                                                .exclude(pk=random_context_factor_2.pk)
                                                .exclude(pk=random_context_factor_3.pk))
        random_context_factor_5 = random.choice(ContextFactor.objects.filter(active=True)
                                                .exclude(pk=random_context_factor_1.pk)
                                                .exclude(pk=random_context_factor_2.pk)
                                                .exclude(pk=random_context_factor_3.pk)
                                                .exclude(pk=random_context_factor_4.pk))

        random_context_factor_value_1 = random.choice(random_context_factor_1.values.filter(active=True))
        random_context_factor_value_2 = random.choice(random_context_factor_2.values.filter(active=True)
                                                      .exclude(pk=random_context_factor_value_1.pk))
        random_context_factor_value_3 = random.choice(random_context_factor_3.values.filter(active=True)
                                                      .exclude(pk=random_context_factor_value_1.pk)
                                                      .exclude(pk=random_context_factor_value_2.pk))
        random_context_factor_value_4 = random.choice(random_context_factor_4.values.filter(active=True)
                                                      .exclude(pk=random_context_factor_value_1.pk)
                                                      .exclude(pk=random_context_factor_value_2.pk)
                                                      .exclude(pk=random_context_factor_value_3.pk))
        random_context_factor_value_5 = random.choice(random_context_factor_5.values.filter(active=True)
                                                      .exclude(pk=random_context_factor_value_1.pk)
                                                      .exclude(pk=random_context_factor_value_2.pk)
                                                      .exclude(pk=random_context_factor_value_3.pk)
                                                      .exclude(pk=random_context_factor_value_4.pk))




        '''
        while True:
            try:
                random_context_factor_1 = random.choice(ContextFactor.objects.filter(active=True))
                random_context_factor_value_1 = random.choice(random_context_factor_1.values.filter(active=True))

                while not is_combination_qualified(user, random_thing, random_context_factor_1, random_context_factor_value_1):
                    random_context_factor_1 = random.choice(ContextFactor.objects.filter(active=True))
                    random_context_factor_value_1 = random.choice(random_context_factor_1.values.filter(active=True))
            except IndexError:
                continue
            break

        while True:
            try:
                random_context_factor_2 = random.choice(ContextFactor.objects.filter(active=True))
                random_context_factor_value_2 = random.choice(random_context_factor_2.values.filter(active=True)
                                                              .exclude(pk=random_context_factor_value_1.pk))

                while not is_combination_qualified(user, random_thing, random_context_factor_2, random_context_factor_value_2):
                    random_context_factor_2 = random.choice(ContextFactor.objects.filter(active=True))
                    random_context_factor_value_2 = random.choice(random_context_factor_2.values.filter(active=True)
                                                                  .exclude(pk=random_context_factor_value_1.pk))
            except IndexError:
                continue
            break

        while True:
            try:
                random_context_factor_3 = random.choice(ContextFactor.objects.filter(active=True))
                random_context_factor_value_3 = random.choice(random_context_factor_3.values.filter(active=True)
                                                              .exclude(pk=random_context_factor_value_1.pk)
                                                              .exclude(pk=random_context_factor_value_2.pk))

                while not is_combination_qualified(user, random_thing, random_context_factor_3, random_context_factor_value_3):
                    random_context_factor_3 = random.choice(ContextFactor.objects.filter(active=True))
                    random_context_factor_value_3 = random.choice(random_context_factor_3.values.filter(active=True)
                                                                  .exclude(pk=random_context_factor_value_1.pk)
                                                                  .exclude(pk=random_context_factor_value_2.pk))
            except IndexError:
                continue
            break

        while True:
            try:
                random_context_factor_4 = random.choice(ContextFactor.objects.filter(active=True))
                random_context_factor_value_4 = random.choice(random_context_factor_4.values.filter(active=True)
                                                              .exclude(pk=random_context_factor_value_1.pk)
                                                              .exclude(pk=random_context_factor_value_2.pk)
                                                              .exclude(pk=random_context_factor_value_3.pk))

                while not is_combination_qualified(user, random_thing, random_context_factor_4, random_context_factor_value_4):
                    random_context_factor_4 = random.choice(ContextFactor.objects.filter(active=True))
                    random_context_factor_value_4 = random.choice(random_context_factor_4.values.filter(active=True)
                                                                  .exclude(pk=random_context_factor_value_1.pk)
                                                                  .exclude(pk=random_context_factor_value_2.pk)
                                                                  .exclude(pk=random_context_factor_value_3.pk))
            except IndexError:
                continue
            break

        while True:
            try:
                random_context_factor_5 = random.choice(ContextFactor.objects.filter(active=True))
                random_context_factor_value_5 = random.choice(random_context_factor_5.values.filter(active=True)
                                                              .exclude(pk=random_context_factor_value_1.pk)
                                                              .exclude(pk=random_context_factor_value_2.pk)
                                                              .exclude(pk=random_context_factor_value_3.pk)
                                                              .exclude(pk=random_context_factor_value_4.pk))

                while not is_combination_qualified(user, random_thing, random_context_factor_5, random_context_factor_value_5):
                    random_context_factor_5 = random.choice(ContextFactor.objects.filter(active=True))
                    random_context_factor_value_5 = random.choice(random_context_factor_5.values.filter(active=True)
                                                                  .exclude(pk=random_context_factor_value_1.pk)
                                                                  .exclude(pk=random_context_factor_value_2.pk)
                                                                  .exclude(pk=random_context_factor_value_3.pk)
                                                                  .exclude(pk=random_context_factor_value_4.pk))
            except IndexError:
                continue
            break
        '''




        form = SampleForm(
            initial={
                "thing": random_thing.id,
                "context_factor_1": random_context_factor_1.id,
                "context_factor_2": random_context_factor_2.id,
                "context_factor_3": random_context_factor_3.id,
                "context_factor_4": random_context_factor_4.id,
                "context_factor_5": random_context_factor_5.id,
                "context_factor_value_1": random_context_factor_value_1.id,
                "context_factor_value_2": random_context_factor_value_2.id,
                "context_factor_value_3": random_context_factor_value_3.id,
                "context_factor_value_4": random_context_factor_value_4.id,
                "context_factor_value_5": random_context_factor_value_5.id,
                "user": user.identifier
            }
        )

        response = render(request, 'add.html',
                          {
                              'form': form,
                              'thing': model_to_dict(random_thing),
                              'context_factor_1': model_to_dict(random_context_factor_1),
                              'context_factor_2': model_to_dict(random_context_factor_2),
                              'context_factor_3': model_to_dict(random_context_factor_3),
                              'context_factor_4': model_to_dict(random_context_factor_4),
                              'context_factor_5': model_to_dict(random_context_factor_5),
                              'context_factor_value_1': model_to_dict(random_context_factor_value_1),
                              'context_factor_value_2': model_to_dict(random_context_factor_value_2),
                              'context_factor_value_3': model_to_dict(random_context_factor_value_3),
                              'context_factor_value_4': model_to_dict(random_context_factor_value_4),
                              'context_factor_value_5': model_to_dict(random_context_factor_value_5)
                          }
                          )

        response.set_cookie(key='iotrec_training_user', value=str(user.identifier),
                            expires=datetime.datetime(2020, 1, 1))
        return response


def get_statistics(request):

    unambiguous_counter_4 = 0
    unambiguous_counter_5 = 0
    significant_counter_5 = 0
    significant_counter_6 = 0
    total_counter = 0
    significant_samples_5 = []
    significant_samples_6 = []

    # go through all possible combinations and check for unambiguousness
    all_things = ReferenceThing.objects.filter(active=True)
    all_context_factors = ContextFactor.objects.filter(active=True)

    for thing in all_things:
        for context_factor in all_context_factors:
            cf_values = context_factor.values.filter(active=True)
            for cf_value in cf_values:
                rating_avg = Sample.objects.filter(thing=thing, context_factor=context_factor,
                                    context_factor_value=cf_value).aggregate(Avg('value'))['value__avg']
                if rating_avg is not None:
                    rating_avg = round(rating_avg, 2)
                total_counter += 1
                if is_combination_unambiguous(thing, context_factor, cf_value, 4):
                    unambiguous_counter_4 += 1
                if is_combination_unambiguous(thing, context_factor, cf_value, 5):
                    unambiguous_counter_5 += 1
                p_value_5 = is_combination_significant(thing, context_factor, cf_value, 5)
                p_value_6 = is_combination_significant(thing, context_factor, cf_value, 6)
                if 0 <= p_value_5 <= 0.1:
                    significant_counter_5 += 1
                    significant_samples_5.append({
                        'thing': thing.title,
                        'thingId': thing.id,
                        'contextFactor': context_factor.title,
                        'cfValue': cf_value.title,
                        'ratingAvg': rating_avg,
                        'pValue': round(p_value_5, 8)
                    })
                if 0 <= p_value_6 <= 0.1:
                    significant_counter_6 += 1
                    significant_samples_6.append({
                        'thing': thing.title,
                        'thingId': thing.id,
                        'contextFactor': context_factor.title,
                        'cfValue': cf_value.title,
                        'ratingAvg': rating_avg,
                        'pValue': round(p_value_6, 8)
                    })

    response = render(request, 'statistics.html',
                      {
                            'total_counter': total_counter,
                            'unambiguous_counter_4': unambiguous_counter_4,
                            'unambiguous_counter_5': unambiguous_counter_5,
                            'significant_counter_5': significant_counter_5,
                            'significant_samples_5': significant_samples_5,
                            'significant_counter_6': significant_counter_6,
                            'significant_samples_6': significant_samples_6
                      })

    return response
