import numpy as np
from django.db.models import Avg
from django.db.models.functions import Coalesce

from training.models import ReferenceThing, ContextFactorValue, Sample, ContextBaseline, ThingBaseline


def calculate_baselines():
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

        for tuple in dataset:
            error += pow(tuple[2] - predicted[tuple[0]][tuple[1]], 2)

        return np.sqrt(error)

    def sgd(dataset):
        '''
        Perform stochastic gradient descent
        '''

        for i, c, r in dataset:
            prediction = get_rating(i, [c])
            e = r - prediction

            # update bias
            b_i_c[i][c] += gamma * (e - lambd * b_i_c[i][c])

    def get_rating(ref_thing, cf_values):
        sum_of_context_biases = 0
        for cfv in cf_values:
            sum_of_context_biases += b_i_c[ref_thing][cfv]
        predicted_rating = b_i[ref_thing] + sum_of_context_biases

        return predicted_rating

    def get_normalized_rating(ref_thing, cf_values):
        non_normalized_rating = get_rating(ref_thing, cf_values)

        minimum_rating = -1 * len(cf_values)
        maximum_rating = len(cf_values)
        normalized_rating = (non_normalized_rating - minimum_rating) / (maximum_rating - minimum_rating)

        return normalized_rating

    def full_matrix():
        '''
        Compute the full matrix
        '''

        # return two_dim_dict_to_matrix(b_i) + two_dim_dict_to_matrix(b_i_c)
        full_matrix = {}
        for rt in ref_things:
            full_matrix[rt.id] = {}
            for cfv in context_factor_values:
                full_matrix[rt.id][cfv.id] = b_i[rt.id] + b_i_c[rt.id][cfv.id]

        return full_matrix

    def normalize_matrix(matrix_in, nr_of_context_factors):
        matrix_out = {}
        min_rating = -1 * (nr_of_context_factors)
        max_rating = nr_of_context_factors
        for i in matrix_in:
            matrix_out[i] = {}
            for j in matrix_in[i]:
                matrix_out[i][j] = (matrix_in[i][j] - min_rating) / (max_rating - min_rating)

        return matrix_out


    # collect data
    ref_things = ReferenceThing.objects.filter(active=True)
    context_factor_values = ContextFactorValue.objects.filter(active=True)

    # populate rating dataset for learning
    R = {}
    for rt in ref_things:
        R[rt.id] = {}
        for cfv in context_factor_values:
            R[rt.id][cfv.id] = Sample\
                .objects\
                .filter(thing=rt, context_factor=cfv.context_factor, context_factor_value=cfv)\
                .aggregate(avg=Coalesce(Avg('value'), 0))['avg']

    gamma = 0.01  # learning rate
    lambd = 0.01  # regularization parameter
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

    # create a list of the training samples
    samples = [
        (i.id, c.id, R[i.id][c.id])
        for i in ref_things
        for c in context_factor_values
    ]

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
        training_process_string += "Iteration: %d - training error = %.4f - testing error = %.4f\n" % (
        it + 1, mse_training, mse_testing)

    for rt in ref_things:
        # thing baselines
        baseline, created = ThingBaseline.objects.get_or_create(
            reference_thing=rt
        )

        # update value and save the object
        baseline.value = b_i[rt.id]
        baseline.save()

        # context baselines
        for cfv in context_factor_values:
            baseline, created = ContextBaseline.objects.get_or_create(
                reference_thing=rt,
                context_factor=cfv.context_factor,
                context_factor_value=cfv
            )

            # update value and save the object
            baseline.value = b_i_c[rt.id][cfv.id]
            baseline.save()

    matrix = full_matrix()
    matrix_norm = normalize_matrix(matrix, 1)

    return R, b_i_c, matrix, matrix_norm, training_process, training_process_string