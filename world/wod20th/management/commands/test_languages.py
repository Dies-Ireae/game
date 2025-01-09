import os
import sys
import django
from django.test import TestCase
from django.conf import settings

# Set up Django settings
os.environ['DJANGO_SETTINGS_MODULE'] = 'server.conf.settings'
django.setup()

from evennia.utils.create import create_object
from typeclasses.characters import Character
from commands.CmdLanguage import CmdLanguage
from commands.CmdSelfStat import CmdSelfStat
from world.wod20th.models import Stat

class TestLanguages(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Set up data for the whole TestCase"""
        # Create test stats
        Stat.objects.create(
            name="Language",
            description="Languages known",
            game_line="Core",
            category="merits",
            stat_type="merit",
            values=[1, 2, 3, 4, 5],
            splat="Any"
        )
        
        Stat.objects.create(
            name="Natural Linguist",
            description="Natural aptitude for languages",
            game_line="Core",
            category="merits",
            stat_type="merit",
            values=[2],
            splat="Any"
        )

    def setUp(self):
        """Set up test fixture."""
        super().setUp()
        self.char1 = create_object(Character, key="TestChar")
        self.char1.db.stats = {
            'merits': {
                'social': {'Language': {'perm': 2, 'temp': 2}},
                'mental': {'Natural Linguist': {'perm': 2, 'temp': 2}}
            }
        }
        self.char1.db.languages = ['English', 'Spanish', 'French', 'Arabic', 'Farsi']
        self.char1.db.native_language = 'English'
        self.char1.db.currently_speaking = 'English'
        self.char1.db.approved = False  # Character in chargen

    def setup_cmd(self, cmd_class, args="", switches=None):
        """Helper method to set up commands properly."""
        cmd = cmd_class()
        cmd.caller = self.char1
        cmd.args = args
        cmd.switches = switches or []
        cmd.cmdstring = cmd.key
        cmd.raw_string = f"{cmd.key} {args}"
        cmd.parse()
        return cmd

    def test_basic_language_setup(self):
        """Test basic language functionality"""
        self.assertEqual(self.char1.get_languages(), ['English', 'Spanish', 'French', 'Arabic', 'Farsi'])
        self.assertEqual(self.char1.db.native_language, 'English')
        self.assertEqual(self.char1.db.currently_speaking, 'English')

    def test_language_merit_reduction(self):
        """Test reducing Language merit points"""
        cmd = self.setup_cmd(CmdSelfStat, "Language/Social=1")
        cmd.stat_name = "Language"  # Set required attributes
        cmd.stat_category = "Social"
        cmd.stat_value = "1"
        cmd.func()
        self.assertEqual(self.char1.get_languages(), ['English', 'Spanish', 'French'])

    def test_natural_linguist_removal(self):
        """Test removing Natural Linguist merit"""
        cmd = self.setup_cmd(CmdSelfStat, "Natural Linguist/Mental=")
        cmd.stat_name = "Natural Linguist"  # Set required attributes
        cmd.stat_category = "Mental"
        cmd.stat_value = ""
        cmd.func()
        self.assertEqual(self.char1.get_languages(), ['English', 'Spanish', 'French'])

    def test_native_language_change(self):
        """Test changing native language"""
        cmd = self.setup_cmd(CmdLanguage, "/native French", ["native"])
        cmd.func()
        self.assertEqual(self.char1.db.native_language, 'French')
        self.assertTrue('French' in self.char1.get_languages())
        self.assertTrue('English' in self.char1.get_languages())

    def test_adding_too_many_languages(self):
        """Test attempting to add more languages than points allow"""
        cmd = self.setup_cmd(CmdLanguage, "/add Swedish", ["add"])
        cmd.func()
        self.assertFalse('Swedish' in self.char1.get_languages())

    def test_removing_currently_speaking(self):
        """Test removing a language that is currently being spoken"""
        self.char1.db.currently_speaking = 'Arabic'
        cmd = self.setup_cmd(CmdSelfStat, "Language/Social=1")
        cmd.stat_name = "Language"  # Set required attributes
        cmd.stat_category = "Social"
        cmd.stat_value = "1"
        cmd.func()
        self.assertEqual(self.char1.db.currently_speaking, 'English')