from django.conf import settings
from django.urls import path

from django.conf.urls.static import static
from entryservice.controller import entrycontroller, entryparametertemplatecontroller, entryoracleapicontroller, \
    faentrytemplatecontroller

urlpatterns = [
    path('entrydetails', entrycontroller.entrydetails, name='entrydetails'),
    path('entrydetails/<entry_id>', entrycontroller.fetch_entrydetails, name='entrydetails'),
    path('fetch_commonentrydetails/<entry_crno>', entrycontroller.fetch_commonentrydetails, name='entrydetails'),
    path('displayname', entryparametertemplatecontroller.createparametername, name='displayname'),
    path('displayallname', entryparametertemplatecontroller.fetch_displaynamedr, name='displayname'),
    path('displayallnamecr', entryparametertemplatecontroller.fetch_displaynamecr, name='displayname'),
    path('conditionsname', entryparametertemplatecontroller.get_conditions, name='displayname'),
    path('commonquerydata', entryparametertemplatecontroller.fetch_querycondition, name='commonquerydata'),
    path('paramnamelist', entryparametertemplatecontroller.fetch_paramname_list, name='paramnamelist'),
    path('updateparametername', entryparametertemplatecontroller.inactive_parametername, name='updateparametername'),
    path('getentrytype', entryparametertemplatecontroller.get_entrytype, name='getentrytype'),
    path('entrytemplateupdate', entryparametertemplatecontroller.entrytemplateupdate, name='entrytemplateupdate'),
    path('entry_oracle_comman_api',entryoracleapicontroller.entry_oracle_comman_api, name='entry_oracle_comman_api'),
    path('entry_filed_transaction',entrycontroller.entry_filed_transaction, name='entry_filed_transaction'),
    path('inactiveentry',entrycontroller.inactive_entry, name='inactive_entry'),
    path('entry_succss_data', entrycontroller.entry_succss_data,name='entry_succss_data'),
    path('facommonquerydata',faentrytemplatecontroller.fetch_FAquerycondition, name='fatemplate_get')

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)