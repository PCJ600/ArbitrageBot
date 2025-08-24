from django.urls import include, path
from app.views import TestView

urlpatterns = [
    path('test/', TestView.as_view(), name='test'),
]
