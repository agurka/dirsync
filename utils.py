import os
import sys
import logging


def get_log_levels():
    return {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARNING,
        "error": logging.ERROR,
        "silent": logging.CRITICAL,
    }


def get_job_directory():
    if sys.platform == "win32":
        path = os.getenv("APPDATA", "%APPDATA%")

    else:
        path = os.path.expanduser(os.path.join("~", ".config"))

    job_dir = os.path.join(path, "dirsync", "jobs")
    if not os.path.exists(job_dir):

        logging.info(f"Job directory not found. Creating {job_dir}")
        os.makedirs(job_dir)

    return job_dir
