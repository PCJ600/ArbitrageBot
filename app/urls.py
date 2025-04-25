from django.urls import include, path
from app.views import TestView
from app.crons.cronjobs import register_cronjobs


urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
]

register_cronjobs()
