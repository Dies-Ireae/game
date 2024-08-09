from evennia.utils.test_resources import EvenniaTestCase
from evennia.objects.models import ObjectDB
from unittest.mock import patch, Mock
from evennia.accounts.models import AccountDB
from evennia.utils.create import create_object
from world.jobs.models import Job, JobTemplate, Queue, JobAttachment
from commands.jobs.jobs_commands import (
    CmdCreateJob, CmdClaimJob, CmdApproveJob, CmdRejectJob,
    CmdListJobs, CmdViewJob, CmdAddParticipant, CmdAttachObject,
    CmdRemoveObject, CmdCreateJobTemplate, CmdEditJobTemplate, CmdDeleteJobTemplate
)

class JobCommandTestCase(EvenniaTestCase):

    def setUp(self):
        super().setUp()
        self.requester = AccountDB.objects.create(username="requester")
        self.assignee = AccountDB.objects.create(username="assignee")
        self.queue = Queue.objects.create(name="SupportQueue")
        self.job_template = JobTemplate.objects.create(
            name="SupportTemplate",
            queue=self.queue,
            close_commands=["command1 {arg1}", "command2 {arg2}"],
            args={"arg1": "Description for arg1", "arg2": "Description for arg2"}
        )
        self.object = create_object(ObjectDB, key="TestObject")  # Ensure proper create_object usage
        self.job = Job.objects.create(
            title="Test Job",
            description="A job for testing",
            requester=self.requester,
            queue=self.queue,
            template_args={"arg1": "Value1", "arg2": "Value2"}
        )
        self.caller = Mock()
        self.caller.msg = Mock()
        self.caller.account = self.requester  # Ensure the caller has an account

    def test_cmd_create_job(self):
        command = CmdCreateJob()
        command.caller = self.caller
        command.msg = Mock()  # Mock the msg method on the command
        command.args = "New Job/New Job Description=SupportTemplate <arg1=Value1, arg2=Value2>"

        with patch('world.jobs.models.Queue.objects.first', return_value=self.queue):
            command.func()
            command.msg.assert_called_with("Job 'New Job' created with ID 2.")

        # Test missing title and description
        command.args = "New Job/New Job Description="
        command.func()
        command.msg.assert_called_with("Usage: +job/create <title>/<description> [= <template>] <args>")

    def test_cmd_claim_job(self):
        command = CmdClaimJob()
        command.caller = self.caller
        command.msg = Mock()  # Mock the msg method on the command
        command.args = "1"
        command.job_number = "1"  # Ensure job_number is set
        command.func()
        command.msg.assert_called_with("You have claimed the job: Test Job")
        self.job.refresh_from_db()  # Ensure the job is refreshed from the database
        self.assertEqual(self.job.assignee, self.requester)  # Check against the requester's account

        # Test invalid job ID
        command.args = "999"
        command.job_number = "999"
        command.func()
        command.msg.assert_called_with("Invalid job ID.")

    def test_cmd_approve_job(self):
        command = CmdApproveJob()
        command.caller = self.caller
        command.msg = Mock()  # Mock the msg method on the command
        command.args = "1"
        command.job_number = "1"  # Ensure job_number is set
        self.job.status = "open"
        self.job.claim(self.assignee)  # Use a valid AccountDB instance for claiming
        command.func()
        self.job.refresh_from_db()  # Ensure the job is refreshed from the database
        command.msg.assert_called_with("Job 'Test Job' has been approved and closed.")
        self.assertEqual(self.job.status, "closed")

    def test_cmd_reject_job(self):
        command = CmdRejectJob()
        command.caller = self.caller
        command.msg = Mock()  # Mock the msg method on the command
        command.args = "1"
        command.job_number = "1"  # Ensure job_number is set
        self.job.status = "open"
        command.func()
        self.job.refresh_from_db()  # Ensure the job is refreshed from the database
        command.msg.assert_called_with("Job 'Test Job' has been rejected.")
        self.assertEqual(self.job.status, "rejected")

    def test_cmd_list_jobs(self):
        command = CmdListJobs()
        command.caller = self.caller
        command.msg = Mock()  # Mock the msg method on the command
        command.args = ""
        command.func()
        command.msg.assert_called()

    def test_cmd_view_job(self):
        command = CmdViewJob()
        command.caller = self.caller
        command.msg = Mock()  # Mock the msg method on the command
        command.args = "1"
        command.job_number = "1"  # Ensure job_number is set
        command.parse()  # Ensure the arguments are parsed
        command.func()

        # Check that the job ID appears somewhere in the calls to msg
        command.msg.assert_any_call(Mock(), f"Job ID: {self.job.id}")
        print(command.msg.call_args_list)

        # Test with a job that doesn't exist
        command.args = "999"
        command.job_number = "999"
        command.func()
        command.msg.assert_called_with("Invalid job ID.")

    def test_cmd_add_participant(self):
        command = CmdAddParticipant()
        command.caller = self.caller
        command.msg = Mock()  # Mock the msg method on the command
        command.args = "1=assignee"
        
        command.parse()
        
        with patch('evennia.utils.search.search_account', return_value=[self.assignee]):
            command.func()
        
        command.msg.assert_called_with(f"{self.assignee.username} added to job #1.")


    def test_cmd_attach_object(self):
        command = CmdAttachObject()
        command.caller = self.caller
        command.msg = Mock()  # Mock the msg method on the command
        command.args = "1=TestObject:arg1"
        command.job_number = "1"  # Ensure job_number is set
        command.object_name = "TestObject"  # Ensure object_name is set
        command.func()
        command.msg.assert_called_with("Object 'TestObject' attached to job #1.")

        # Test attaching to a non-existing job
        command.args = "999=TestObject"
        command.job_number = "999"
        command.func()
        command.msg.assert_called_with("Job not found.")

    def test_cmd_remove_object(self):
        JobAttachment.objects.create(job=self.job, object=self.object)
        command = CmdRemoveObject()
        command.caller = self.caller
        command.msg = Mock()  # Mock the msg method on the command
        command.args = "1=TestObject"
        command.job_number = "1"  # Ensure job_number is set
        command.object_name = "TestObject"  # Ensure object_name is set
        command.func()
        command.msg.assert_called_with("Object 'TestObject' removed from job #1.")

        # Test removing a non-existing attachment
        command.args = "1=NonExistentObject"
        command.object_name = "NonExistentObject"  # Ensure object_name is set
        command.func()
        command.msg.assert_called_with("No object found with the name 'NonExistentObject'.")

    def test_cmd_create_job_template(self):
        command = CmdCreateJobTemplate()
        command.caller = self.caller
        command.msg = Mock()  # Mock the msg method on the command
        command.args = "NewTemplate/SupportQueue=cmd1;cmd2|arg1=Description1,arg2=Description2"
        
        command.func()
        
        command.msg.assert_called_with("JobTemplate 'NewTemplate' created successfully.")
        job_template = JobTemplate.objects.get(name__iexact="NewTemplate")
        self.assertIsNotNone(job_template)
        self.assertEqual(job_template.close_commands, ["cmd1", "cmd2"])
        self.assertEqual(job_template.args, {"arg1": "Description1", "arg2": "Description2"})

        # Test with an existing template name
        command.args = "NewTemplate/SupportQueue=cmd1;cmd2|arg1=Description1,arg2=Description2"
        command.func()
        command.msg.assert_called_with("A job template with the name 'NewTemplate' already exists.")

        # Test invalid queue
        command.args = "InvalidTemplate/InvalidQueue=cmd1;cmd2|arg1=Description1,arg2=Description2"
        command.func()
        command.msg.assert_called_with("No queue found with the name 'InvalidQueue'.")

        # Test invalid argument format
        command.args = "InvalidTemplate/SupportQueue=cmd1;cmd2|arg1=Description1,arg2"
        command.func()
        command.msg.assert_called_with("Invalid args format: Each argument must be in the form of 'key=value'. Use <arg1=description1,arg2=description2,...>")

    def test_cmd_edit_job_template(self):
        command = CmdEditJobTemplate()
        command.caller = self.caller
        command.msg = Mock()  # Mock the msg method on the command
        command.args = "SupportTemplate name=NewName queue=SupportQueue commands=cmd1|cmd2 args=arg1=NewDesc"
        command.func()
        command.msg.assert_called_with("JobTemplate 'NewName' updated successfully.")

        # Test editing non-existent template
        command.args = "NonExistentTemplate name=NewName queue=SupportQueue commands=cmd1|cmd2 args=arg1=NewDesc"
        command.func()
        command.msg.assert_called_with("No job template found with the name 'NonExistentTemplate'.")

    def test_cmd_delete_job_template(self):
        command = CmdDeleteJobTemplate()
        command.caller = self.caller
        command.msg = Mock()  # Mock the msg method on the command
        command.args = "SupportTemplate"
        command.func()
        command.msg.assert_called_with("JobTemplate 'SupportTemplate' deleted successfully.")

        # Test deleting non-existent template
        command.args = "NonExistentTemplate"
        command.func()
        command.msg.assert_called_with("No job template found with the name 'NonExistentTemplate'.")
