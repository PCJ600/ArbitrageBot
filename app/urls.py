from django.urls import include, path
from app import views
from app.crons.cronjobs import register_cronjobs
from app.query.query_funds import query_funds

urlpatterns = [
]

# Init work
register_cronjobs()
