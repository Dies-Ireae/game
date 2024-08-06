from evennia import Command
from evennia.utils import evtable
from world.jobs.models import Job, JobTemplate, Queue

from evennia import Command
from world.jobs.models import Job, JobTemplate, Queue

from evennia import Command
from world.jobs.models import Job, JobTemplate, Queue

class CmdCreateJob(Command):
    key = "@createjob"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.msg("Usage: @createjob <title>/<description> [= <template>] <args>")
            return
        
        title_desc, _, remainder = self.args.partition("=")
        title, _, description = title_desc.partition("/")
        template_name, _, args_str = remainder.partition("<args>")
        title = title.strip()
        description = description.strip()
        template_name = template_name.strip()
        args_str = args_str.strip()

        if not title or not description:
            self.msg("Both title and description must be provided.")
            return

        template = None
        template_args = {}
        close_commands = []

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
                self.msg("No queue found and no template specified.")
                return

        # Create the job
        job = Job.objects.create(
            title=title,
            description=description,
            requester=self.caller,
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




class CmdClaimJob(Command):
    key = "@claimjob"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.msg("Usage: @claimjob <job ID>")
            return

        try:
            job_id = int(self.args.strip())
            job = Job.objects.get(id=job_id)
            
            if job.status != 'open':
                self.msg("This job is not open for claiming.")
                return

            job.claim(self.caller)
            self.msg(f"You have claimed the job: {job.title}")
            
        except (ValueError, Job.DoesNotExist):
            self.msg("Invalid job ID.")
        except Exception as e:
            self.msg(f"Error claiming job: {str(e)}")


class CmdCloseJob(Command):
    key = "@closejob"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.msg("Usage: @closejob <job ID>")
            return

        try:
            job_id = int(self.args.strip())
            job = Job.objects.get(id=job_id)
            
            if job.assignee != self.caller:
                self.msg("You are not the assignee of this job.")
                return

            if job.status != 'claimed':
                self.msg("This job is not currently claimed.")
                return

            job.close()
            job.execute_close_commands()  # Execute the templated close commands
            self.msg(f"Job '{job.title}' has been closed.")
            
        except (ValueError, Job.DoesNotExist):
            self.msg("Invalid job ID.")
        except Exception as e:
            self.msg(f"Error closing job: {str(e)}")



class CmdListJobs(Command):
    key = "@listjobs"
    locks = "cmd:all()"

    def func(self):
        args = self.args.strip().lower()
        jobs = Job.objects.none()
        
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
                models.Q(requester=self.caller) |
                models.Q(assignee=self.caller) |
                models.Q(participants=self.caller)
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


class CmdViewJob(Command):
    key = "@viewjob"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.msg("Usage: @viewjob <job ID>")
            return

        try:
            job_id = int(self.args.strip())
            job = Job.objects.get(id=job_id)

            if not (job.requester == self.caller or job.assignee == self.caller or job.participants.filter(id=self.caller.id).exists()):
                self.msg("You do not have permission to view this job.")
                return

            self.msg(f"Job ID: {job.id}")
            self.msg(f"Title: {job.title}")
            self.msg(f"Description: {job.description}")
            self.msg(f"Status: {job.status}")
            self.msg(f"Requester: {job.requester}")
            self.msg(f"Assignee: {job.assignee if job.assignee else 'None'}")
            self.msg(f"Queue: {job.queue.name if job.queue else 'None'}")
            self.msg(f"Created At: {job.created_at}")
            self.msg(f"Closed At: {job.closed_at if job.closed_at else 'N/A'}")
            self.msg(f"Attached Objects: {job.attached_objects}")

        except (ValueError, Job.DoesNotExist):
            self.msg("Invalid job ID.")
        except Exception as e:
            self.msg(f"Error viewing job: {str(e)}")

