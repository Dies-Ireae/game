from evennia.commands.default.muxcommand import MuxCommand
from world.wod20th.models import Stat, CATEGORIES, SHIFTER_IDENTITY_STATS, SHIFTER_RENOWN, CLAN, MAGE_FACTION, MAGE_SPHERES, \
    TRADITION, TRADITION_SUBFACTION, CONVENTION, METHODOLOGIES, NEPHANDI_FACTION, SEEMING, KITH, SEELIE_LEGACIES, \
    UNSEELIE_LEGACIES, ARTS, REALMS, calculate_willpower, calculate_road
from evennia.utils.ansi import ANSIString
from evennia.utils.evtable import EvTable

class CmdInfo(MuxCommand):
    """
    List and search chargen information.

    Usage:
      +info
      +info <topic>
      +info/search <keyword>

    Switches:
      /search   - Search all abilities for a keyword
      /<splat>  - View only entries matching specified splat

    Examples:
      +info/fera merits  - View merits belonging only to fera
      +info merits       - View all merits across all splats 
    """
    key = "info"
    aliases = []
    help_category = "Chargen & Character Info"
    ignore_categories = {"pools", "other", "legacy", "virtues", "identity"}

    def func(self):
        if not self.args and not self.switches:
            # Display all possible categories
            return self.list_categories()
        if ('search' in self.switches):
            # We doing a search!
            if not self.args:
                return self.caller.msg("Include something to search for!")
            return self.search_all(self.args.strip())
        only_splat = ''
        valid_splats = {'changeling', 'fera', 'shifter', 'vampire', 'mage'}
        if any(value.lower() in valid_splats for value in self.switches):
            only_splat = next(value for value in self.switches if value.lower() in valid_splats)

        if (category := self.match_category(self.args.strip())):
            self.show_category(category, only_splat)
        elif (subject := self.match_subject(self.args.strip(), only_splat)):
            self.show_subject(subject)
        else:
            skills = Stat.objects.filter(category="abilities", stat_type="skill")
            for i, skill in enumerate(skills):
                self.caller.msg(f"|r{skill.name}|n")

    def format_header(self, text, width=78):
        return f"|r{'=' * 5}< |w{text}|r >{'=' * (width - len(text) - 9)}|n\n"

    def format_footer(self, width=78):
        return f"|r{'=' * width}|n\n"

    def match_category(self, input_str):
        input_str_lower = input_str.lower()
        for key, display_name in CATEGORIES:
            if input_str_lower in (key.lower(), display_name.lower()):
                return key, display_name
        return None  # Return None if no match is found
    
    def match_subject(self, input_str, only_splat):
        results = Stat.objects.filter(name__iexact=input_str)
        if (only_splat != ''):
            results = results.filter(splat__iexact=only_splat)
        if not results:
            return None # Return None is no match is found
        return results[0]

    def list_categories(self):
        string = self.format_header("+Info Categories", width=78)
        i = 0
        for key, title in [category for category in CATEGORIES if category[0] not in self.ignore_categories]:
            i += 1
            string += title.center(26)
            if i % 3 == 0:
                string += "\r\n"
        string += self.format_footer(width=78)

        self.caller.msg(string)
    
    def show_category(self, category, only_splat):
        string = self.format_header(f"+Info {category[1]}", width=78)
        results = Stat.objects.filter(category=category[0]).order_by('name', 'splat')
        if (only_splat != ''):
            results = results.filter(splat__iexact=only_splat)

        if (len(results) <= 0):
            string += "No results to show.\r\n"
        elif (category[0] == "merits" or category[0] == "flaws"):
            table = EvTable("|wName|n", "|wSplat|n", "|wType|n", "|wValues|n", border="none")
            table.reformat_column(0, width=30, align="l")
            table.reformat_column(1, width=18, align="l")
            table.reformat_column(2, width=16, align="l")
            for result in results:
                formatted_values = "None" if not result.values else str(result.values[0]) if len(result.values) == 1 else ", ".join(map(str, result.values[:-1])) + f", or {result.values[-1]}"
                table.add_row(result.name, result.splat, result.stat_type, formatted_values)
            string += ANSIString(table)
        elif (category[0] == "backgrounds"):
            table = EvTable("|wName|n", "|wSplat|n", border="none")
            table.reformat_column(0, width=30, align="l")
            table.reformat_column(1, width=18, align="l")
            for result in results:
                table.add_row(result.name, result.splat, result.stat_type)
            string += ANSIString(table)
        else:
            for i, result in enumerate(results):
                string += result.name.center(39)
                if i % 2 == 0:
                    string += "\r\n"
        
        string += self.format_footer(width=78)
        self.caller.msg(string)

    def show_subject(self, subject):
        string = self.format_header(f"+Info {subject.name}", width=78)
        string += f"  |wName:|n {subject.name.ljust(38)}"
        if subject.values:
            formatted_values = "None" if not subject.values else str(subject.values[0]) if len(subject.values) == 1 else ", ".join(map(str, subject.values[:-1])) + f", or {subject.values[-1]}"
            string += f"|wValues:|n {formatted_values}"
        string += "\r\n"
        if subject.splat:
            string += f"  |wSplat:|n {subject.splat}\r\n"
        string += "\r\n"
        string += subject.description + "\r\n"
        string += self.format_footer(width=78)
        self.caller.msg(string)
    
    def search_all(self, input_str):
        # Perform a case-insensitive search by name (partial or full match)
        filtered_categories = [category for category in CATEGORIES if category[0] not in self.ignore_categories]
        filtered_categories = [category[0] for category in filtered_categories]
        matches = Stat.objects.filter(name__icontains=input_str, category__in=filtered_categories)
        
        if not matches.exists():
            # If no name matches, search by description
            matches = Stat.objects.filter(description__icontains=input_str, category__in=filtered_categories)
            if not matches.exists():
                return self.caller.msg(f"No matches found containing the text '{input_str}'.")
        if len(matches) == 1:
            return self.show_subject(matches[0])
        string = self.format_header(f"+Info Search: {input_str.ljust(-16)}", width=78)
        table = EvTable("|wName|n", "|wSplat|n", "|wCategory|n", "|wType|n", border="none")
        table.reformat_column(0, width=30, align="l")
        table.reformat_column(1, width=22, align="l")
        table.reformat_column(2, width=16, align="l")
        for result in matches[:10]:
            table.add_row(result.name, result.splat, result.category, result.stat_type)
        string += ANSIString(table)
        matches_string = f"\r\n    There were |w{len(matches)}|n matches"
        if (len(matches) > 10):
            matches_string += ", and some were truncated."
        string += matches_string.rjust(-78) + "\r\n"
        string += self.format_footer(width=78)
        self.caller.msg(string)
                    
