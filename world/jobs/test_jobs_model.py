import unittest
from unittest.mock import Mock, patch
from evennia import create_object
from evennia.accounts.models import AccountDB
from evennia.objects.models import ObjectDB
from world.jobs.models import Job, JobAttachment, Queue, JobTemplate
from django.utils import timezone
from datetime import timedelta

class TestJobModel(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment.
        """
        self.requester = AccountDB.objects.create_user(
            "Requester", email="requester@example.com", password="adsfaw4tga4tq43t4!"
        )
        self.assignee = AccountDB.objects.create_user(
            "Assignee", email="assignee@example.com", password="adsfaw4tga4tq43t4!"
        )
        
        self.queue = Queue.objects.create(name="TestQueue")
        self.job_template = JobTemplate.objects.create(
            name="TestTemplate", queue=self.queue, close_commands=["do_something {arg1}"], args={"arg1": "value"}
        )

        self.job = Job.objects.create(
            title="Test Job",
            description="Test Job Description",
            requester=self.requester,
            queue=self.queue
        )

        # Create the in-game object linked to the assignee
        self.assignee_obj = create_object(ObjectDB, key="AssigneeObj")
        self.assignee_obj.db_player = self.assignee  # Link the object to the account

        # Create a test object for attachment
        self.obj = create_object(ObjectDB, key="TestObject")

    def tearDown(self):
        """
        Clean up the test environment.
        """
        Job.objects.all().delete()
        JobAttachment.objects.all().delete()
        Queue.objects.all().delete()
        JobTemplate.objects.all().delete()
        AccountDB.objects.all().delete()
        ObjectDB.objects.all().delete()

    def test_job_creation(self):
        """
        Test creating a job.
        """
        self.assertIsNotNone(self.job)
        self.assertEqual(self.job.title, "Test Job")
        self.assertEqual(self.job.description, "Test Job Description")
        self.assertEqual(self.job.requester, self.requester)
        self.assertEqual(self.job.queue, self.queue)

    def test_job_attachment_creation(self):
        """
        Test attaching an object to a job.
        """
        attachment = JobAttachment.objects.create(job=self.job, object=self.obj)
        self.assertIsNotNone(attachment)
        self.assertEqual(attachment.job, self.job)
        self.assertEqual(attachment.object, self.obj)


    def test_job_close_rejected(self):
        """
        Test closing a job after it is rejected.
        """
        self.job.approved = False
        self.job.close()
        self.job.refresh_from_db()
        self.assertEqual(self.job.status, "rejected")
        self.assertIsNone(self.job.closed_at)

    def test_job_comments(self):
        """
        Test adding comments to a job.
        """
        self.job.comments.append("This is a comment.")
        self.job.save()
        self.job.refresh_from_db()
        self.assertIn("This is a comment.", self.job.comments)

    def test_job_template_creation(self):
        """
        Test creating a job template.
        """
        template = JobTemplate.objects.create(
            name="NewTemplate", queue=self.queue, close_commands=["do_other {arg1}"], args={"arg1": "description"}
        )
        self.assertIsNotNone(template)
        self.assertEqual(template.name, "NewTemplate")
        self.assertEqual(template.queue, self.queue)

    def test_job_with_due_date(self):
        """
        Test creating a job with a due date.
        """
        due_date = timezone.now() + timedelta(days=7)
        job_with_due = Job.objects.create(
            title="Due Job", description="Job with due date", requester=self.requester, queue=self.queue, due_date=due_date
        )
        self.assertIsNotNone(job_with_due)
        self.assertEqual(job_with_due.due_date, due_date)

    def test_queue_creation(self):
        """
        Test creating a queue.
        """
        new_queue = Queue.objects.create(name="NewQueue")
        self.assertIsNotNone(new_queue)
        self.assertEqual(new_queue.name, "NewQueue")


if __name__ == '__main__':
    unittest.main()
