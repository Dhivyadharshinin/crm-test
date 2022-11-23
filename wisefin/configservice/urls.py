from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from configservice.controller import entitycontroller, applicationcontroller, configcontroller

urlpatterns = [
    path('entity', entitycontroller.entity, name='entity'),
    path('application', applicationcontroller.application, name='application'),
    path('schema', configcontroller.schema, name='schema'),
    path('reserve', configcontroller.configure, name='configure'),
    path('test', configcontroller.test, name='test'),
    path('entity_search', entitycontroller.entity_search, name='search'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)