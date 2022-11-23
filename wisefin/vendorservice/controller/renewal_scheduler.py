from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime ,timedelta,date

from nwisefin.settings import logger

now = datetime.now()
# from vendorservice.controller import vendorcontroller
#
def scheduler_renewal():
    logger.info("renewal started")
    sched = BackgroundScheduler()
    current_time = datetime.now()
    h = current_time.hour
    m = current_time.minute
    s = current_time.second
    sched.add_job(scheduler_renewal_process, 'cron', hour=11, minute=45)
    sched.start()


def scheduler_renewal_process():
    from vendorservice.models import Vendor
    from vendorservice.controller import vendorcontroller
    from django.db.models import Q
    # vendorcontroller.modication_approve(ven)
    today = date.today()
    logger.info(str(today))
    ven_obj=Vendor.objects.filter(Q(renewal_date=today)&Q(requeststatus=5)&Q(vendor_status=5))
    for ren_vendor in ven_obj:
        vendor_id=ren_vendor.id
        vendorcontroller.renewal_approve(vendor_id)
    logger.info("obj len"+ ''+str(len(ven_obj)))
    logger.info("renewal end")
    # ven_obj.query


