from django.db import models
from evennia.utils.utils import lazy_property

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
    status = models.CharField(max_length=20, choices=[('open', 'Open'), ('claimed', 'Claimed'), ('closed', 'Closed')], default='open')
    attached_objects = models.JSONField(default=list, blank=True)  # Or use ManyToManyField with custom object manager
    template_args = models.JSONField(default=dict)  # Actual values of the args provided during job creation

    def claim(self, user):
        if self.status == 'open':
            self.assignee = user
            self.status = 'claimed'
            self.save()

    def close(self):
        if self.status == 'claimed' and self.assignee:
            self.status = 'closed'
            self.closed_at = timezone.now()
            self.save()
            self.execute_close_commands()

    def execute_close_commands(self):
        if not self.assignee:
            # If there's no assignee, there's no one to execute commands
            self.msg("Cannot execute close commands: no assignee.")
            return

        for command_template in self.queue.jobtemplate.close_commands:
            try:
                # Populate the template string with the provided arguments
                filled_command = command_template.format(**self.template_args)
                
                # Execute the filled command with the assignee as the caller
                # This assumes Evennia's `self.assignee` object has a method to interpret commands, like `execute_cmd`.
                self.assignee.execute_cmd(filled_command)

            except KeyError as e:
                # Handle missing template argument
                if hasattr(self.assignee, 'msg'):
                    self.assignee.msg(f"Error executing command: missing argument {str(e)}")
            except Exception as e:
                # Catch any other errors in command execution
                if hasattr(self.assignee, 'msg'):
                    self.assignee.msg(f"Error executing command: {str(e)}")


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
