"""nwisefin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('configserv/', include('configservice.urls')),
    path('usrserv/', include('userservice.urls')),
    path('mstserv/', include('masterservice.urls')),
    path('memoserv/', include('memoservice.urls')),
    path('venserv/', include('vendorservice.urls')),
    path('taserv/', include('taservice.urls')),
    path('docserv/', include('docservice.urls')),
    path('inwdserv/', include('inwardservice.urls')),
    path('apserv/', include('apservice.urls')),
    path('ecfserv/', include('ecfservice.urls')),
    path('entryserv/', include('entryservice.urls')),
    path('reportserv/', include('reportservice.urls')),
    path('faserv/', include('faservice.urls')),
    path('pprservice/',include('pprservice.urls')),
    path('jvserv/', include('jvservice.urls')),
    path('cmsserv/', include('cmsservice.urls')),
    path('atdserv/', include('attendanceservice.urls')),
    path('hrmsserv/', include('hrmsservice.urls')),
    path('payrollserv/', include('payrollservice.urls')),
    path('prodserv/', include('productservice.urls')),
]
