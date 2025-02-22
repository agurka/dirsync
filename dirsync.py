import utils
import jobs


def main():
    args = utils.parse_args()
    if args["command"] == "setup":
        jobs.add_job(args)

    if args["command"] == "run":
        jobs.run(args)

    if args["command"] == "jobs":
        if args["remove"]:
            jobs.remove_job(args)
        else:
            jobs.list_jobs(args)


if __name__ == "__main__":
    main()
