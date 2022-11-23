from masterservice.models.mastermodels import LeaveGradeMapping , Grade
from utilityservice.service.applicationconstants import ApplicationNamespace
from utilityservice.service.threadlocal import NWisefinThread
from masterservice.util.masterutil import ModifyStatus
from datetime import timedelta,datetime
from attendanceservice.util.responsemessage import MessageResponse, StatusType
from utilityservice.data.response.nwisefinerror import NWisefinError
from utilityservice.data.response.nwisefinerrorconstants import ErrorMessage
from django.db.models import Q

class GradeMappingService(NWisefinThread):

    def __init__(self, scope):
        super().__init__(scope)
        self._set_namespace(ApplicationNamespace.MASTER_SERVICE)

    def gradeleave_mapping(self,data , emp_id):
        grade=data['grade']
        leave=data['leave']
        count=data['count']
        effective_from=data['effective_from']
        effective_from=(datetime.strptime(effective_from, '%Y-%m-%d').date())

        obj=LeaveGradeMapping.objects.using(self._current_app_schema()).filter(grade_id=grade,leave_id=leave,status=ModifyStatus.create).order_by('-id')

        if len(obj)> 0 :
            print(obj[0].id)
            active_effective_from = obj[0].effective_from
            effective_to =effective_from - timedelta(days=1)
            # print(effective_from,effective_to)
            print(active_effective_from,effective_from)
            if effective_from <= active_effective_from :
                error_obj = NWisefinError()
                error_obj.set_code(ErrorMessage.INVALID_DATA)
                error_obj.set_description("INVAILD Effective date")
                return error_obj

            LeaveGradeMapping.objects.using(self._current_app_schema()).filter(id=obj[0].id).update(effective_to=effective_to)

        LeaveGradeMapping.objects.using(self._current_app_schema()).create(grade_id=grade, leave_id=leave,effective_from=effective_from,leave_count=count,created_by=emp_id)

        success_obj = MessageResponse()
        success_obj.set_status(StatusType.SUCCESS)

        return success_obj


    def get_leave_grade(self,grade,month,year):

        grade_obj=Grade.objects.using(self._current_app_schema()).filter(code=grade,status=ModifyStatus.create)
        arr=[]
        if len(grade_obj)==0:
            return arr
        grade_id = grade_obj[0].id

        cond = Q(grade_id=grade_id,status=ModifyStatus.create)
        if month == None:
            cond &= Q(effective_to=None)
        else:
            cond &= (( Q(effective_to__month__gte=month) & Q(effective_to__year__gte=year))|Q(effective_to =None ))& Q(effective_from__month__lte=month) & Q(effective_from__year__lte=year)


        leave_obj=LeaveGradeMapping.objects.using(self._current_app_schema()).filter(cond).order_by('-id')

        for m in  leave_obj :
            leave_obj=m.leave
            leave_type ={"id":leave_obj.id,"name":leave_obj.name}
            leave_count = m.leave_count
            d={"leave_type":leave_type,"leave_count":leave_count}
            arr.append(d)

        return arr

    def get_active_grademapping(self):
        cond = Q( status=ModifyStatus.create)&Q(effective_to=None)

        leave_obj = LeaveGradeMapping.objects.using(self._current_app_schema()).filter(cond).order_by('-id').values()
        return leave_obj
