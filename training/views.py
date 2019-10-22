import datetime
import random

import scipy.stats
import numpy as np
from django.contrib import messages
from django.db.models import Avg
from django.db.models.functions import Coalesce
from django.forms import model_to_dict
from django.shortcuts import render, redirect

from training.forms import SampleForm
from training.models import TrainingUser, ReferenceThing, ContextFactor, Sample, ContextFactorValue


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

    '''
    if is_combination_unambiguous(thing, context_factor, context_factor_value, 4):
        return False

    if 0 <= is_combination_significant(thing, context_factor, context_factor_value, 6) <= 0.1:
        return False
    '''

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



        '''
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
    samples_counter = Sample.objects.count()

    unambiguous_counter_4 = 0
    unambiguous_counter_5 = 0
    unambiguous_counter_6 = 0
    significant_counter_4 = 0
    significant_counter_5 = 0
    significant_counter_6 = 0
    total_counter = 0
    significant_samples_4 = []
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
                if is_combination_unambiguous(thing, context_factor, cf_value, 6):
                    unambiguous_counter_6 += 1
                p_value_4 = is_combination_significant(thing, context_factor, cf_value, 4)
                p_value_5 = is_combination_significant(thing, context_factor, cf_value, 5)
                p_value_6 = is_combination_significant(thing, context_factor, cf_value, 6)
                if 0 <= p_value_4 <= 0.1:
                    significant_counter_4 += 1
                    significant_samples_4.append({
                        'thing': thing.title,
                        'thingId': thing.id,
                        'contextFactor': context_factor.title,
                        'cfValue': cf_value.title,
                        'ratingAvg': rating_avg,
                        'pValue': round(p_value_4, 8)
                    })
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
                            'samples_counter': samples_counter,
                            'unambiguous_counter_4': unambiguous_counter_4,
                            'unambiguous_counter_5': unambiguous_counter_5,
                            'unambiguous_counter_6': unambiguous_counter_6,
                            'significant_counter_4': significant_counter_4,
                            'significant_samples_4': significant_samples_4,
                            'significant_counter_5': significant_counter_5,
                            'significant_samples_5': significant_samples_5,
                            'significant_counter_6': significant_counter_6,
                            'significant_samples_6': significant_samples_6
                      })

    return response

def get_results(request):
    '''
    Perform matrix factorization to predict empty entries in a matrix.

    Arguments
        - R (ndarray)    : item-context rating matrix
        - d (int)        : number of latent dimensions
        - gamma (float)  : learning rate
        - lambda (float) : regularization parameter
    '''

    def calc_mse(dataset):
        '''
        Compute the total mean square error
        '''

        predicted = full_matrix()
        error = 0

        #for rtId in predicted:
        #    for cfvId in predicted[rtId]:
        #        error += pow(R[rtId][cfvId] - predicted[rtId][cfvId], 2)

        for tuple in dataset:
            error += pow(tuple[2] - predicted[tuple[0]][tuple[1]], 2)

        return np.sqrt(error)

    def calc_mse_old():
        '''
        Compute the total mean square error
        '''

        predicted = full_matrix()
        error = 0

        for rtId in predicted:
            for cfvId in predicted[rtId]:
                error += pow(R[rtId][cfvId] - predicted[rtId][cfvId], 2)

        return np.sqrt(error)

    def sgd(dataset):
        '''
        Perform stochastic gradient descent
        '''

        #print(dataset)

        for i, c, r in dataset:
            #print("i: " + str(i))
            #print("c: " + str(c))
            #print("r: " + str(r))
            prediction = get_rating(i, [c])
            e = r - prediction

            # update bias
            b_i_c[i][c] += gamma * (e - lambd * b_i_c[i][c])

    def get_rating(ref_thing, context_factor_values):
        '''
        Get the predicted rating of a given user in a given context
        '''

        print("number of context factor values: " + str(len(context_factor_values)))

        sum_of_context_biases = 0
        for cfv in context_factor_values:
            sum_of_context_biases += b_i_c[ref_thing][cfv]
        predicted_rating = b_i[ref_thing] + sum_of_context_biases

        print("predicted rating (not normalized): " + str(predicted_rating))

        # normalize
        #minimum_rating = -1 * (1 + len(context_factor_values))
        #maximum_rating = 1 + len(context_factor_values)
        #predicted_rating = (predicted_rating - minimum_rating)/(maximum_rating - minimum_rating)

        print("predicted rating (normalized): " + str(predicted_rating))

        return predicted_rating

    def full_matrix():
        '''
        Compute the full matrix using the resultant bias B
        '''

        #return two_dim_dict_to_matrix(b_i) + two_dim_dict_to_matrix(b_i_c)
        full_matrix = {}
        for rt in ref_things:
            full_matrix[rt.id] = {}
            for cfv in context_factor_values:
                full_matrix[rt.id][cfv.id] = b_i[rt.id] + b_i_c[rt.id][cfv.id]
                # normalize (number of context factor values is fixed to 1 here, the function is only used for training where it's always 1, not for making predictions)
                #full_matrix[rt.id][cfv.id] = (full_matrix[rt.id][cfv.id] + 2) / 4

        return full_matrix

    def normalize_matrix(matrix_in, nr_of_context_factors):
        matrix_out = {}
        min_rating = -1 * (nr_of_context_factors)
        max_rating = nr_of_context_factors
        for i in matrix_in:
            matrix_out[i] = {}
            for j in matrix_in[i]:
                matrix_out[i][j] = (matrix_in[i][j] - min_rating)/(max_rating - min_rating)

        return matrix_out

    def two_dim_dict_to_matrix(dict):
        result_matrix = np.zeros(len(dict), len(list(dict)[0]))
        for i in dict:
            dict_in_i = list(dict)[i]
            for j in dict_in_i:
                result_matrix[i][j] = j

        print(dict)
        print(result_matrix)

        return result_matrix


    # collect data
    ref_things = ReferenceThing.objects.filter(active=True)
    context_factor_values = ContextFactorValue.objects.filter(active=True)

    # populate rating dataset for learning
    R = {}
    for rt in ref_things:
        R[rt.id] = {}
        for cfv in context_factor_values:
            R[rt.id][cfv.id] = Sample.objects.filter(thing=rt, context_factor=cfv.context_factor,
                                                     context_factor_value=cfv).aggregate(avg=Coalesce(Avg('value'), 0))['avg']

    num_ref_things = len(ref_things)
    num_context_factor_values = len(context_factor_values)
    gamma = 0.01 # learning rate
    lambd = 0.01 # regularization parameter
    iterations = 1000

    # initialize biases
    b_i_c = {}
    b_i = {}
    for rt in ref_things:
        # initialize item-context biases with 0
        b_i_c[rt.id] = {}
        for cfv in context_factor_values:
            b_i_c[rt.id][cfv.id] = 0
        # item bias is the average of all ratings for the item
        b_i[rt.id] = Sample.objects.filter(thing=rt).aggregate(avg=Coalesce(Avg('value'), 0))['avg']

    #print("b_i_c")
    #print(b_i_c)

    #print("b_i")
    #print(b_i)

    # create a list of the training samples
    samples = [
        (i.id, c.id, R[i.id][c.id])
        for i in ref_things
        for c in context_factor_values
    ]
    training_set = []
    testing_set = []

    #print(samples)

    # perform stochastic gradient descent
    training_process = []
    training_process_string = ""
    for it in range(iterations):
        np.random.shuffle(samples)
        size_of_training_set = round(len(samples) * 0.8)
        training_set = samples[:size_of_training_set]
        testing_set = samples[size_of_training_set:]

        sgd(training_set)
        mse_training = calc_mse(training_set)
        mse_testing = calc_mse(testing_set)
        training_process.append((it + 1, "{:.4f}".format(mse_training), "{:.4f}".format(mse_testing)))
        training_process_string += "Iteration: %d - training error = %.4f - testing error = %.4f\n" % (it+1, mse_training, mse_testing)
        #print("Iteration: %d - error = %.4f" % (it+1, mse))

    print(training_process_string)

    print("\n\nBASELINES")
    baselines_string = ""
    baselines_table_header = []
    baselines_table_body = {}

    headers_c = "cf_value    "
    for c in b_i_c[list(b_i_c)[0]]:
        headers_c += "{:9d}".format(c)
        cf_name = str(context_factor_values.get(id=c).title)
        baselines_table_header.append(str(c) + "\n" + ((cf_name[:8] + '...') if len(cf_name) > 11 else cf_name))
    #print(headers_c)
    baselines_string += headers_c + "\n"

    for i in b_i_c:
        i_string = ""
        baselines_table_body[i] = {}
        for c in b_i_c[i]:
            i_string += "{:7.3f}".format(b_i_c[i][c]) + ", "
            baselines_table_body[i][c] = ("{:.2f}".format(b_i_c[i][c]))
        #print("b_i_c[" + str(i) + "][] = " + i_string)
        baselines_string += "b_i_c[" + str(i) + "][] = " + i_string + "\n"

    print(baselines_string)

    print("\n\nRATINGS DATASET")
    ratings_string = ""
    ratings_table_header = []
    ratings_table_body = {}

    headers_c = "cf_value"
    for c in R[list(R)[0]]:
        headers_c += "{:9d}".format(c)
        cf_name = str(context_factor_values.get(id=c).title)
        ratings_table_header.append(str(c) + "\n" + ((cf_name[:8] + '...') if len(cf_name) > 11 else cf_name))
    #print(headers_c)
    ratings_string += headers_c + "\n"

    for i in R:
        i_string = ""
        ratings_table_body[i] = {}
        for c in R[i]:
            i_string += "{:7.3f}".format(R[i][c]) + ", "
            ratings_table_body[i][c] = ("{:.2f}".format(R[i][c]))
        #print("R[" + str(i) + "][] = " + i_string)
        ratings_string += "R[" + str(i) + "][] = " + i_string + "\n"

    print(ratings_string)

    print("\n\nRATING PREDICTIONS")
    predictions_string = ""
    predictions_table_header = []
    predictions_table_body = {}

    matrix = full_matrix()

    headers_c = "cf_value        "
    for c in matrix[list(matrix)[0]]:
        headers_c += "{:9d}".format(c)
        cf_name = str(context_factor_values.get(id=c).title)
        predictions_table_header.append(str(c) + "\n" + ((cf_name[:8] + '...') if len(cf_name) > 11 else cf_name))
    #print(headers_c)
    predictions_string += headers_c + "\n"

    for i in matrix:
        i_string = ""
        predictions_table_body[i] = {}
        for c in matrix[i]:
            i_string += "{:7.3f}".format(matrix[i][c]) + ", "
            predictions_table_body[i][c] = ("{:.2f}".format(matrix[i][c]))
        #print("predicted[" + str(i) + "][] = " + i_string)
        predictions_string += "predicted[" + str(i) + "][] = " + i_string + "\n"

    print(predictions_string)

    # PREDICTIONS NORMALIZED

    predictions_norm_table_header = []
    predictions_norm_table_body = {}

    matrix_normalized = normalize_matrix(matrix, 1)

    for c in matrix_normalized[list(matrix_normalized)[0]]:
        cf_name = str(context_factor_values.get(id=c).title)
        predictions_norm_table_header.append(str(c) + "\n" + ((cf_name[:8] + '...') if len(cf_name) > 11 else cf_name))

    for i in matrix_normalized:
        predictions_norm_table_body[i] = {}
        for c in matrix_normalized[i]:
            predictions_norm_table_body[i][c] = ("{:.2f}".format(matrix_normalized[i][c]))

    #print("\n\nTEST PREDICTIONS")
    #print("get_rating[33, [1, 8, 17, 39]] = " + str(get_rating(33, [1, 8])))
    #print("get_rating[33, 21] = " + str(get_rating(33, [21])))
    #print("get_rating[58, 9] = " + str(get_rating(58, [9])))
    #print("get_rating[58, 16] = " + str(get_rating(58, [16])))

    response = render(request, 'results.html',
                      {
                          'baselines': baselines_string,
                          'ratings': ratings_string,
                          'predictions': predictions_string,
                          'ratings_table_header': ratings_table_header,
                          'ratings_table_body': ratings_table_body,
                          'predictions_table_header': predictions_table_header,
                          'predictions_table_body': predictions_table_body,
                          'baselines_table_header': baselines_table_header,
                          'baselines_table_body': baselines_table_body,
                          'training_process': training_process,
                          'predictions_norm_table_header': predictions_norm_table_header,
                          'predictions_norm_table_body': predictions_norm_table_body
                      })

    return response