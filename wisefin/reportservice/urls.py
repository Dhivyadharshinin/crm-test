from django.conf import settings
from django.urls import path

from django.conf.urls.static import static
from reportservice.controller import reportcontroller, reportdownloadcontroller,vendorstatementreporcontroller

urlpatterns = [
    path('module', reportcontroller.fetch_moduledropdown, name='moduledropdown'),
    path('modulename/<module_id>', reportcontroller.fetch_modulenamedropdown, name='modulename'),
    path('fetch_displayname', reportcontroller.fetch_displayname, name='entrydetails'),
    path('parametersave', reportcontroller.fetch_moduleparameter, name='parametersave'),
    path('parameterlist', reportdownloadcontroller.fetch_parameterlist, name='parameterlist'),
    path('reportdownload', reportdownloadcontroller.fetch_reportdownload, name='reportdownload'),
    path('downloadlist', reportdownloadcontroller.fetch_downloadlist, name='reportdownload'),
    path('downloadreport/<id>', reportdownloadcontroller.downloadreport, name='downloadreport'),
    path('fetch_vendor/<vendor_id>', reportdownloadcontroller.fetch_vendor, name='fetch_vendor'),
    path('fetch_supplierdetails', vendorstatementreporcontroller.fetch_vendorstatement, name='fetch_supplierdetails'),
    path('download_vendorstatement', vendorstatementreporcontroller.download_vendorstatement, name='download_vendorstatement'),
    path('vendorstatement_eod', vendorstatementreporcontroller.vendorstatement_eod, name='vendorstatement_eod'),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)