import datetime
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
            #return redirect('add_sample')
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

        response.set_cookie(key='iotrec_training_user', value=str(user.identifier), expires=datetime.datetime(2020, 1, 1))
        return response


