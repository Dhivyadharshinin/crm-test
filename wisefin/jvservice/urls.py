from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from jvservice.controller import jvcontroller
#test
urlpatterns = [
    path('get_journaltype', jvcontroller.get_journaltype, name='journaltype'),
    path('get_journaldetailstype', jvcontroller.get_journaldetailtype, name='journaltype'),
    path('create_jventry', jvcontroller.create_jventry, name='create'),
    path('jvaprvlsummary', jvcontroller.fetch_journalaprvl_list, name='approval summary'),
    path('jventry/<jv_id>', jvcontroller.fetch_jventry, name='create'),
    path('jventrysearch', jvcontroller.search_jv, name='jventry search'),
    path('jvrefnosearch', jvcontroller.search_jvrefno, name='jvrefno search'),
    path('jvdelete/<jv_id>', jvcontroller.delete_jventry, name='jventry delete'),
    path('jvdetaildelete/<jv_id>', jvcontroller.delete_jvdentry, name='jvdetailentry delete'),
    path('jventryreject', jvcontroller.jvreject, name='jventryreject'),
    path('jventryapproved', jvcontroller.jvapproved, name='jventryapprove'),
    path('search_jvupload', jvcontroller.search_jvupload, name='jventryupload'),
    path('get_journalstatus', jvcontroller.get_journalstatus, name='journaltype'),
    path('get_trans/<No>',jvcontroller.get_jvtransget,name='jvtransaction'),
    path('jvfile/<file_id>', jvcontroller.fetch_file, name='download'),
    path('deletefile/<file_id>', jvcontroller.delete_file, name='deletefile'),
    path('fileview/<file_id>', jvcontroller.view_file, name='view_file'),
    path('xltemp', jvcontroller.view_exceltemplate, name='xltemplate'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)