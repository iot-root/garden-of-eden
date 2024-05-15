from flask import jsonify
from api.lib.lib import log 
from crontab import CronTab
import uuid

class Scheduler:
    cron = CronTab(user='peter')

    def __init__(self):
        log('Initializing scheduler')

    def add(self, min):
        log('Adding job')
        id = str(uuid.uuid4())
        job = Scheduler.cron.new(command='python ~/garden-of-eden/api/sensors/light/light.py --on --brightness 100', comment=id)
        job.minute.every(min)
        job.enable()
        Scheduler.cron.write()
    
    def update(self, id, min):
        log('Updating job')
        job = self._find(id)
        job.minute.every(min)
        Scheduler.cron.write()

    def delete(self, id):
        log('Deleting job')
        Scheduler.cron.remove_all(comment=id)
        Scheduler.cron.write()

    def deleteAll(self):
        log('Deleting all jobs')
        Scheduler.cron.remove_all()
        Scheduler.cron.write()

    def getAll(self): 
        log('Getting all jobs')
        jobs = [{'id': job.comment, 'command': job.command, 'schedule': str(job.slices), 'enabled': job.is_enabled()}
            for job in Scheduler.cron]
        return {'jobs': jobs}

    def _find(self, id):
        log('Finding job')
        for job in Scheduler.cron:
            if job.comment == id:
                return job
        return None

    def _sortAll(self):
        log('Sorting jobs')

    

# lightsOn(time, duration, brightness)
# find by time