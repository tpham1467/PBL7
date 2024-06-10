class Job:
    def __init__(self, job_id, job_type, step, status, created_at, begin_at, end_at):
        self.job_id = job_id
        self.job_type = job_type
        self.step = step
        self.status = status
        self.created_at = created_at
        self.begin_at = begin_at
        self.end_at = end_at

    def __repr__(self):
        return f"Job(id={self.job_id}, type={self.job_type}, step={self.step}, status={self.status}, created_at={self.created_at}), begin_at={self.begin_at}, end_at={self.end_at}"
