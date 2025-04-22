from django.urls import include, path
from app import views
from app.crons.cronjobs import register_cronjobs

urlpatterns = [
]

# Init work
register_cronjobs()
