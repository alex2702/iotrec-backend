from django.contrib import admin

from evaluation.models import Experiment, Questionnaire, Reply, Question, AnalyticsEvent, Scenario


class ExperimentAdmin(admin.ModelAdmin):
    fields = ['id', 'user', 'scenario', 'order', 'context_active', 'preferences_active', 'start', 'end', 'created_at', 'updated_at']
    list_display = ['id', 'user', 'scenario', 'order', 'context_active', 'preferences_active', 'start', 'end']

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'order', 'context_active', 'preferences_active', 'created_at', 'updated_at']


admin.site.register(Experiment, ExperimentAdmin)


class QuestionAdmin(admin.ModelAdmin):
    fields = ['id', 'short_name', 'text', 'created_at', 'updated_at']
    list_display = ['id', 'short_name', 'text', 'created_at', 'updated_at']

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']


admin.site.register(Question, QuestionAdmin)


class ReplyAdmin(admin.ModelAdmin):
    fields = ['id', 'user', 'experiment', 'question', 'value', 'created_at', 'updated_at']
    list_display = ['created_at', 'user', 'experiment', 'question', 'value']
    list_filter = ['user', 'experiment', 'question', 'created_at']

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']


admin.site.register(Reply, ReplyAdmin)


class QuestionnaireAdmin(admin.ModelAdmin):
    fields = ['id', 'user', 'age', 'gender', 'qualification', 'smartphone_usage', 'created_at', 'updated_at']
    list_display = ['id', 'created_at', 'user', 'gender', 'qualification', 'smartphone_usage', 'updated_at']
    list_filter = ['user', 'created_at']

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']


admin.site.register(Questionnaire, QuestionnaireAdmin)


class AnalyticsEventAdmin(admin.ModelAdmin):
    fields = ['id', 'type', 'user', 'thing', 'recommendation', 'value', 'created_at', 'updated_at']
    list_display = ('id', 'created_at', 'type', 'user', 'thing', 'recommendation', 'value')
    list_filter = ['user', 'created_at']

    def get_readonly_fields(self, request, obj=None):
        return ['id', 'created_at', 'updated_at']


admin.site.register(AnalyticsEvent, AnalyticsEventAdmin)


class ScenarioAdmin(admin.ModelAdmin):
    fields = ['text_id', 'title', 'created_at', 'updated_at']
    list_display = ('text_id', 'title')

    def get_readonly_fields(self, request, obj=None):
        return ['created_at', 'updated_at']


admin.site.register(Scenario, ScenarioAdmin)