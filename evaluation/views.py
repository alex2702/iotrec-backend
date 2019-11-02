from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from evaluation.models import Experiment, Question, Reply, Questionnaire, Scenario
from evaluation.serializers import QuestionnaireSerializer, ReplySerializer, QuestionSerializer, \
    ExperimentSerializer, AnalyticsEventSerializer, ScenarioSerializer


class ExperimentViewSet(viewsets.ModelViewSet):
    serializer_class = ExperimentSerializer

    def get_queryset(self):
        queryset = Experiment.objects.filter(user=self.request.user)
        return queryset


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class ReplyViewSet(viewsets.ModelViewSet):
    queryset = Reply.objects.all()
    serializer_class = ReplySerializer


class QuestionnaireViewSet(viewsets.ModelViewSet):
    queryset = Questionnaire.objects.all()
    serializer_class = QuestionnaireSerializer


class AnalyticsEventViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = AnalyticsEventSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={
            **request.data,
            "user": request.user.id,
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ScenarioViewSet(viewsets.ModelViewSet):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer
