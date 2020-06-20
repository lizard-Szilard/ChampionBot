from collections import defaultdict

class DictInMemory:
    """The main responsibility of this class is keep track job.queue object of
    "the schedule match a team" max 5 job.queue object (team).
    When the bot restrat a data will purge.
    TODO: Caused only dict object can manage job.queue object to store in memory.
    We can branch PTB and add a feature for storing job.queue object with named "context.job_data".
    """
    
    def __init__(self):
        self.job_data = defaultdict(dict)
        
    def job_enter(self, first_key, second_key):
        if not isinstance(first_key, int):
            raise ValueError("You First key is not int (chat_id)")
        if not isinstance(second_key, dict):
            raise ValueError("You Second key is not dict")
        self.job_data[first_key] = second_key
        return self.job_data

a = DictInMemory()
DATA_JOB = a.job_enter(1, dict(arsenal=[1,2,3])) # Must have one data
print(DATA_JOB[1])