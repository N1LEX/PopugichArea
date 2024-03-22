from rest_framework.routers import SimpleRouter

from task_app.views import TaskTrackerView

router = SimpleRouter()
router.register(r'', TaskTrackerView, basename='task-tracker')

urlpatterns = router.urls
