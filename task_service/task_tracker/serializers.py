from rest_framework import serializers

from task_tracker.models import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ['id']
        read_only_fields = ['user']
