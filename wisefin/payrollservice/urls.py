from django.conf import settings
from django.urls import path
from django.conf.urls.static import static
from payrollservice.controller import salarycomponentcontroller,salarylabelcontroller,salarystructuremapingcontroller,detectionInfocontroller

urlpatterns = [
    path('salarycomponent', salarycomponentcontroller.salarycomponent, name='salarycomponent'),
    path('salarycomponent/<salary_id>', salarycomponentcontroller.fetch_salarycomponent, name='fetch_salarycomponent'),
    path('salarylabel', salarylabelcontroller.salarylabel, name='salarylabel'),
    path('salarylabel/<salary_id>', salarylabelcontroller.fetch_salarylabel, name='fetch_salarylabel'),
    path('structuremapping', salarystructuremapingcontroller.structuremapping, name='structuremapping'),
    path('structuremapping/<salary_id>', salarystructuremapingcontroller.fetch_structuremapping, name='fetch_structuremapping'),
    path('detection_info', detectionInfocontroller.detection_info, name='detection_info'),
    path('detection_info/<salary_id>', detectionInfocontroller.fetch_detectioninfo, name='fetch_detectioninfo'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)