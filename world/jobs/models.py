from django.db import models
from evennia.utils.utils import lazy_property
from evennia.objects.models import ObjectDB  # Assuming objects are instances of ObjectDB
from django.utils import timezone

class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    requester = models.ForeignKey("accounts.AccountDB", on_delete=models.CASCADE, related_name="requested_jobs")
    assignee = models.ForeignKey("accounts.AccountDB", null=True, blank=True, on_delete=models.SET_NULL, related_name="assigned_jobs")
    participants = models.ManyToManyField("accounts.AccountDB", related_name="participated_jobs", blank=True)
    queue = models.ForeignKey("Queue", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('open', 'Open'), ('claimed', 'Claimed'), ('closed', 'Closed'), ('rejected', 'Rejected')], default='open')
    template_args = models.JSONField(default=dict)  # Actual values of the args provided during job creation
    approved = models.BooleanField(default=False)
    comments = models.JSONField(default=list)
    due_date = models.DateTimeField(null=True, blank=True)
    attached_objects = models.ManyToManyField(ObjectDB, through='JobAttachment', related_name="attached_jobs", blank=True)


    def claim(self, user):
        if self.status == 'open':
            self.assignee = user
            self.status = 'claimed'
            self.save()
            # Check if the user has an active session
            if hasattr(user, 'sessions') and user.sessions.count():
                user.msg(f"You have been assigned to the job: {self.title}")

    def assign_to(self, user):
        self.assignee = user
        self.status = 'claimed'
        self.save()
        # Check if the user has an active session
        if hasattr(user, 'sessions') and user.sessions.count():
            user.msg(f"You have been reassigned to the job: {self.title}")


    def close(self):
        if self.approved:
            self.status = "closed"
            self.closed_at = timezone.now()  # Correctly set the closed_at field
            self.save()
            self.execute_close_commands()
        else:
            self.status = "rejected"
            self.save()

    def execute_close_commands(self):
        if not self.assignee:
            self.msg("Cannot execute close commands: no assignee.")
            return

        try:
            if not hasattr(self.queue, 'jobtemplate') or not self.queue.jobtemplate:
                return

            for command_template in self.queue.jobtemplate.close_commands:
                try:
                    filled_command = command_template.format(**self.template_args)
                    self.assignee.execute_cmd(filled_command)

                except KeyError as e:
                    if hasattr(self.assignee, 'msg'):
                        self.assignee.msg(f"Error executing command: missing argument {str(e)}")
                except Exception as e:
                    if hasattr(self.assignee, 'msg'):
                        self.assignee.msg(f"Error executing command: {str(e)}")

        except Exception as e:
            self.msg(f"Unexpected error during command execution: {str(e)}")

class JobAttachment(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    object = models.ForeignKey(ObjectDB, on_delete=models.CASCADE)
    attached_to_arg = models.CharField(max_length=255, null=True, blank=True)  # Stores the template arg if applicable

    def __str__(self):
        return f"Attachment: {self.object.key} to Job #{self.job.job_number} (Arg: {self.attached_to_arg or 'None'})"

class Queue(models.Model):
    name = models.CharField(max_length=255)
    automatic_assignee = models.ForeignKey("accounts.AccountDB", null=True, blank=True, on_delete=models.SET_NULL, related_name="auto_assigned_queues")

    def __str__(self):
        return self.name

class JobTemplate(models.Model):
    name = models.CharField(max_length=255)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE)
    close_commands = models.JSONField(default=list)  # Array of templated strings
    args = models.JSONField(default=dict)  # Expected args format, e.g., {"arg1": "description", "arg2": "description"}

    def __str__(self):
        return self.name
