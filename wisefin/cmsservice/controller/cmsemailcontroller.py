import json
from django.http import HttpResponse
from rest_framework.decorators import api_view
from cmsservice.service.cms_email_service import EmailService

@api_view(['GET'])
def mailScheduler(request):
    if request.method == 'GET':
        mail_service = EmailService(request.scope)
        resp_obj = mail_service.cmsemail()
        response = HttpResponse(resp_obj, content_type="application/json")
        return response