# Evennia Job Management Commands

This project provides a series of commands for managing jobs and queues in an Evennia-based MUD. These commands allow players and administrators to create, claim, approve, reject, and manage jobs, as well as create and manage queues for job assignments.

## Commands

### Job Commands

#### `+job/create`
- **Usage:** `+job/create <title>/<description> [= <template>] <args>`
- **Description:** Creates a new job with the given title and description. Optionally, a template and arguments can be specified.
- **Example:** `+job/create Fix the server/Something is wrong with the server. Please fix it. = hardware issue <server_id=1234, location=datacenter>`

#### `+job/claim`
- **Usage:** `+job/claim <job ID>`
- **Description:** Allows a player to claim an open job.
- **Example:** `+job/claim 42`

#### `+job/approve`
- **Usage:** `+job/approve <job ID>`
- **Description:** Approves and closes a job. Only jobs that are open or claimed can be approved.
- **Example:** `+job/approve 42`

#### `+job/reject`
- **Usage:** `+job/reject <job ID>`
- **Description:** Rejects a job, setting its status to "rejected." Only jobs that are open or claimed can be rejected.
- **Example:** `+job/reject 42`

#### `+job/list`
- **Usage:** `+job/list [queue <queue_name>] [all]`
- **Description:** Lists jobs associated with the player, filtered by queue or status if specified.
- **Example:** `+job/list Default`

#### `+job`
- **Usage:** `+job <job ID>`
- **Description:** Displays detailed information about a specific job, including its status, requester, assignee, queue, and description.
- **Example:** `+job 42`

#### `+job/addparticipant`
- **Usage:** `+job/addparticipant <job_number>=<participant_name>`
- **Description:** Adds a participant to a job.
- **Example:** `+job/addparticipant 42=JohnDoe`

#### `+job/attach`
- **Usage:** `+job/attach <job ID>=<object name>[:<arg>]`
- **Description:** Attaches an object to a job.
- **Example:** `+job/attach 42=KeyItem1`

#### `+job/remove`
- **Usage:** `+job/remove <job ID>=<object name>`
- **Description:** Removes an attached object from a job.
- **Example:** `+job/remove 42=KeyItem1`

#### `+job/reassign`
- **Usage:** `+job/reassign <job ID>=<new assignee>`
- **Description:** Reassigns a job to a new assignee.
- **Example:** `+job/reassign 42=JaneDoe`

#### `+job/list_with_object`
- **Usage:** `+job/list_with_object <object_name>`
- **Description:** Lists all jobs that have a specified object attached.
- **Example:** `+job/list_with_object KeyItem1`

### Queue Commands

#### `+queue/create`
- **Usage:** `+queue/create <name>[=automatic_assignee]`
- **Description:** Creates a new queue for job assignments. Optionally, an automatic assignee can be specified.
- **Example:** `+queue/create BugFixQueue=AdminUser`

#### `+queue/edit`
- **Usage:** `+queue/edit <name> [name=<new_name>] [assignee=<automatic_assignee>]`
- **Description:** Edits an existing queue. You can change its name or set a new automatic assignee.
- **Example:** `+queue/edit BugFixQueue name=NewQueueName assignee=NewAdmin`

#### `+queue/delete`
- **Usage:** `+queue/delete <name>`
- **Description:** Deletes an existing queue.
- **Example:** `+queue/delete OldQueue`

#### `+queue/list`
- **Usage:** `+queue/list`
- **Description:** Lists all available queues along with their details.
- **Example:** `+queue/list`

#### `+queue/view`
- **Usage:** `+queue/view <queue name>`
- **Description:** Lists all jobs within a specific queue.
- **Example:** `+queue/view BugFixQueue`

### Job Template Commands

#### `+jobtemplate/create`
- **Usage:** `+jobtemplate/create <name>/<queue>=<cmd1;cmd2>|<arg1=desc1,arg2=desc2>`
- **Description:** Creates a new job template with the specified close commands and arguments.
- **Example:** `+jobtemplate/create FixBug/Development=cmd1;cmd2|arg1=description1,arg2=description2`

#### `+jobtemplate/edit`
- **Usage:** `+jobtemplate/edit <name> [name=<new_name>] [queue=<queue_name>] [commands=<cmd1;cmd2>] [args=<arg1=desc1,arg2=desc2>]`
- **Description:** Edits an existing job template, allowing changes to its name, queue, close commands, or arguments.
- **Example:** `+jobtemplate/edit FixBug name=FixCriticalBug queue=CriticalQueue commands=cmd3;cmd4 args=arg1=new_description`

#### `+jobtemplate/delete`
- **Usage:** `+jobtemplate/delete <name>`
- **Description:** Deletes an existing job template.
- **Example:** `+jobtemplate/delete OldTemplate`

## Installation and Setup

1. **Place the Command Classes:**
   - Copy the provided command classes into your Evennia `commands` module or another appropriate location in your project.

2. **Add Commands to Command Sets:**
   - Ensure that the commands are added to the appropriate command sets within your Evennia project so they are accessible to players.

3. **Database Models:**
   - Ensure the `Job`, `JobTemplate`, `Queue`, and `JobAttachment` models are correctly defined in your Django models and that migrations have been applied.

4. **Permissions:**
   - Adjust the command locks (`locks`) as needed to control who can use each command.

## Contributing

Feel free to fork this repository and submit pull requests. Contributions to improve the commands, add new features, or fix bugs are always welcome!

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

