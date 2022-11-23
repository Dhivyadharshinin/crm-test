from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from docservice.controller import doccontroller

urlpatterns = [
    path('document', doccontroller.upload_documents, name='upload_documents'),
    path('document_single', doccontroller.upload_single_document, name='upload_documents'),
    path('document/<file_id>', doccontroller.fetch_documents, name='fetch_documents'),
    path('document/download/<file_id>', doccontroller.download_attachment, name='download_documents'),
    path('documentinfo', doccontroller.get_info, name='fetch_documentsinfo'),
    path('doc_moduletype', doccontroller.doc_moduletype, name='doc_moduletype'),
    path('doc_module', doccontroller.doc_module, name='doc_module'),
    path('doc_module_ta', doccontroller.doc_module_ta, name='doc_module_ta'),
    path('doc_upload_ta', doccontroller.doc_upload_ta, name='doc_upload'),
    path('doc_upload', doccontroller.doc_upload, name='doc_upload'),
    path('docdownload/<file_id>', doccontroller.doc_download, name='download_documents'),

    # vow
    path('doc_download/<file_id>', doccontroller.doc_download, name='download_documents'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)