from django.urls import path

from task_tracker.views import TasksView

urlpatterns = [
    path('tasks/', TasksView.as_view()),
]
