import os
import sys
import logging
import json
import shutil
import filecmp
import argparse


def get_scheduled_task_name(job_name):
    return f"dirsync-{job_name}"


def set_logging(args, job):
    logging_setup = {
        "level": get_log_levels().get(args["verbosity"]),
        "format": "%(asctime)s - %(levelname)s - %(message)s",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    }

    logfile = job.get("logfile")
    if args["command"] == "setup":
        if logfile:
            logging_setup["filename"] = logfile
        else:
            print(
                "No logfile provided on job creation. Logs for this job will not be stored to a file"
            )

    if args["command"] == "run":
        if logfile:
            logging_setup["filename"] = logfile

    logging.basicConfig(**logging_setup)


def get_log_levels():
    return {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARNING,
        "error": logging.ERROR,
        "silent": logging.CRITICAL,
    }


def parse_args():
    desc = "dirsync performs one-way syncing of 2 directories"
    parser = argparse.ArgumentParser(description=desc)

    default_log_level = "warn"
    parser.add_argument(
        "-v",
        "--verbosity",
        choices=get_log_levels().keys(),
        default=default_log_level,
        help=f"Set verbosity level. Defaults to {default_log_level}.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    setup_parser = subparsers.add_parser("setup", help="setup and configure a sync job")
    setup_parser.add_argument("job", help="job name")
    setup_parser.add_argument("src", help="source directory")
    setup_parser.add_argument("dest", help="destination directory")
    setup_parser.add_argument(
        "scheduling",
        help="platform-specific scheduling (cron or windows task scheduler string)",
    )
    setup_parser.add_argument(
        "-l",
        "--logfile",
        help="path to log file. If not provided, no logs will be stored.",
        required=False,
        default=False,
    )

    run_parser = subparsers.add_parser("run", help="run a sync job")
    run_parser.add_argument("job", help="name of the job to run")

    jobs_parser = subparsers.add_parser("jobs", help="list jobs")
    jobs_parser.add_argument(
        "-r", "--remove", help="remove job by name", action="store_true"
    )
    jobs_parser.add_argument("name", nargs="?", help="list specific job")

    args = parser.parse_args()

    return args.__dict__


def get_or_create_job_directory():
    if sys.platform == "win32":
        path = os.getenv("APPDATA", "%APPDATA%")

    else:
        path = os.path.expanduser(os.path.join("~", ".config"))

    job_dir = os.path.join(path, "dirsync", "jobs")
    if not os.path.exists(job_dir):
        logging.info(f"Job directory not found. Creating {job_dir}")
        os.makedirs(job_dir)

    return job_dir


def get_job_by_name(jobname):
    job_dir = get_or_create_job_directory()
    job_filename = f"{jobname}.json"

    all_jobs = os.listdir(job_dir)
    if job_filename not in all_jobs:
        logging.error(f"job '{jobname}' does not exist")
        sys.exit(1)

    with open(f"{os.path.join(job_dir, job_filename)}") as jf:
        return json.load(jf)


def compare_trees(src_root, dest_root):
    """
    Function compares 2 trees, returning a dict with keys 'remove' and 'overwrite'.
    The values are lists with files that need removing or simply overwritten with src file
    """
    to_remove = []
    to_write = []

    source_files = {}
    dest_files = {}

    for root, _, files in os.walk(src_root):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), src_root)
            source_files[relative_path] = os.path.join(root, file)

    for root, _, files in os.walk(dest_root):
        for file in files:
            relative_path = os.path.relpath(os.path.join(root, file), dest_root)
            dest_files[relative_path] = os.path.join(root, file)

    for relative_path in dest_files:
        if relative_path not in source_files:
            to_remove.append(relative_path)

    for relative_path, source_file in source_files.items():
        if relative_path in dest_files:
            dest_file = dest_files[relative_path]
            if not filecmp.cmp(source_file, dest_file, shallow=False):
                to_write.append(relative_path)
        else:
            to_write.append(relative_path)

    return {"remove": to_remove, "write": to_write}


def copy_files(src, dest, files):
    for file in files:
        source_path = os.path.join(src, file)
        dest_path = os.path.join(dest, file)

        os.makedirs(os.path.dirname(dest_path), exist_ok=True)

        logging.debug(f"Writing file {source_path} to destination folder.")
        shutil.copy(source_path, dest_path)


def remove_files(dest, files):
    for file in files:
        path = os.path.join(dest, file)
        if os.path.isfile(path):
            logging.debug(f"Removing file {path}")
            os.remove(path)
        else:
            logging.debug(f"Removing directory {path}")
            shutil.rmtree(path)


def sync_directories(src, dest):
    diffs = compare_trees(src, dest)

    remove_files(dest, diffs["remove"])
    copy_files(src, dest, diffs["write"])

    logging.info(f"Directory {dest} is synced to {src}")
