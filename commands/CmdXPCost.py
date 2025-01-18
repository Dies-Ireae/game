from evennia import default_cmds
from evennia.utils.evtable import EvTable
from decimal import Decimal

class CmdXPCost(default_cmds.MuxCommand):
    """
    View costs for character advancement.
    
    Usage:
      +costs              - Show all available purchases
      +costs/attributes   - Show attribute costs
      +costs/abilities    - Show ability costs
      +costs/backgrounds  - Show background costs
      +costs/powers      - Show power/gift costs
      +costs/pools       - Show pool costs
    """
    
    key = "+costs"
    aliases = ["costs"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        """Execute command"""
        if not self.switches:
            # Show overview of all categories
            self._display_all_costs(self.caller)
            return
            
        switch = self.switches[0].lower()
        if switch in ["attributes", "abilities", "backgrounds", "powers", "pools"]:
            self._display_category_costs(self.caller, switch)
        else:
            self.caller.msg("Invalid switch. Use +help costs for usage information.")

    def _display_category_costs(self, character, category):
        """Display costs for a specific category"""
        current_xp = character.db.xp.get('current', 0) if character.db.xp else 0
        total_width = 78
        
        # Create section header
        title = f" {category.title()} Costs "
        title_len = len(title)
        dash_count = (total_width - title_len) // 2
        header = f"|b{'-' * dash_count}|y{title}|n|b{'-' * (total_width - dash_count - title_len)}|n\n"
        
        # Create table with blue borders
        table = EvTable(
            "|wPurchase|n",
            "|wCurrent|n",
            "|wNext|n",
            "|wCost|n",
            "|wAffordable|n",
            border="table",
            width=total_width
        )
        
        # Add blue color to the table border
        table.border_left = "|b||n"
        table.border_right = "|b||n"
        table.border_top = "|b-|n"
        table.border_bottom = "|b-|n"
        table.corner_top_left = "|b+|n"
        table.corner_top_right = "|b+|n"
        table.corner_bottom_left = "|b+|n"
        table.corner_bottom_right = "|b+|n"

        if category == "attributes":
            # Add section headers for each subcategory
            subcategories = [
                ('physical', ['Strength', 'Dexterity', 'Stamina']),
                ('social', ['Charisma', 'Manipulation', 'Appearance']),
                ('mental', ['Perception', 'Intelligence', 'Wits'])
            ]
            
            for subcat, stats in subcategories:
                # Add subcategory header with divider
                table.add_row(f"|y{subcat.title()} Attributes:|n", "", "", "", "")
                for stat in stats:
                    current = int(character.get_stat('attributes', subcat, stat) or 0)
                    if current < 5:  # Max rating of 5
                        next_rating = current + 1
                        try:
                            cost, requires_approval = character.calculate_xp_cost(
                                stat, 
                                next_rating, 
                                category='attributes',
                                subcategory=subcat,
                                current_rating=current
                            )
                            table.add_row(
                                f"  {stat}",
                                str(current),
                                str(next_rating),
                                str(cost),
                                "Yes" if cost <= current_xp and not requires_approval else "No"
                            )
                        except Exception as e:
                            character.msg(f"Error calculating cost for {stat}: {str(e)}")
                            continue

        elif category == "abilities":
            subcategories = [
                ('talent', ['Alertness', 'Athletics', 'Awareness', 'Brawl', 'Empathy',
                           'Expression', 'Intimidation', 'Leadership', 'Streetwise', 'Subterfuge']),
                ('skill', ['Animal Ken', 'Crafts', 'Drive', 'Etiquette', 'Firearms',
                          'Larceny', 'Melee', 'Performance', 'Stealth', 'Survival']),
                ('knowledge', ['Academics', 'Computer', 'Finance', 'Investigation', 'Law',
                             'Medicine', 'Occult', 'Politics', 'Science', 'Technology'])
            ]
            
            for subcat, stats in subcategories:
                table.add_row(f"|y{subcat.title()} Abilities:|n", "", "", "", "")
                for stat in stats:
                    current = int(character.get_stat('abilities', subcat, stat) or 0)
                    if current < 5:
                        next_rating = current + 1
                        try:
                            cost, requires_approval = character.calculate_xp_cost(
                                stat, 
                                next_rating, 
                                category='abilities',
                                subcategory=subcat,
                                current_rating=current
                            )
                            table.add_row(
                                f"  {stat}",
                                str(current),
                                str(next_rating),
                                str(cost),
                                "Yes" if cost <= current_xp and not requires_approval else "No"
                            )
                        except Exception as e:
                            character.msg(f"Error calculating cost for {stat}: {str(e)}")
                            continue

        elif category == "backgrounds":
            backgrounds = ['Resources', 'Contacts', 'Allies', 'Backup', 'Herd', 'Library',
                          'Kinfolk', 'Spirit Heritage', 'Ancestors']
            
            table.add_row("|yBackgrounds:|n", "", "", "", "")
            for stat in backgrounds:
                current = int(character.get_stat('backgrounds', 'background', stat) or 0)
                if current < 5:
                    next_rating = current + 1
                    try:
                        cost, requires_approval = character.calculate_xp_cost(
                            stat, 
                            next_rating, 
                            category='backgrounds',
                            subcategory='background',
                            current_rating=current
                        )
                        table.add_row(
                            f"  {stat}",
                            str(current),
                            str(next_rating),
                            str(cost),
                            "Yes" if cost <= current_xp and not requires_approval else "No"
                        )
                    except Exception as e:
                        character.msg(f"Error calculating cost for {stat}: {str(e)}")
                        continue

        elif category == "powers":
            # Add your game's specific powers/gifts here
            powers = ['Spirit Speech', 'Master of Fire', 'Sense Wyrm', 'Create Element',
                     'Primal Anger', 'Scent of Running Water', 'Scent of the True Form']
            
            table.add_row("|yPowers:|n", "", "", "", "")
            for stat in powers:
                current = int(character.get_stat('powers', 'gift', stat) or 0)
                if current < 5:
                    next_rating = current + 1
                    try:
                        cost, requires_approval = character.calculate_xp_cost(
                            stat, 
                            next_rating, 
                            category='powers',
                            subcategory='gift',
                            current_rating=current
                        )
                        table.add_row(
                            f"  {stat}",
                            str(current),
                            str(next_rating),
                            str(cost),
                            "Yes" if cost <= current_xp and not requires_approval else "No"
                        )
                    except Exception as e:
                        character.msg(f"Error calculating cost for {stat}: {str(e)}")
                        continue

        elif category == "pools":
            pools = ['Willpower', 'Rage', 'Gnosis']
            
            table.add_row("|yPools:|n", "", "", "", "")
            for stat in pools:
                current = int(character.get_stat('pools', 'dual', stat) or 0)
                if current < 10:  # Pools usually go to 10
                    next_rating = current + 1
                    try:
                        cost, requires_approval = character.calculate_xp_cost(
                            stat, 
                            next_rating, 
                            category='pools',
                            subcategory='dual',
                            current_rating=current
                        )
                        table.add_row(
                            f"  {stat}",
                            str(current),
                            str(next_rating),
                            str(cost),
                            "Yes" if cost <= current_xp and not requires_approval else "No"
                        )
                    except Exception as e:
                        character.msg(f"Error calculating cost for {stat}: {str(e)}")
                        continue

        # Send the formatted output with header and footer
        footer = f"|b{'-' * total_width}|n"
        character.msg(f"{header}{table}\n{footer}")

    def _display_all_costs(self, character):
        """Display an overview of all categories"""
        total_width = 78
        title = " Available Character Advancement Options "
        title_len = len(title)
        dash_count = (total_width - title_len) // 2
        
        header = f"|b{'-' * dash_count}|y{title}|n|b{'-' * (total_width - dash_count - title_len)}|n\n"
        
        # Create centered category list
        msg = header
        msg += "|yCategories:|n\n"
        msg += "  |w+costs/attributes|n  - Physical, Social, and Mental Attributes\n"
        msg += "  |w+costs/abilities|n   - Talents, Skills, and Knowledges\n"
        msg += "  |w+costs/backgrounds|n - Character Backgrounds\n"
        msg += "  |w+costs/powers|n      - Gifts and Other Powers\n"
        msg += "  |w+costs/pools|n       - Rage, Gnosis, and Willpower\n"
        msg += "\n|yUsage:|n\n"
        msg += "  Use the switches above to view detailed costs for each category.\n"
        msg += f"|b{'-' * total_width}|n"
        
        character.msg(msg) 