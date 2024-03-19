from django.urls import path

from accounting.views import AccountingView

urlpatterns = [
    path('', AccountingView.as_view())
]
