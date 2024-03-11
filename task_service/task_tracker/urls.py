from rest_framework.routers import SimpleRouter

from task_tracker.views import TaskViewSet

router = SimpleRouter()
router.register(r'task', TaskViewSet, basename='task')

urlpatterns = router.urls
