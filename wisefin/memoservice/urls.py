from django.conf import settings
from django.urls import path
from django.conf.urls.static import static

from memoservice.controller import memocontroller

urlpatterns = [
    path('memo', memocontroller.memo, name='memo'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
