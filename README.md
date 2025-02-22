# dirsync

Python script for synchronising 2 directories. No dependencies outside of standard library

## How to use

### Job creation

To create a job, use  
`./dirsync.py setup <job name> <source directory> <destination directory> <cron>`

### Job deletion

To remove a job, either:

- `./dirsync.py jobs -r <job name>`
- remove the job file (`~/.config/dirsync/jobs` for Linux-based systems, `%APPDATA%\\dirsync\\jobs` on Windows)

### Running a job

You should not need to run a job manually. But if you want to, run `./dirsync run <job name>`

### List all jobs

To see all jobs, use `./dirsync jobs`  
You can optionally provide a job name, to see a specific job configuration: `./dirsync jobs <job name>`
