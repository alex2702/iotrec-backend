from iotrec_api.utils.thing import get_utility


def get_recommendation_score(thing, user, context):
    return get_utility(thing, user, context)
