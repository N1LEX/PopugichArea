from rest_framework.routers import SimpleRouter

from task_tracker.views import TaskTrackerView

router = SimpleRouter()
router.register(r'task-tracker', TaskTrackerView, basename='task-tracker')

urlpatterns = router.urls
