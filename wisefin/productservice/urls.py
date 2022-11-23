from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from productservice.controller import sourcecontroller


urlpatterns = [
                  path('source',sourcecontroller.source,name='source_create'),
                  # path('summary_source', sourcecontroller. summary_source, name='summary_source'),
                  # path('source_get/<id>', sourcecontroller.get_source, name='summary_source'),

              ]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)