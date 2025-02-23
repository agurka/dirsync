import utils
import jobs


def main():
    args = utils.parse_args()
    if args["command"] == "setup":
        if jobs.add_job(args):
            jobs.schedule_job(args, __file__)

    if args["command"] == "run":
        jobs.run(args)

    if args["command"] == "jobs":
        if args["remove"]:
            if jobs.remove_job(args):
                jobs.remove_job_from_schedule(args)
        else:
            jobs.list_jobs(args)


if __name__ == "__main__":
    main()
