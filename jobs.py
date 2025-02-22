import utils
import json
import os
from pprint import pprint


def list_specific_job(jobname):
    job_dir = utils.get_job_directory()
    with open(os.path.join(job_dir, f"{jobname}.json")) as f:
        job = json.load(f)
    pprint(job)


def list_all_jobs():
    job_dir = utils.get_job_directory()

    jobs = os.listdir(job_dir)
    jobs = [os.path.splitext(job)[0] for job in jobs]
    job_cnt = len(jobs)

    if not job_cnt:
        print(f"No jobs found at {job_dir}")
        return

    jobs_str = "\t" + "\n\t".join(jobs)
    print(f"{job_cnt} jobs found:\n{jobs_str}")


def list_jobs(args):
    if args.name:
        list_specific_job(args.name)
    else:
        list_all_jobs()
