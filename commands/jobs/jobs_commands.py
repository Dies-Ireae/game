from evennia import Command
from evennia.utils import evtable
from world.jobs.models import Job, JobTemplate, Queue, JobAttachment
from evennia.utils.search import search_account, search_object
from django.db import models

class CmdCreateJob(Command):
    key = "+job/create"
    locks = "cmd:all()"
    help_category = "Jobs"

    def func(self):
        if not self.args:
            self.msg("Usage: +job/create <title>/<description> [= <template>] <args>")
            return
        
        title_desc, _, remainder = self.args.partition("=")
        title, _, description = title_desc.partition("/")
        title = title.strip()
        description = description.strip()
        template_name, _, args_str = remainder.partition("<args>")
        template_name = template_name.strip()
        args_str = args_str.strip()

        if not title or not description:
            self.msg("Both title and description must be provided.")
            return

        template = None
        template_args = {}
        close_commands = []

        # Determine the queue to assign the job to
        queue = None
        if template_name:
            try:
                template = JobTemplate.objects.get(name__iexact=template_name)
                queue = template.queue
                close_commands = template.close_commands
                
                # Parse the args for the template
                try:
                    args_dict = dict(arg.split('=') for arg in args_str.split(','))
                    for arg_key, _ in template.args.items():
                        if arg_key not in args_dict:
                            self.msg(f"Missing argument '{arg_key}' for template.")
                            return
                    template_args = args_dict
                except ValueError:
                    self.msg("Invalid args format. Use <arg1=value1, arg2=value2, ...>")
                    return
                
            except JobTemplate.DoesNotExist:
                self.msg(f"No template found with the name '{template_name}'.")
                return
        else:
            queue = Queue.objects.first()

        if not queue:
            # If no queue is provided or found, create a default queue with no automatic assignee
            queue, created = Queue.objects.get_or_create(name="Default", automatic_assignee=None)
            if created:
                self.msg("No queue specified or found. Created and assigned to 'Default'.")

        # Ensure the requester is an AccountDB instance
        account = self.caller.account if hasattr(self.caller, 'account') else self.caller

        # Create the job
        job = Job.objects.create(
            title=title,
            description=description,
            requester=account,  # Use the AccountDB instance
            queue=queue,
            status='open',
            template_args=template_args
        )

        self.msg(f"Job '{job.title}' created with ID {job.id}.")

        # Assign automatic assignee if set
        if queue.automatic_assignee:
            job.assignee = queue.automatic_assignee
            job.status = 'claimed'
            job.save()
            self.msg(f"Job '{job.title}' automatically assigned to {queue.automatic_assignee}.")
            if hasattr(queue.automatic_assignee, 'sessions') and queue.automatic_assignee.sessions.exists():
                queue.automatic_assignee.msg(f"You have been assigned to the job '{job.title}'.")

class CmdClaimJob(Command):
    key = "+job/claim"
    locks = "cmd:all()"
    help_category = "Jobs"

    def func(self):
        if not self.args:
            self.msg("Usage: +job/claim <job ID>")
            return

        try:
            job_id = int(self.args.strip())
            job = Job.objects.get(id=job_id)

            if job.status != 'open':
                self.msg("This job is not open for claiming.")
                return

            account = self.caller.account if hasattr(self.caller, 'account') else self.caller
            job.claim(account)

            self.msg(f"You have claimed the job: {job.title}")
            
        except (ValueError, Job.DoesNotExist):
            self.msg("Invalid job ID.")
        except Exception as e:
            self.msg(f"Error claiming job: {str(e)}")


class CmdApproveJob(Command):
    key = "+job/approve"
    locks = "cmd:all()"
    help_category = "Jobs"

    def func(self):
        if not self.args:
            self.msg("Usage: +job/approve <job ID>")
            return

        try:
            job_id = int(self.args.strip())
            job = Job.objects.get(id=job_id)
            
            if job.status not in ["open", "claimed"]:
                self.msg("This job cannot be approved.")
                return

            job.approved = True
            job.close()  # Automatically closes and executes close commands
            self.msg(f"Job '{job.title}' has been approved and closed.")
            
        except (ValueError, Job.DoesNotExist):
            self.msg("Invalid job ID.")
        except Exception as e:
            self.msg(f"Error approving job: {str(e)}")

class CmdRejectJob(Command):
    key = "+job/reject"
    locks = "cmd:all()"
    help_category = "Jobs"

    def func(self):
        if not self.args:
            self.msg("Usage: +job/reject <job ID>")
            return

        try:
            job_id = int(self.args.strip())
            job = Job.objects.get(id=job_id)
            
            if job.status not in ["open", "claimed"]:
                self.msg("This job cannot be rejected.")
                return

            job.approved = False
            job.close()  # This sets the status to "rejected" without executing close commands
            self.msg(f"Job '{job.title}' has been rejected.")
            
        except (ValueError, Job.DoesNotExist):
            self.msg("Invalid job ID.")
        except Exception as e:
            self.msg(f"Error rejecting job: {str(e)}")

class CmdListJobs(Command):
    key = "+job/list"
    locks = "cmd:all()"
    help_category = "Jobs"

    def func(self):
        args = self.args.strip().lower()
        jobs = Job.objects.none()

        account = self.caller.account if hasattr(self.caller, 'account') else self.caller
        
        if "queue" in args:
            queue_name = args.split("queue", 1)[1].strip()
            try:
                queue = Queue.objects.get(name__iexact=queue_name)
                jobs = Job.objects.filter(queue=queue)
            except Queue.DoesNotExist:
                self.msg(f"No queue found with the name '{queue_name}'.")
                return
        else:
            jobs = Job.objects.filter(
                models.Q(requester=account) |
                models.Q(assignee=account) |
                models.Q(participants=account)
            )

        if "all" not in args:
            jobs = jobs.filter(status__in=['open', 'claimed'])

        if not jobs.exists():
            self.msg("No jobs found.")
            return

        table = evtable.EvTable("ID", "Title", "Status", "Requester", "Assignee", "Queue")
        for job in jobs:
            table.add_row(
                job.id, job.title, job.status,
                job.requester.key, job.assignee.key if job.assignee else "None",
                job.queue.name if job.queue else "None"
            )
        self.msg(table)

from evennia import Command
from evennia.utils import evtable
from world.jobs.models import Job, JobTemplate, Queue, JobAttachment
from textwrap import fill

class CmdViewJob(Command):
    key = "+job"
    locks = "cmd:all()"
    help_category = "Jobs"

    def func(self):
        if not self.args:
            self.msg("Usage: +job <job ID>")
            return

        try:
            job_id = int(self.args.strip())
            job = Job.objects.get(id=job_id)

            # Ensure we're comparing the correct object types
            account = self.caller.account if hasattr(self.caller, 'account') else self.caller

            if not (job.requester == account or job.assignee == account or job.participants.filter(id=account.id).exists()):
                self.msg("You do not have permission to view this job.")
                return

            # Creating the table with job metadata
            table = evtable.EvTable(
                "|wAttribute|n", "|wValue|n",
                border=None,  # No border for metadata table
                align="l",  # Aligns all columns to the left
                width=80  # Sets the total width of the table
            )
            
            table.add_row("Job ID:", job.id)
            table.add_row("Title:", job.title)
            table.add_row("Status:", job.status)
            table.add_row("Requester:", job.requester)
            table.add_row("Assignee:", job.assignee.key if job.assignee else "None")
            table.add_row("Queue:", job.queue.name if job.queue else "None")
            table.add_row("Created At:", job.created_at)
            table.add_row("Closed At:", job.closed_at if job.closed_at else "N/A")
            table.add_row("Attached Objects:", ", ".join([str(obj.key) for obj in job.attached_objects.all()]))

            # Wrapping the description text to fit the table width
            wrapped_description = fill(job.description, width=80)

            # Sending the metadata table
            self.msg(table)

            # Adding a separator line and the full description
            self.msg("\n" + "-"*80 + "\n")
            self.msg(f"|wDescription:|n\n{wrapped_description}")

        except (ValueError, Job.DoesNotExist):
            self.msg("Invalid job ID.")
        except Exception as e:
            self.msg(f"Error viewing job: {str(e)}")


class CmdAddParticipant(Command):
    key = "+job/addparticipant"
    locks = "cmd:all()"
    help_category = "Jobs"
    
    def parse(self):
        """
        Parse the command arguments.
        Expected format: <job_number>=<participant_name>
        """
        if "=" in self.args:
            self.job_number, self.participant_name = [part.strip() for part in self.args.split("=", 1)]
        else:
            self.job_number = self.args.strip()
            self.participant_name = None  # Indicates that participant_name was not provided
    
    def func(self):
        """
        Execute the command to add a participant to a job.
        """
        # Check if participant name was provided
        if not self.participant_name:
            self.caller.msg("Usage: +job/addparticipant <job_number>=<participant_name>")
            return
        
        # Validate job number
        try:
            job_id = int(self.job_number)
        except ValueError:
            self.caller.msg("Invalid job number. Please provide a valid number.")
            return
        
        # Retrieve the job
        try:
            job = Job.objects.get(id=job_id)
        except Job.DoesNotExist:
            self.caller.msg(f"Job with ID {job_id} does not exist.")
            return
        
        # Search for the participant account
        participant = search_account(self.participant_name)
        if not participant:
            self.caller.msg(f"No such player: {self.participant_name}")
            return
        
        # Add participant to the job
        job.participants.add(participant[0])
        job.save()
        
        self.caller.msg(f"{participant[0].name} added to job #{job.id}.")

class CmdAttachObject(Command):
    key = "+job/attach"
    locks = "cmd:all()"
    help_category = "Jobs"

    def parse(self):
        try:
            job_number, object_name_arg = self.args.split("=", 1)
            self.job_number = int(job_number.strip())
            object_name, _, attached_to_arg = object_name_arg.partition(":")
            self.object_name = object_name.strip()
            self.attached_to_arg = attached_to_arg.strip() if attached_to_arg else None
        except ValueError:
            self.job_number = None
            self.object_name = ""
            self.attached_to_arg = None

    def func(self):
        if not self.job_number or not self.object_name:
            self.msg("Usage: +job/attach <job ID>=<object name>[:<arg>]")
            return

        try:
            job = Job.objects.get(id=self.job_number)
            obj = search_object(self.object_name)
            
            if not obj:
                self.msg(f"No object found with the name '{self.object_name}'.")
                return

            if self.attached_to_arg and job.template_args and self.attached_to_arg not in job.template_args:
                self.msg(f"No argument '{self.attached_to_arg}' found in this job's template.")
                return

            JobAttachment.objects.create(job=job, object=obj[0], attached_to_arg=self.attached_to_arg)
            self.msg(f"Object '{obj[0].key}' attached to job #{job.id}.")
            if self.attached_to_arg:
                self.msg(f"Attached to template argument '{self.attached_to_arg}'.")
            
        except Job.DoesNotExist:
            self.msg("Job not found.")
        except Exception as e:
            self.msg(f"Error attaching object: {str(e)}")

class CmdRemoveObject(Command):
    key = "+job/remove"
    locks = "cmd:all()"
    help_category = "Jobs"

    def parse(self):
        try:
            job_number, object_name = self.args.split("=", 1)
            self.job_number = int(job_number.strip())
            self.object_name = object_name.strip()
        except ValueError:
            self.job_number = None
            self.object_name = ""

    def func(self):
        if not self.job_number or not self.object_name:
            self.msg("Usage: +job/remove <job ID>=<object name>")
            return

        try:
            job = Job.objects.get(id=self.job_number)
            obj = search_object(self.object_name)
            
            if not obj:
                self.msg(f"No object found with the name '{self.object_name}'.")
                return

            attachment = JobAttachment.objects.filter(job=job, object=obj[0]).first()
            if not attachment:
                self.msg(f"Object '{obj[0].key}' is not attached to job #{job.id}.")
                return

            attachment.delete()
            self.msg(f"Object '{obj[0].key}' removed from job #{job.id}.")
            
        except Job.DoesNotExist:
            self.msg("Job not found.")
        except Exception as e:
            self.msg(f"Error removing object: {str(e)}")

class CmdCreateJobTemplate(Command):
    key = "+jobtemplate/create"
    locks = "perm(Admin)"  # Adjust the lock to your needs
    help_category = "Jobs"

    def func(self):
        if not self.args:
            self.msg("Usage: +jobtemplate/create <name>/<queue>=<cmd1;cmd2>|<arg1=desc1,arg2=desc2>")
            return
        
        try:
            # Parse and strip input components
            name_queue, _, details = self.args.partition("=")
            name, _, queue_name = name_queue.partition("/")
            close_commands_str, _, args_str = details.partition("|")
            
            name = name.strip()
            queue_name = queue_name.strip()
            
            # Check if close_commands and args are provided
            if not close_commands_str or not args_str:
                self.msg("Both close_commands and args must be provided.")
                return
            
            # Parse close commands using semicolon as a delimiter
            close_commands = [cmd.strip() for cmd in close_commands_str.split(";") if cmd.strip()]

            # Parse args into a dictionary using comma as a delimiter
            args = {}
            for arg in args_str.split(","):
                if "=" not in arg:
                    raise ValueError("Each argument must be in the form of 'key=value'.")
                key, value = arg.split("=", 1)
                args[key.strip()] = value.strip()

            # Fetch the queue
            queue = Queue.objects.get(name__iexact=queue_name)

            # Check for an existing job template with the same name
            if JobTemplate.objects.filter(name__iexact=name).exists():
                self.msg(f"A job template with the name '{name}' already exists.")
                return

            # Create the job template
            job_template = JobTemplate.objects.create(
                name=name,
                queue=queue,
                close_commands=close_commands,
                args=args
            )

            self.msg(f"JobTemplate '{job_template.name}' created successfully.")

        except Queue.DoesNotExist:
            self.msg(f"No queue found with the name '{queue_name}'.")
        except ValueError as e:
            self.msg(f"Invalid args format: {str(e)} Use <arg1=description1,arg2=description2,...>")
        except Exception as e:
            self.msg(f"Error creating job template: {str(e)}")



class CmdEditJobTemplate(Command):
    key = "+jobtemplate/edit"
    locks = "perm(Admin)"  # Adjust the lock to your needs
    help_category = "Jobs"

    def func(self):
        if not self.args:
            self.msg("Usage: +jobtemplate/edit <name> [name=<new_name>] [queue=<queue_name>] [commands=<cmd1;cmd2>] [args=<arg1=desc1,arg2=desc2>]")
            return
        
        try:
            name, _, updates = self.args.partition(" ")
            name = name.strip()

            job_template = JobTemplate.objects.get(name__iexact=name)
            updates = updates.split(" ")
            for update in updates:
                field, _, value = update.partition("=")
                value = value.strip()

                if field == "name":
                    job_template.name = value
                elif field == "queue":
                    queue = Queue.objects.get(name__iexact=value)
                    job_template.queue = queue
                elif field == "commands":
                    # Parse close commands using semicolon as a delimiter
                    job_template.close_commands = [cmd.strip() for cmd in value.split(";") if cmd.strip()]
                elif field == "args":
                    # Parse args into a dictionary using comma as a delimiter
                    job_template.args = {}
                    for arg in value.split(","):
                        if "=" not in arg:
                            raise ValueError("Each argument must be in the form of 'key=value'.")
                        key, arg_value = arg.split("=", 1)
                        job_template.args[key.strip()] = arg_value.strip()
                else:
                    self.msg(f"Unknown field: {field}")
                    return

            job_template.save()
            self.msg(f"JobTemplate '{job_template.name}' updated successfully.")

        except JobTemplate.DoesNotExist:
            self.msg(f"No job template found with the name '{name}'.")
        except Queue.DoesNotExist:
            self.msg(f"No queue found with the name '{value}'.")
        except ValueError as e:
            self.msg(f"Invalid args format: {str(e)} Use <arg1=desc1,arg2=desc2,...>")
        except Exception as e:
            self.msg(f"Error editing job template: {str(e)}")


class CmdDeleteJobTemplate(Command):
    key = "+jobtemplate/delete"
    locks = "perm(Admin)"  # Adjust the lock to your needs
    help_category = "Jobs"

    def func(self):
        if not self.args:
            self.msg("Usage: +jobtemplate/delete <name>")
            return

        try:
            name = self.args.strip()
            job_template = JobTemplate.objects.get(name__iexact=name)
            job_template.delete()

            self.msg(f"JobTemplate '{name}' deleted successfully.")

        except JobTemplate.DoesNotExist:
            self.msg(f"No job template found with the name '{name}'.")
        except Exception as e:
            self.msg(f"Error deleting job template: {str(e)}")

class CmdCreateQueue(Command):
    key = "+queue/create"
    locks = "perm(Admin)"  # Adjust the lock to your needs
    help_category = "Jobs"

    def func(self):
        if not self.args:
            self.msg("Usage: +queue/create <name>[=automatic_assignee]")
            return
        
        try:
            name_assignee = self.args.split("=")
            name = name_assignee[0].strip()
            assignee_name = name_assignee[1].strip() if len(name_assignee) > 1 else None

            if Queue.objects.filter(name__iexact=name).exists():
                self.msg(f"A queue with the name '{name}' already exists.")
                return

            assignee = None
            if assignee_name:
                assignee = search_account(assignee_name)
                if not assignee:
                    self.msg(f"No such player: {assignee_name}")
                    return
                assignee = assignee[0]

            queue = Queue.objects.create(
                name=name,
                automatic_assignee=assignee  # This will be None if no assignee is specified
            )

            self.msg(f"Queue '{queue.name}' created successfully.")
            if assignee:
                self.msg(f"Automatic assignee set to {assignee.key}.")
        
        except Exception as e:
            self.msg(f"Error creating queue: {str(e)}")


class CmdEditQueue(Command):
    key = "+queue/edit"
    locks = "perm(Admin)"  # Adjust the lock to your needs
    help_category = "Jobs"

    def func(self):
        if not self.args:
            self.msg("Usage: +queue/edit <name> [name=<new_name>] [assignee=<automatic_assignee>]")
            return
        
        try:
            name, _, updates = self.args.partition(" ")
            name = name.strip()

            queue = Queue.objects.get(name__iexact=name)
            updates = updates.split(" ")
            for update in updates:
                field, _, value = update.partition("=")
                value = value.strip()

                if field == "name":
                    queue.name = value
                elif field == "assignee":
                    assignee = search_account(value)
                    if not assignee:
                        self.msg(f"No such player: {value}")
                        return
                    queue.automatic_assignee = assignee[0]
                else:
                    self.msg(f"Unknown field: {field}")
                    return

            queue.save()
            self.msg(f"Queue '{queue.name}' updated successfully.")

        except Queue.DoesNotExist:
            self.msg(f"No queue found with the name '{name}'.")
        except Exception as e:
            self.msg(f"Error editing queue: {str(e)}")

class CmdDeleteQueue(Command):
    key = "+queue/delete"
    locks = "perm(Admin)"  # Adjust the lock to your needs
    help_category = "Jobs"

    def func(self):
        if not self.args:
            self.msg("Usage: +queue/delete <name>")
            return

        try:
            name = self.args.strip()
            queue = Queue.objects.get(name__iexact=name)
            queue.delete()

            self.msg(f"Queue '{name}' deleted successfully.")

        except Queue.DoesNotExist:
            self.msg(f"No queue found with the name '{name}'.")
        except Exception as e:
            self.msg(f"Error deleting queue: {str(e)}")


class CmdListQueues(Command):
    key = "+queue/list"
    locks = "cmd:all()"
    help_category = "Jobs"

    def func(self):
        queues = Queue.objects.all()

        if not queues.exists():
            self.msg("No queues found.")
            return

        # Creating the table with alignment and column separation
        table = evtable.EvTable(
            "|wQueue Name|n", "|wAutomatic Assignee|n", "|wTotal Open Jobs|n", "|wTotal Unclaimed Jobs|n",
            border="table",  # Adds a border around the table
            align="l",  # Aligns all columns to the left
            header_line_char="-",  # Sets the header line character
            width=100  # Sets the total width of the table
        )

        for queue in queues:
            assignee = queue.automatic_assignee.key if queue.automatic_assignee else "None"
            total_open_jobs = Job.objects.filter(queue=queue, status='open').count()
            total_unclaimed_jobs = Job.objects.filter(queue=queue, status='open', assignee__isnull=True).count()
            table.add_row(queue.name, assignee, total_open_jobs, total_unclaimed_jobs)
        
        self.msg(table)


class CmdReassignJob(Command):
    key = "+job/reassign"
    locks = "cmd:all()"
    help_category = "Jobs"

    def func(self):
        if not self.args:
            self.msg("Usage: +job/reassign <job ID>=<new assignee>")
            return

        try:
            job_id, new_assignee_name = self.args.split("=", 1)
            job_id = int(job_id.strip())
            new_assignee_name = new_assignee_name.strip()

            job = Job.objects.get(id=job_id)
            new_assignee = search_account(new_assignee_name)

            if not new_assignee:
                self.msg(f"No such player: {new_assignee_name}")
                return

            job.assignee = new_assignee[0]
            job.save()
            self.msg(f"Job '{job.title}' reassigned to {new_assignee[0].key}.")
            if hasattr(new_assignee[0], 'sessions') and new_assignee[0].sessions.exists():
                new_assignee[0].msg(f"You have been reassigned to the job '{job.title}'.")

            # Creating the table with alignment and column separation
            table = evtable.EvTable(
                "|wJob ID|n", "|wNew Assignee|n", "|wTitle|n", "|wStatus|n",
                border="table",  # Adds a border around the table
                align="l",  # Aligns all columns to the left
                header_line_char="-",  # Sets the header line character
                width=80  # Sets the total width of the table
            )
            
            table.add_row(job.id, new_assignee[0].key, job.title, job.status)
            self.msg(table)
        
        except (ValueError, Job.DoesNotExist):
            self.msg("Invalid job ID.")
        except Exception as e:
            self.msg(f"Error reassigning job: {str(e)}")

class CmdViewQueueJobs(Command):
    key = "+queue/view"
    locks = "cmd:all()"
    help_category = "Jobs"

    def func(self):
        if not self.args:
            self.msg("Usage: +queue/view <queue name>")
            return

        queue_name = self.args.strip()
        try:
            queue = Queue.objects.get(name__iexact=queue_name)
            jobs = Job.objects.filter(queue=queue).order_by('status')

            if not jobs.exists():
                self.msg(f"No jobs found in the queue '{queue_name}'.")
                return

            # Creating the table with alignment and column separation
            table = evtable.EvTable(
                "|wID|n", "|wTitle|n", "|wStatus|n", "|wRequester|n", "|wAssignee|n",
                border="table",  # Adds a border around the table
                align="l",  # Aligns all columns to the left
                header_line_char="-",  # Sets the header line character
                width=80  # Sets the total width of the table
            )
            
            for job in jobs:
                table.add_row(
                    job.id, job.title, job.status,
                    job.requester.key, job.assignee.key if job.assignee else "None"
                )
            self.msg(f"Jobs in queue '{queue_name}':")
            self.msg(table)

        except Queue.DoesNotExist:
            self.msg(f"No queue found with the name '{queue_name}'.")
