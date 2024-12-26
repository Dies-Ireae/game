import unittest
from unittest.mock import MagicMock, patch
from evennia.utils.test_resources import EvenniaTest
from commands.CmdSelfStat import CmdSelfStat
from world.wod20th.models import Stat, CharacterSheet, calculate_willpower
from evennia.utils import create

class TestCmdSelfStat(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.character = create.create_object("typeclasses.characters.Character", key="TestChar", location=self.room1)
        self.character.db.stats = {}
        self.cmd = CmdSelfStat()
        self.cmd.caller = self.character

    def test_parse(self):
        self.cmd.args = "Strength/Physical=+1"
        self.cmd.parse()
        self.assertEqual(self.cmd.stat_name, "Strength")
        self.assertEqual(self.cmd.category, "Physical")
        self.assertEqual(self.cmd.value_change, "+1")

    def test_func_invalid_usage(self):
        self.cmd.args = ""
        self.cmd.func()
        expected = "|rUsage: +selfstat <stat>[(<instance>)]/[<category>]=[+-]<value>|n"
        self.assertEqual(self.character.msg.call_args[0][0], expected)

    @patch('commands.CmdSelfStat.Stat.objects.filter')
    def test_func_stat_not_found(self, mock_filter):
        mock_filter.return_value = []
        self.cmd.args = "NonexistentStat/Physical=+1"
        self.cmd.func()
        expected = "|rNo stats matching 'NonexistentStat' found in the database.|n"
        self.assertEqual(self.character.msg.call_args[0][0], expected)

    @patch('commands.CmdSelfStat.Stat.objects.filter')
    def test_func_update_stat(self, mock_filter):
        mock_stat = MagicMock()
        mock_stat.name = "Strength"
        mock_stat.category = "attributes"
        mock_stat.stat_type = "physical"
        mock_filter.return_value = [mock_stat]
        
        self.cmd.args = "Strength/Physical=3"
        self.cmd.func()
        expected = "|gUpdated Strength to 3.|n"
        self.assertEqual(self.character.msg.call_args[0][0], expected)
        self.assertEqual(self.character.db.stats['attributes']['physical']['Strength'], 3)

class TestStatModel(unittest.TestCase):
    def setUp(self):
        self.stat = Stat(
            name="Strength",
            description="Physical power",
            game_line="World of Darkness",
            category="attributes",
            stat_type="physical",
            values=[1, 2, 3, 4, 5],
            lock_string="view:all();edit:perm(Admin)"
        )

    def test_str_representation(self):
        self.assertEqual(str(self.stat), "Strength")

    def test_lock_storage(self):
        self.assertEqual(self.stat.lock_string, "view:all();edit:perm(Admin)")

    @patch('evennia.utils.create.create_object')
    def test_can_access(self, mock_create_object):
        mock_admin = MagicMock()
        mock_create_object.return_value = mock_admin
        
        self.assertTrue(self.stat.can_access(mock_admin, "view"))
        self.assertFalse(self.stat.can_access(mock_admin, "edit"))

class TestCharacterSheet(unittest.TestCase):
    @patch('evennia.utils.create.create_account')
    @patch('evennia.utils.create.create_object')
    def setUp(self, mock_create_object, mock_create_account):
        self.account = mock_create_account.return_value
        self.character = mock_create_object.return_value
        self.sheet = CharacterSheet(account=self.account, character=self.character)

    def test_character_sheet_creation(self):
        self.assertIsNotNone(self.sheet)
        self.assertEqual(self.sheet.account, self.account)
        self.assertEqual(self.sheet.character, self.character)

class TestCalculateWillpower(EvenniaTest):
    def setUp(self):
        super().setUp()
        self.character = create.create_object("typeclasses.characters.Character", key="TestChar", location=self.room1)
        self.character.db.stats = {'virtues': {'moral': {}}}

    def test_calculate_willpower_with_courage(self):
        self.character.db.stats['virtues']['moral']['Courage'] = {'perm': 3}
        self.assertEqual(calculate_willpower(self.character), 3)

    def test_calculate_willpower_without_courage(self):
        self.character.db.stats['virtues']['moral'] = {
            'Self-Control': {'perm': 2},
            'Conscience': {'perm': 4}
        }
        self.assertEqual(calculate_willpower(self.character), 4)

if __name__ == '__main__':
    unittest.main()
