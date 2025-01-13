from evennia.commands.default.muxcommand import MuxCommand
from world.wod20th.models import Stat, STAT_TYPES, SHIFTER_IDENTITY_STATS, SHIFTER_RENOWN, CLAN, MAGE_FACTION, MAGE_SPHERES, \
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
      +info/type <stat_type>
      +info/shifter <shifter_type>

    Switches:
      /search   - Search all abilities for a keyword
      /type     - Show all entries of a specific type (gift, discipline, etc)
      /<splat>  - View only entries matching specified splat
      /shifter  - View gifts for a specific shifter type (garou, ananasi, etc)

    Examples:
      +info/fera merits  - View merits belonging only to fera
      +info merits       - View all merits across all splats
      +info/type gift    - View all gifts
      +info/shifter ananasi - View all Ananasi gifts
    """
    key = "info"
    aliases = []
    help_category = "Chargen & Character Info"
    
    # Group similar stat types together
    DISPLAY_CATEGORIES = {
        'Attributes': ['physical', 'social', 'mental'],
        'Abilities': ['skill', 'knowledge', 'talent', 'ability'],
        'Secondary Abilities': ['secondary_knowledge', 'secondary_talent', 'secondary_skill', 'secondary_ability'],
        'Powers': ['discipline', 'gift', 'art', 'sphere', 'bygone_power'],
        'Advantages': ['advantage', 'background'],
        'Supernatural': ['lineage', 'enlightenment', 'path'],
        'Merits & Flaws': ['merit', 'flaw'],
        'Identity': ['splat', 'kith', 'seeming', 'house'],
        'Other': ['other', 'specialty', 'trait']
    }
    
    ignore_categories = {'other', 'specialty'}  # Categories to ignore in searches

    def func(self):
        if not self.args and not self.switches:
            # Display all possible categories
            return self.list_categories()
            
        if 'search' in self.switches:
            if not self.args:
                return self.caller.msg("Include something to search for!")
            return self.search_all(self.args.strip())
            
        if 'type' in self.switches:
            if not self.args:
                return self.caller.msg("Include a type to filter by!")
            return self.show_type(self.args.strip())
            
        if 'shifter' in self.switches:
            if not self.args:
                return self.caller.msg("Include a shifter type to filter by!")
            return self.show_shifter_gifts(self.args.strip())

        only_splat = ''
        valid_splats = {'changeling', 'fera', 'shifter', 'vampire', 'mage'}
        if any(value.lower() in valid_splats for value in self.switches):
            only_splat = next(value for value in self.switches if value.lower() in valid_splats)

        if (category := self.match_category(self.args.strip())):
            self.show_category(category, only_splat)
        elif (subject := self.match_subject(self.args.strip(), only_splat)):
            self.show_subject(subject)
        else:
            self.caller.msg(f"No matches found for '{self.args.strip()}'.")

    def format_header(self, text, width=78):
        return f"|r{'=' * 5}< |w{text}|r >{'=' * (width - len(text) - 9)}|n\n"

    def format_footer(self, width=78):
        return f"|r{'=' * width}|n\n"

    def match_category(self, input_str):
        """Match category and return tuple of (key, display_name)."""
        input_str_lower = input_str.lower()
        
        # Check display categories first
        for display_name, stat_types in self.DISPLAY_CATEGORIES.items():
            if input_str_lower == display_name.lower():
                return (stat_types, display_name)
            # Also check individual stat types within each category
            for stat_type in stat_types:
                if input_str_lower == stat_type.lower():
                    return ([stat_type], display_name)
        
        return None
    
    def match_subject(self, input_str, only_splat):
        results = Stat.objects.filter(name__iexact=input_str)
        if (only_splat != ''):
            results = results.filter(splat__iexact=only_splat)
        if not results:
            return None # Return None is no match is found
        return results[0]

    def list_categories(self):
        string = self.format_header("+Info Categories", width=78)
        
        # Get the display categories (excluding empty ones)
        categories = [cat for cat in self.DISPLAY_CATEGORIES.keys()]
        
        # Calculate rows needed (3 columns)
        rows = (len(categories) + 2) // 3
        
        # Pad the list for complete rows
        while len(categories) % 3 != 0:
            categories.append('')
            
        # Print in rows
        for row in range(rows):
            for col in range(3):
                idx = row * 3 + col
                if idx < len(categories):
                    title = categories[idx]
                    string += title.center(26)
            string += "\r\n"
            
        string += self.format_footer(width=78)
        self.caller.msg(string)
    
    def show_category(self, category, only_splat):
        stat_types, display_name = category
        string = self.format_header(f"+Info {display_name}", width=78)
        
        # Query for stats of the specified types
        results = Stat.objects.filter(stat_type__in=stat_types).order_by('name', 'splat')
        
        # Apply splat filter if specified
        if only_splat:
            results = results.filter(splat__iexact=only_splat)

        if not results.exists():
            string += "No results to show.\r\n"
        elif display_name == "Merits & Flaws":
            # Merit/flaw table formatting
            table = EvTable("|wName|n", "|wSplat|n", "|wShifter Type|n", "|wType|n", "|wValues|n", border="none")
            table.reformat_column(0, width=30, align="l")
            table.reformat_column(1, width=18, align="l")
            table.reformat_column(2, width=16, align="l")
            table.reformat_column(3, width=16, align="l")
            for result in results:
                formatted_values = "None" if not result.values else str(result.values[0]) if len(result.values) == 1 else ", ".join(map(str, result.values[:-1])) + f", or {result.values[-1]}"
                table.add_row(result.name, result.splat, result.stat_type, formatted_values)
            string += ANSIString(table)
        else:
            # Two-column format for other categories
            for i, result in enumerate(results):
                string += result.name.center(39)
                if i % 2 == 1:
                    string += "\r\n"
            if len(results) % 2:  # Add final newline if odd number of results
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
        # Add shifter_type for gifts
        if subject.stat_type == 'gift' and subject.shifter_type:
            string += f"  |wShifter Type:|n {subject.shifter_type.title()}\r\n"
        string += "\r\n"
        string += subject.description + "\r\n"
        string += self.format_footer(width=78)
        self.caller.msg(string)
    
    def search_all(self, input_str):
        # Get all valid stat types from our DISPLAY_CATEGORIES
        valid_stat_types = []
        for stat_types in self.DISPLAY_CATEGORIES.values():
            valid_stat_types.extend(stat_types)
        
        # Remove ignored categories
        valid_stat_types = [st for st in valid_stat_types if st not in self.ignore_categories]
        
        # Perform a case-insensitive search by name
        matches = Stat.objects.filter(
            name__icontains=input_str,
            stat_type__in=valid_stat_types
        )
        
        if not matches.exists():
            # If no name matches, search by description
            matches = Stat.objects.filter(
                description__icontains=input_str,
                stat_type__in=valid_stat_types
            )
            if not matches.exists():
                return self.caller.msg(f"No matches found containing the text '{input_str}'.")
        
        if len(matches) == 1:
            return self.show_subject(matches[0])
            
        string = self.format_header(f"+Info Search: {input_str}", width=78)
        table = EvTable("|wName|n", "|wSplat|n", "|wShifter Type|n", "|wType|n", border="none")
        table.reformat_column(0, width=30, align="l")
        table.reformat_column(1, width=22, align="l")
        table.reformat_column(2, width=16, align="l")
        table.reformat_column(3, width=16, align="l")
        
        for result in matches[:10]:
            table.add_row(result.name, result.splat, result.shifter_type, result.stat_type)
            
        string += ANSIString(table)
        matches_string = f"\r\n    There were |w{len(matches)}|n matches"
        if len(matches) > 10:
            matches_string += ", and some were truncated."
        string += matches_string + "\r\n"
        string += self.format_footer(width=78)
        self.caller.msg(string)
                    
    def show_type(self, type_name):
        """Show all entries of a specific stat type."""
        # Get all valid stat types from our DISPLAY_CATEGORIES
        valid_stat_types = []
        for stat_types in self.DISPLAY_CATEGORIES.values():
            valid_stat_types.extend(stat_types)
        
        # Try to match the input to a valid stat type
        type_name_lower = type_name.lower()
        matched_type = None
        
        # First try exact match
        for stat_type in valid_stat_types:
            if stat_type.lower() == type_name_lower:
                matched_type = stat_type
                break
        
        # If no exact match, try partial match
        if not matched_type:
            for stat_type in valid_stat_types:
                if type_name_lower in stat_type.lower().replace('_', ' '):
                    matched_type = stat_type
                    break
        
        if not matched_type:
            return self.caller.msg(f"No stat type found matching '{type_name}'.")
        
        # Get all matches for the type
        results = Stat.objects.filter(stat_type__iexact=matched_type).order_by('name')
        
        if not results.exists():
            return self.caller.msg(f"No entries found for type '{matched_type}'.")
        
        string = self.format_header(f"+Info Type: {matched_type.title()}", width=78)
        
        # Use table format for better organization
        if matched_type == 'gift':
            table = EvTable("|wName|n", "|wSplat|n", "|wShifter Type|n", "|wValues|n", border="none")
            table.reformat_column(0, width=30, align="l")
            table.reformat_column(1, width=15, align="l")
            table.reformat_column(2, width=15, align="l")
            table.reformat_column(3, width=10, align="l")
        else:
            table = EvTable("|wName|n", "|wSplat|n", "|wValues|n", border="none")
            table.reformat_column(0, width=30, align="l")
            table.reformat_column(1, width=20, align="l")
            table.reformat_column(2, width=20, align="l")
        
        for result in results:
            formatted_values = "None" if not result.values else str(result.values[0]) if len(result.values) == 1 else ", ".join(map(str, result.values[:-1])) + f", or {result.values[-1]}"
            if matched_type == 'gift':
                table.add_row(
                    result.name, 
                    result.splat or "Any", 
                    result.shifter_type.title() if result.shifter_type else "None",
                    formatted_values
                )
            else:
                table.add_row(result.name, result.splat or "Any", formatted_values)
            
        string += ANSIString(table)
        string += f"\r\n    There were |w{len(results)}|n entries of type '{matched_type}'.\r\n"
        string += self.format_footer(width=78)
        self.caller.msg(string)
                    
    def show_shifter_gifts(self, shifter_type):
        """Show all gifts for a specific shifter type."""
        # Get all gifts for the specified shifter type
        results = Stat.objects.filter(
            stat_type='gift',
            shifter_type__iexact=shifter_type
        ).order_by('name')
        
        if not results.exists():
            return self.caller.msg(f"No gifts found for shifter type '{shifter_type}'.")
        
        string = self.format_header(f"+Info {shifter_type.title()} Gifts", width=78)
        
        # Use table format for better organization
        table = EvTable("|wName|n", "|wValues|n", "|wDescription|n", border="none")
        table.reformat_column(0, width=25, align="l")
        table.reformat_column(1, width=10, align="l")
        table.reformat_column(2, width=43, align="l")
        
        for result in results:
            formatted_values = str(result.values[0]) if result.values else "N/A"
            # Truncate description if too long
            desc = result.description[:40] + "..." if len(result.description) > 40 else result.description
            table.add_row(result.name, formatted_values, desc)
            
        string += ANSIString(table)
        string += f"\r\n    Found |w{len(results)}|n gifts for {shifter_type.title()}.\r\n"
        string += self.format_footer(width=78)
        self.caller.msg(string)
                    
