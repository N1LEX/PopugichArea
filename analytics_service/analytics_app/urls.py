from rest_framework.routers import SimpleRouter

from analytics_app.views import StatsView

router = SimpleRouter()
router.register(r'', StatsView, basename='stats')
urlpatterns = router.urls
