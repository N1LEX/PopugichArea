from rest_framework.routers import SimpleRouter

from analytics_service.app.views import CurrentDayStatsView, AllDaysStatsView

router = SimpleRouter()
router.register(r'', CurrentDayStatsView)
router.register(r'all-stats', AllDaysStatsView)

urlpatterns = router.urls
