from rest_framework.routers import SimpleRouter

from app.views import CurrentDayStatsView, AllStatsView

router = SimpleRouter()
router.register(r'', CurrentDayStatsView, basename='day-stats')
router.register(r'all-stats', AllStatsView, basename='all-stats')

urlpatterns = router.urls
