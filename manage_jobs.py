import utils
import os
import json


def add_job(args):
    job_dir = utils.get_job_directory()

    job_name = args.job
    job_filename = f"{job_name}.json"
    job_filepath = os.path.join(job_dir, job_filename)

    src = os.path.abspath(args.src)
    dest = os.path.abspath(args.dest)
    log = args.logfile

    if job_filename in os.listdir(job_dir):
        print(
            f"Job '{job_name}' already exists. Create new name or remove '{job_filepath}'"
        )
        return

    job = {"src": src, "dest": dest, "logfile": log, "cron": None}
    with open(job_filepath, "w") as jf:
        json.dump(job, jf, sort_keys=True, indent=4)
