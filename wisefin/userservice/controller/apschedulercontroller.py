from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

now = datetime.now()

def scheduler_trigger_Trailbalance_Report():
    from entryservice.controller.entryeodcontroller import scheduler
    sched1 = BackgroundScheduler()
    # sched1.add_job(scheduler, 'interval', minutes=1)
    sched1.add_job(scheduler, 'cron', hour=23, minute=50)
    sched1.start()
    return True

def scheduler_trigger_Vendorbalance_Report():
    from reportservice.controller.vendoreodcontroller import vendorscheduler
    sched1 = BackgroundScheduler()
    # sched1.add_job(scheduler, 'interval', minutes=1)
    sched1.add_job(vendorscheduler, 'cron', hour=13, minute=47)
    sched1.start()
    return True
