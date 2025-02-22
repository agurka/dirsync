import utils
import json
import os
import logging
from pprint import pprint


def list_specific_job(jobname):
    job = utils.get_job_by_name(jobname)
    print(f"{jobname}:")
    pprint(job)


def list_all_jobs():
    job_dir = utils.get_or_create_job_directory()

    jobs = os.listdir(job_dir)
    jobs = [os.path.splitext(job)[0] for job in jobs]
    job_cnt = len(jobs)

    if not job_cnt:
        print(f"No jobs found at {job_dir}")
        return

    jobs_str = "\t" + "\n\t".join(jobs)
    print(f"{job_cnt} jobs found:\n{jobs_str}")


def list_jobs(args):
    if args["name"]:
        list_specific_job(args["name"])
    else:
        list_all_jobs()


def remove_job(args):
    job_name = args.get("name")
    assert job_name, "must provide job name if 'remove' is true"

    job_filepath = os.path.join(utils.get_or_create_job_directory(), f"{job_name}.json")

    logging.info(f"Removing job {job_filepath}")
    os.remove(job_filepath)


def add_job(args):
    job_dir = utils.get_or_create_job_directory()

    job_name = args["job"]
    job_filename = f"{job_name}.json"
    job_filepath = os.path.join(job_dir, job_filename)

    src = os.path.abspath(args["src"])
    dest = os.path.abspath(args["dest"])
    log = os.path.abspath(args["logfile"])

    if job_filename in os.listdir(job_dir):
        print(
            f"Job '{job_name}' already exists. Create new name or remove '{job_filepath}'"
        )
        return

    job = {"src": src, "dest": dest, "logfile": log, "cron": None}
    utils.set_logging(args, job)
    with open(job_filepath, "w") as jf:
        logging.info(f"created job {job_name} at {job_filepath}")
        json.dump(job, jf, sort_keys=True, indent=4)


def run(args):
    job = utils.get_job_by_name(args["job"])

    utils.set_logging(args, job)
    logging.info("Starting sync job")

    utils.sync_directories(job["src"], job["dest"])
