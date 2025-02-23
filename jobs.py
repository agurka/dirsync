import utils
import json
import os
import logging
import subprocess
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
        logging.warning(f"No jobs found at {job_dir}")
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
    if not job_name:
        logging.error("must provide job name if 'remove' is true")
        return False

    job_filename = f"{job_name}.json"
    job_dir = utils.get_or_create_job_directory()
    if job_filename not in os.listdir(job_dir):
        logging.error(f"job {job_name} does not exist")
        return False

    job_filepath = os.path.join(job_dir, job_filename)
    logging.info(f"Removing job {job_filepath}")
    os.remove(job_filepath)

    job = utils.get_job_by_name(job_name)
    logfile = job.get("logfile")
    if logfile:
        os.remove(logfile)

    return True


def remove_job_from_schedule(args):
    task_name = utils.get_scheduled_task_name(args["name"])
    if os.name == "nt":
        cmd = [
            "schtasks",
            "/Delete",
            "/TN",
            task_name,
            "/F",
        ]
    else:
        cmd = f"crontab -l | grep -v '{task_name}' | crontab -"

    try:
        if os.name == "nt":
            subprocess.run(cmd, check=True)
        else:
            subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"error descheduling job: {e}")


def schedule_job(args, script_path):
    scheduling = args["scheduling"]

    job_name = args["job"]
    command = f"python {script_path} -v {args.get('verbosity')} run {job_name}"
    task_name = utils.get_scheduled_task_name(job_name)
    if os.name == "nt":
        schedule_cmd = [
            "schtasks",
            "/Create",
            "/TN",
            f"{task_name}",
            "/TR",
            f'"{command}"',
            "/SC",
            f"{scheduling}",
            "/F",
        ]
    else:
        cron_entry = f"{scheduling} {command} # {task_name}"
        schedule_cmd = f'(crontab -l; echo "{cron_entry}") | crontab -'
    try:
        if os.name == "nt":
            subprocess.run(schedule_cmd, check=True)
        else:
            subprocess.run(schedule_cmd, shell=True, check=True)
        logging.info(f"scheduled job '{job_name}' successfully")
    except subprocess.CalledProcessError as e:
        logging.error(f"error scheduling job: {e}")


def add_job(args):
    job_dir = utils.get_or_create_job_directory()

    job_name = args["job"]
    job_filename = f"{job_name}.json"
    job_filepath = os.path.join(job_dir, job_filename)

    src = os.path.abspath(args["src"])
    dest = os.path.abspath(args["dest"])
    log = args.get("logfile")
    if log:
        log = os.path.abspath(log)

    job = {"src": src, "dest": dest, "logfile": log, "scheduling": args["scheduling"]}
    utils.set_logging(args, job)

    if job_filename in os.listdir(job_dir):
        logging.error(
            f"Job '{job_name}' already exists. Create new name or remove '{job_filepath}'"
        )
        return False

    with open(job_filepath, "w") as jf:
        logging.info(f"creating job {job_name} at {job_filepath}")
        json.dump(job, jf, sort_keys=True, indent=4)
    return True


def run(args):
    job = utils.get_job_by_name(args["job"])

    utils.set_logging(args, job)
    logging.info("Starting sync job")

    utils.sync_directories(job["src"], job["dest"])
