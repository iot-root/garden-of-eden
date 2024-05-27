from flask import jsonify
from app.lib.lib import log 
from crontab import CronTab
import uuid
from functools import wraps
import re
from abc import ABC, abstractmethod
from collections import defaultdict
import os
import getpass
import logging


def validate_args(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            log("validating args")
            self._validateArgs(**kwargs)
            log("validating scheduke")
            self._validateSchedule(*args)
            log("validating state")
            self._validateState(**kwargs)
        except Exception as e:
            log(str(e))
            return {"error": str(e)}
        return func(self, *args, **kwargs)
    return wrapper


cron = CronTab(user=getpass.getuser())

class Scheduler(ABC):
    def __init__(self):
        self.cron = cron
        log('Initializing scheduler')
    
    # Helpers
    @abstractmethod
    def construct_command(self, *args, **kwargs):
        pass

    @abstractmethod
    def _validateArgs(self, **kwargs):
        pass

    def _validateSchedule(self, min, hour, day):
        log("validating schedule")
        if not (0 <= min <= 59):
            raise ValueError("min must be between 0 and 59")
        if not (0 <= hour <= 23):
            raise ValueError("hour must be between 0 and 23")
        if not (0 <= day <= 6):
            raise ValueError("day must be between 0 and 6")
        return

    def _validateState(self, **kwargs):
        log("validating state")
        try: 
            if kwargs["state"] is not None:
                if kwargs["state"] not in ['on', 'off']:
                    raise ValueError("state must be either 'on' or 'off'")
        except Exception as e:
            log(str(e))
        return

    # Scheduling Methods
    @validate_args
    def add(self, min, hour, day, *args, **kwargs):
        """Add a new job."""
        log('Adding job')
        id = str(uuid.uuid4())
        command = self.construct_command(**kwargs)
        job = self.cron.new(command=command, comment=id)
        job.minute.on(min)
        job.hour.on(hour)
        job.dow.on(day)
        job.enable()
        self.cron.write()
        return {"message": "Job added successfully", "id": id}

    def update(self, id, min, hour, day, *args, **kwargs):
        """Update a job by ID."""
        log('Updating job')
        job = self._find(id)
        if job:
            job.set_command(self.construct_command(*args, **kwargs))
            job.minute.on(min)
            job.hour.on(hour)
            job.dow.on(day)
            self.cron.write()
            return {"message": "Job updated successfully"}
        return {"error": "Job not found"}

    def delete(self, id):
        """Delete a job by ID."""
        log('Deleting job')
        self.cron.remove_all(comment=id)
        self.cron.write()

    def deleteAll(self):
        """Delete all jobs."""
        log('Deleting all jobs')
        self.cron.remove_all()
        self.cron.write()

    def getAll(self):
        """Get a sorted list of cron jobs."""
        log('Getting all jobs')
        jobs = [{'id': job.comment, 'command': job.command, 'schedule': str(job.slices), 'enabled': job.is_enabled()}
                for job in self.cron]

        log(self.cron)
        jobs = self._sort({'jobs': jobs})
        return jobs

    def _find(self, id):
        """Find a cron jobs by ID."""
        log('Finding job')
        for job in self.cron:
            if job.comment == id:
                return job
        return None

    def _sort(self, cron_jobs):
        """Sort a list of cron jobs by day of week, then by hour, then by minute."""
        def parse_cron_schedule(schedule):
            """Parse a cron schedule string into its components."""
            match = re.match(r'^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$', schedule)
            if match:
                minute, hour, day_of_month, month, day_of_week = match.groups()
                return {
                    'minute': minute,
                    'hour': hour,
                    'day_of_month': day_of_month,
                    'month': month,
                    'day_of_week': day_of_week
                }
            else:
                raise ValueError("Invalid cron schedule format")

        def handle_special(char):
            """Convert special characters to sortable integers."""
            if char == '*':
                return -1
            return int(char)

        def sort_key(job):
            schedule = parse_cron_schedule(job['schedule'])
            day_of_week = schedule['day_of_week']
            hour = schedule['hour']
            minute = schedule['minute']
            return (
                handle_special(day_of_week),
                handle_special(hour),
                handle_special(minute)
            )

        def extract_file_name(command):
            """Extract the file name (without extension) from the command."""
            match_sensor_script = re.search(r'/([^/]+)\.py', command)
            match_log_script = re.search(r'/(log-sensor-data)', command)
            
            if match_sensor_script:
                return match_sensor_script.group(1)
            elif match_log_script:
                return match_log_script.group(1)
            else:
                return 'unknown'

        # Group jobs by file name
        grouped_jobs = defaultdict(list)
        for job in cron_jobs['jobs']:
            file_name = extract_file_name(job['command'])
            grouped_jobs[file_name].append(job)

        # Sort jobs within each group
        sorted_grouped_jobs = {file_name: sorted(jobs, key=sort_key) for file_name, jobs in grouped_jobs.items()}

        return {"jobs": sorted_grouped_jobs}

class LightScheduler(Scheduler):
    def __init__(self):
        super().__init__()

    def construct_command(self, **kwargs):
        return f'python ~/garden-of-eden/api/sensors/light/light.py --{kwargs["state"]} --brightness {kwargs["brightness"]}'

    def _validateArgs(self, **kwargs):
        if not (0 <= kwargs["brightness"] <= 100):
            raise ValueError("brightness must be between 0 and 100")

class PumpScheduler(Scheduler):
    def __init__(self):
        super().__init__()

    def construct_command(self,**kwargs):
        return f'python ~/garden-of-eden/api/sensors/pump/pump.py --{kwargs["state"]} --speed {kwargs["speed"]}'

    def _validateArgs(self, **kwargs):
        if not (0 < kwargs["speed"] <= 100):
            raise ValueError("duration must be between 1 and 60 minutes")      

class LogScheduler(Scheduler):
    def __init__(self):
        super().__init__()

    def construct_command(self,**kwargs):
        return f'~/garden-of-eden/bin/api/log-sensor-data.sh'

    def _validateArgs(self, **kwargs):
        return
 

# Instances
pumpScheduler = PumpScheduler()
lightScheduler = LightScheduler()
logScheduler = LogScheduler()