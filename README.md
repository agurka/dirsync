# dirsync

Python script for synchronising 2 directories. No dependencies outside of standard library

## How to use

### Job creation

`./dirsync.py setup <job name> <source directory> <destination directory> <scheduling>`

### Job deletion

`./dirsync.py jobs -r <job name>`

### Running a job

You should not need to run a job manually. But if you want to, run `./dirsync run <job name>`

### List all jobs

To see all jobs, use `./dirsync jobs`  
You can optionally provide a job name, to see a specific job configuration: `./dirsync jobs <job name>`

## Scheduling

Running the job on schedule is handled by the system. Whatever you pass to the `scheduling` argument gets passed either to `crontab` on Linux or `schtasks` on Windows
