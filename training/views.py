import random

from django.contrib import messages
from django.forms import model_to_dict
from django.shortcuts import render, redirect

from training.forms import SampleForm
from training.models import TrainingUser, ReferenceThing, ContextFactor, Sample


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
            #sample_2 =
            #sample_3 =
            #sample_4 =
            #sample_5 =
            sample_1.save()
            #
            #
            #
            #
            messages.success(request, 'Form submission successful. Want to submit another one?')
            return redirect('add_sample')
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
        random_thing = random.choice(ReferenceThing.objects.all())
        random_context_factor_1 = random.choice(ContextFactor.objects.all())
        random_context_factor_2 = random.choice(ContextFactor.objects.all())
        random_context_factor_3 = random.choice(ContextFactor.objects.all())
        random_context_factor_4 = random.choice(ContextFactor.objects.all())
        random_context_factor_5 = random.choice(ContextFactor.objects.all())
        random_context_factor_value_1 = random.choice(random_context_factor_1.values.all())
        random_context_factor_value_2 = random.choice(random_context_factor_2.values.all())
        random_context_factor_value_3 = random.choice(random_context_factor_3.values.all())
        random_context_factor_value_4 = random.choice(random_context_factor_4.values.all())
        random_context_factor_value_5 = random.choice(random_context_factor_5.values.all())

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
        response.set_cookie(key='iotrec_training_user', value=str(user.identifier))
        return response


