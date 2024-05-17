from flask import jsonify
from api.lib.lib import log 
from crontab import CronTab
import uuid
from functools import wraps
import re
from abc import ABC, abstractmethod
from collections import defaultdict



def validate_args(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            self._validateArgs(*args, **kwargs)
        except ValueError as e:
            return {"status": "error", "message": str(e)}
        return func(self, *args, **kwargs)
    return wrapper

# TODO: change
cron = CronTab(user='peter')

class Scheduler(ABC):
    def __init__(self):
        self.cron = cron
        log('Initializing scheduler')
    
    @abstractmethod
    def construct_command(self, *args, **kwargs):
        pass

    @abstractmethod
    def _validateArgs(self, min, hour, day, *args, **kwargs):
        pass

    @validate_args
    def add(self, min, hour, day, *args, **kwargs):
        """Add a new job."""
        log('Adding job')
        id = str(uuid.uuid4())
        command = self.construct_command(*args, **kwargs)
        job = self.cron.new(command=command, comment=id)
        job.minute.on(min)
        job.hour.on(hour)
        job.dow.on(day)
        job.enable()
        self.cron.write()
        return {"status": "success", "message": "Job added successfully"}

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
            return {"status": "success", "message": "Job updated successfully"}
        return {"status": "error", "message": "Job not found"}

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

        print(self.cron)
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
            match = re.search(r'/([^/]+)\.py', command)
            if match:
                return match.group(1)
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

    def construct_command(self, state, brightness):
        return f'python ~/garden-of-eden/api/sensors/light/light.py --{state} --brightness {brightness}'

    def _validateArgs(self, min, hour, day, state, brightness):
        if not (0 <= min <= 59):
            raise ValueError("min must be between 0 and 59")
        if not (0 <= hour <= 23):
            raise ValueError("hour must be between 0 and 23")
        if not (0 <= day <= 6):
            raise ValueError("day must be between 0 and 6")
        if state not in ['on', 'off']:
            raise ValueError("state must be either 'on' or 'off'")
        if not (0 <= brightness <= 100):
            raise ValueError("brightness must be between 0 and 100")

class PumpScheduler(Scheduler):
    def __init__(self):
        super().__init__()

    def construct_command(self, state, speed):
        return f'python ~/garden-of-eden/api/sensors/pump/pump.py --{state} --speed {speed}'

    def _validateArgs(self, min, hour, day, state, speed):
        if not (0 <= min <= 59):
            raise ValueError("min must be between 0 and 59")
        if not (0 <= hour <= 23):
            raise ValueError("hour must be between 0 and 23")
        if not (0 <= day <= 6):
            raise ValueError("day must be between 0 and 6")
        if state not in ['on', 'off']:
            raise ValueError("state must be either 'on' or 'off'")
        if not (0 < speed <= 100):
            raise ValueError("duration must be between 1 and 60 minutes")      

pumpScheduler = PumpScheduler()
lightScheduler = LightScheduler()