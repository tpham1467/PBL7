class JobResult:
    def __init__(self, job_type, job_id, total_record, created_at, begin_at, end_at):
        self.job_type = job_type
        self.job_id = job_id
        self.total_record = total_record
        self.created_at = created_at
        self.begin_at = begin_at
        self.end_at = end_at

    def __repr__(self):
        return f"Job result(job_id={self.job_id}, job_type={self.job_type}, created_at={self.created_at}), begin_at={self.begin_at}, end_at={self.end_at}"
