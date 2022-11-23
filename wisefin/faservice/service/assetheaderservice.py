import json
import traceback
from dateutil import parser
from django.db import IntegrityError
from django.db.models import Q
from datetime import datetime
from django.utils.dateformat import DateFormat, TimeFormat
from django.db.models import Count
from django.db import connection
from faservice.models.famodels import AssetHeader
from faservice.util.fautil import AssetQuery
from faservice.util.fautil_valid import date_validation
from django.http import HttpResponse
from utilityservice.data.response.nwisefinerror import NWisefinError as Error
from utilityservice.data.response.nwisefinerrorconstants import ErrorDescription,ErrorMessage
from utilityservice.data.response.nwisefinlist import NWisefinList
from django.utils import timezone
from nwisefin.settings import logger
from django.utils.timezone import now
from utilityservice.data.response.nwisefinsuccess import NWisefinSuccess,SuccessMessage,SuccessStatus
from utilityservice.data.response.nwisefinpaginator import NWisefinPaginator
from faservice.util.FaApiService import FaApiService
from faservice.data.response.depreciationresponse import DepreciationResponse
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread


class AssetheaderService(NWisefinThread):
    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.FA_SERVICE)
    def create_assetheader(self,headerobj):
        Header = AssetHeader.objects.create(barcode=headerobj.get_barcode(),
                                                        date=headerobj.get_date(),
                                                        assetheadermonth=headerobj.get_assetheadermonth(),
                                                        assetheaderyear=headerobj.get_assetheaderyear(),
                                                        astvalbeforedeptot=headerobj.get_astvalbeforedeptot(),
                                                        computeddeptot=headerobj.get_computeddeptot(),
                                                        reviseddeptot=headerobj.get_reviseddeptot(),
                                                        revisedcbtot=headerobj.get_revisedcbtot(),
                                                        deprestot=headerobj.get_deprestot(),
                                                        costtot=headerobj.get_costtot(),
                                                        valuetot=headerobj.get_valuetot(),
                                                        type=headerobj.get_type(),
                                                        issale=headerobj.get_issale(),
                                                        created_by=1)

        success_obj = NWisefinSuccess()
        success_obj.set_status(SuccessStatus.SUCCESS)
        success_obj.set_message(SuccessMessage.CREATE_MESSAGE)
        success_obj.id=Header.id
        return success_obj