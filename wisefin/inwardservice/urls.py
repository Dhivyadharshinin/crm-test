from django.conf import settings
from django.urls import path

from django.conf.urls.static import static
from inwardservice.controller import inwardcontroller
# from inwardservice.controller import inwardcontroller, inwardproductsubcategorycontroller,inwardproductcatcontroller
# from inwardservice.controller import escalationtypecontroller
# from inwardservice.controller import escalationsubtypecontroller

urlpatterns = [
    path('inward', inwardcontroller. create_inward, name='inward_creation'),
    path('inward/<inward_id>', inwardcontroller.fetch_inward, name='fetch_inward'),
    path('inward/<inward_id>/details', inwardcontroller.fetch_inward_detail_list, name='inward_details_list'),
    # path('inward/<inward_id>/details/<details_id>/clone/<count>', inwardcontroller.clone_detail, name='clone_inward'),
    # path('inward/<inward_id>/details/<details_id>/file/<file_id>', inwardcontroller.fetch_file, name='fetch_file'),
    # path('search', inwardcontroller.search_inward, name='inward_search'),
    # path('pdtcat', inwardproductcatcontroller.create_productcat, name='createproductcat'),
    # path('pdtcat/<productcat_id>', inwardproductcatcontroller.fetch_productcat, name='fetch_productcat'),
    # path('escalationtype',escalationtypecontroller. create_escaltiontype, name='escaltiontype_creation'),
    # path('escalationtype/<escalationtype_id>',escalationtypecontroller. fetch_escalation, name='fetch_escaltiontype'),
    # path('escalationsubtype', escalationsubtypecontroller.create_escaltionsubtype, name='escaltiontype_creation'),
    # path('escalationsubtype/<escalationsubtype_id>', escalationsubtypecontroller.fetch_escalationsub,name='fetch_escaltiontype'),
    # path('productcat/<product_id>',inwardproductsubcategorycontroller.fetch_procat_list, name='productcat'),
    # path('prosubcat',inwardproductsubcategorycontroller.create_prosubcat, name='prosubcat'),
    # path('prosubcat/<prosubcat_id>',inwardproductsubcategorycontroller.fetch_prosubcat, name='prosubcat'),
    # path('prosubcat/<prosubcat_id>', inwardproductsubcategorycontroller.delete_prosubcat, name='prosubcat'),
    # path('search_prosubcat', inwardproductsubcategorycontroller.search_prosubcat, name='search_prosubcat'),
    # path('search_escalation', escalationtypecontroller.search_escalation, name='search_escalation'),
    # path('search_escalationsub', escalationsubtypecontroller.search_escalationsub, name='search_escalationsub'),
    # path('search_productcat', inwardproductcatcontroller.search_productcat, name='search_productcat'),
    # path('inwardbranchassign/<branch_id>/<user_id>', inwardcontroller.emp_branchassign, name='emp_branchassign'),

    path('get_apinward', inwardcontroller.fetch_ap_inward, name='fetch_ap_inward'),
    path('get_apinward_status', inwardcontroller.get_inward_status, name='get_inward_status'),
    path('inwardstatus_update', inwardcontroller.inwardstatus_update, name='inwardstatus_update'),

    path('inward_summarysearch', inwardcontroller.inward_summarysearch, name='inward_summarysearch'),
    path('fileview/<file_id>', inwardcontroller.view_file, name='view_file'),
    path('inwardetails_summarysearch', inwardcontroller.inward_details_summarysearch, name='inwardetails_summarysearch'),
    path('inward_docstatus', inwardcontroller.fetch_inward_docstatus, name = 'inward_docstatus'),
    path('inward_status', inwardcontroller.fetch_inwardstatus, name = 'inward_status'),
    path('inward_action', inwardcontroller.fetch_inwardaction, name = 'inward_action'),
    path('inward_docaction', inwardcontroller.fetch_inward_docaction, name='inward_action'),
    # # path('documentassignupdate', inwardcontroller.documentassignupdate, name='documentassignupdate'),
    # # path('documentresponseupdate', inwardcontroller.documentresponseupdate, name='documentresponseupdate'),
    # # path('documentsummarysearch', inwardcontroller.documentsummarysearch, name='documentsummarysearch'),
    path('inwarddetails/<inward_id>', inwardcontroller.fetch_inwarddetails, name='fetch_inwarddetails'),
    path('inwarddetails', inwardcontroller.inwarddetails, name='inwarddetails'),
    path('inward/<inward_id>/details/<details_id>/clone', inwardcontroller.clone_detail, name='clone_inward'),
    path('inward/<inward_id>/packet_no/<packet_no>/count/<count>', inwardcontroller.clone_packet_count, name='clone_packet_count'),
    path('inwarddetailupdate', inwardcontroller.inwarddetailupdate, name='inwarddetailupdate'),
    # path('inwardtran/<inward_id>', inwardcontroller.inwardtran, name='inwardtran'),
    # # path('doc_responsesummarysearch', inwardcontroller.doc_responsesummarysearch, name='doc_responsesummarysearch'),
    path('inward_delete/<inward_id>/<detail_id>/<packet_no>', inwardcontroller.inward_delete, name='inward_delete'),
    path('inward_file_download/<file_id>', inwardcontroller.inward_file_download, name='download_file'),
    path('inwarddetails_file/<file_id>', inwardcontroller.inwarddetails_file, name='inwarddetails_file'),

]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)