import argparse
import utils
import logging


def set_logging(args):
    logging.basicConfig(level=utils.get_log_levels().get(args.verbosity))


def main():
    desc = "dirsync performs one-way syncing of 2 directories"
    parser = argparse.ArgumentParser(description=desc)

    default_log_level = "warn"
    parser.add_argument(
        "-v",
        "--verbosity",
        choices=utils.get_log_levels().keys(),
        default=default_log_level,
        help=f"Set verbosity level. Defaults to {default_log_level}.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    setup_parser = subparsers.add_parser("setup", help="setup and configure a sync job")
    setup_parser.add_argument("job", help="job name")
    setup_parser.add_argument("src", help="source directory")
    setup_parser.add_argument("dest", help="destination directory")
    setup_parser.add_argument(
        "-l",
        "--logfile",
        help="path to log file. If not provided, no logs will be stored.",
        required=False,
    )

    run_parser = subparsers.add_parser("run", help="run a sync job")
    run_parser.add_argument("job", help="name of the job to run")

    list_parser = subparsers.add_parser("jobs", help="list jobs")
    list_parser.add_argument("-n", "--name", help="list specific job")

    args = parser.parse_args()
    set_logging(args)

    if args.command == "setup":
        import manage_jobs

        manage_jobs.add_job(args)

    if args.command == "run":
        print("RUN")

    if args.command == "jobs":
        import jobs

        jobs.list_jobs(args)


if __name__ == "__main__":
    main()
