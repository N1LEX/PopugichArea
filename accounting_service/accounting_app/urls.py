from accounting_app.views import AccountingView
from django.urls import path

urlpatterns = [
    path('', AccountingView.as_view())
]
