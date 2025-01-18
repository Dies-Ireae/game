"""
Custom channel command for Dies Irae.
"""
from evennia.commands.default.comms import CmdChannel
from evennia.utils.ansi import strip_ansi
from evennia.comms.models import ChannelDB
from evennia.utils.evtable import EvTable

class CustomCmdChannel(CmdChannel):
    """
    Custom channel command that doesn't check permissions during search.
    """
    
    channel_class = ChannelDB
    
    def add_channel_alias(self, caller, channel, alias):
        """Helper method to add a channel alias."""
        # Add the alias mapping for recognition
        caller.nicks.add(alias, channel.key, category="channel")
        # Add the command substitution for sending messages
        caller.nicks.add(alias, f"channel {channel.key}", category="inputcmd")
    
    def remove_channel_aliases(self, caller, channel):
        """Helper method to remove all aliases for a channel."""
        nicks = caller.nicks.get(category="channel")
        if nicks:
            for nick in nicks:
                try:
                    if nick[2] == channel.key:  # nick[2] is the db_value
                        alias = nick[0]  # nick[0] is the db_key
                        caller.nicks.remove(alias, category="channel")
                        caller.nicks.remove(alias, category="inputcmd")
                except (IndexError, TypeError):
                    continue
    
    def list_channels(self, all_channels=False):
        """
        List channels available to the caller.
        
        Args:
            all_channels (bool): Show all channels or just subscribed ones.
        """
        caller = self.caller
        channels = self.channel_class.objects.all()
        
        if not all_channels:
            # Only show subscribed channels
            channels = [chan for chan in channels if chan.subscriptions.has(caller)]
            if not channels:
                self.msg("You are not subscribed to any channels. Use channel/all to see all available channels.")
                return
        
        table = EvTable(
            "|wSub|n",
            "|wChannel|n",
            "|wAliases|n",
            "|wMy Aliases|n",
            "|wDescription|n",
            border="header"
        )
        
        for chan in channels:
            subscribed = "Yes" if chan.subscriptions.has(caller) else "No"
            aliases = [alias.strip() for alias in chan.aliases.all()]
            alias_str = ",".join(aliases) if aliases else ""
            
            # Get personal aliases for this channel
            my_aliases = []
            nicks = caller.nicks.get(category="channel")
            if nicks:
                for nick in nicks:
                    try:
                        if nick[2] == chan.key:  # nick[2] is the db_value
                            my_aliases.append(nick[0])  # nick[0] is the db_key
                    except (IndexError, TypeError):
                        continue
            my_alias_str = ", ".join(my_aliases) if my_aliases else ""
            
            desc = chan.db.desc or ""
            table.add_row(subscribed, chan.key, alias_str, my_alias_str, desc)
        
        self.msg(str(table))
    
    def has_subscription(self, channel):
        """Helper method to check if caller is subscribed to a channel."""
        return channel.subscriptions.has(self.caller)
    
    def sub_to_channel(self, channel):
        """
        Subscribe to a channel with custom permission handling.
        
        Args:
            channel (Channel): The channel to subscribe to.
            
        Returns:
            bool: True if subscription was successful, False otherwise.
        """
        caller = self.caller
        
        # Check if already subscribed
        if self.has_subscription(channel):
            self.msg(f"You are already subscribed to channel {channel.key}.")
            return False
            
        # Check if banned
        if caller in channel.banlist:
            self.msg(f"You are banned from {channel.key}.")
            return False
            
        # Try to subscribe
        try:
            # Add to subscriptions directly
            channel.subscriptions.add(caller)
            
            # Then add the default alias
            alias = channel.key[:3].lower()
            self.add_channel_alias(caller, channel, alias)
            
            self.msg(f"You are now subscribed to channel {channel.key}. "
                    f"Default alias '{alias}' was set. Use /alias to add additional aliases.")
            return True
        except Exception as err:
            self.msg(f"Could not subscribe to {channel.key}: {err}")
            # Clean up any partial subscription
            if self.has_subscription(channel):
                channel.subscriptions.remove(caller)
            return False
    
    def search_channel(self, channelname, exact=False, handle_errors=True):
        """
        Search for a channel without checking permissions.
        
        Args:
            channelname (str): Name to search for.
            exact (bool, optional): Require exact name match.
            handle_errors (bool, optional): Show error messages.
            
        Returns:
            list: List of matching channels.
        """
        channelname = channelname.strip()
        
        # Debug output
        self.msg(f"Searching for channel: '{channelname}'")
        
        # First try exact match
        channels = list(self.channel_class.objects.filter(db_key__iexact=channelname))
        if channels:
            self.msg(f"Found exact match: {channels[0].key}")
            return channels
            
        if not exact:
            # Try inexact match
            channels = list(self.channel_class.objects.filter(db_key__icontains=channelname))
            if channels:
                self.msg(f"Found partial match: {channels[0].key}")
                return channels
            
        # Try aliases
        channels = list(self.channel_class.objects.filter(
            db_tags__db_key__iexact=channelname,
            db_tags__db_tagtype__iexact="alias"
        ))
        if channels:
            self.msg(f"Found by alias: {channels[0].key}")
            return channels
            
        if handle_errors:
            self.msg(f"No channel found matching '{channelname}'.")
        return []
    
    def func(self):
        """
        Handle the channel command with custom permission handling.
        """
        caller = self.caller
        args = self.args.strip()

        if not args:
            # No args - show channels you are subscribed to
            self.list_channels()
            return

        if args.startswith('/'):
            # Command prefixed with /
            arg_list = args[1:].split()
            if not arg_list:
                # Empty command
                self.msg("Usage: channel[/switches] [channel] = [message]")
                return
            option = arg_list[0].lower()
            rest = ' '.join(arg_list[1:])

            if option in ("list", "all"):
                # List all available channels
                self.list_channels(all_channels=True)
                return
            elif option == "who":
                # Show who is subscribed to a channel
                if not rest:
                    self.msg("Usage: channel/who <channel>")
                    return
                channels = self.search_channel(rest, exact=False)
                if not channels:
                    return
                channel = channels[0]
                who_list = self.channel_list_who(channel)
                if who_list:
                    self.msg(f"Subscribers on channel {channel.key}:")
                    self.msg("\n".join(f"  {subscriber}" for subscriber in who_list))
                else:
                    self.msg(f"No subscribers on channel {channel.key}.")
                return
            elif option == "alias":
                # Set an alias for a channel
                if not rest or "=" not in rest:
                    self.msg("Usage: channel/alias <channel>=<alias>")
                    return
                channel_name, alias = [part.strip() for part in rest.split("=", 1)]
                channels = self.search_channel(channel_name, exact=False)
                if not channels:
                    return
                channel = channels[0]
                if not self.has_subscription(channel):
                    self.msg(f"You are not subscribed to channel {channel.key}.")
                    return
                # Add the alias
                self.add_channel_alias(caller, channel, alias)
                self.msg(f"Channel alias set: {alias} now points to channel {channel.key}")
                return
            elif option == "sub":
                # Subscribe to a channel
                if not rest:
                    self.msg("Usage: channel/sub <channel>")
                    return
                channels = self.search_channel(rest, exact=False)
                if not channels:
                    return
                self.sub_to_channel(channels[0])
                return
            elif option == "unsub":
                # Unsubscribe from a channel
                if not rest:
                    self.msg("Usage: channel/unsub <channel>")
                    return
                channels = self.search_channel(rest, exact=False)
                if not channels:
                    return
                channel = channels[0]
                if not self.has_subscription(channel):
                    self.msg(f"You are not subscribed to channel {channel.key}.")
                    return
                # Remove any aliases for this channel
                self.remove_channel_aliases(caller, channel)
                # Remove subscription directly
                channel.subscriptions.remove(caller)
                self.msg(f"You un-subscribed from channel {channel.key}. All aliases were cleared.")
                return
            else:
                self.msg("Usage: channel[/switches] [channel] = [message]")
                return

        # No switch - sending a message or subscribing
        if "=" in args:
            # Sending a message
            channel_name, message = [part.strip() for part in args.split("=", 1)]
            channels = self.search_channel(channel_name, exact=False)
            if not channels:
                return
            channel = channels[0]
            if not self.has_subscription(channel):
                self.msg(f"You are not subscribed to channel {channel.key}.")
                return
            channel.msg(message, senders=caller)
        else:
            # Trying to subscribe
            channels = self.search_channel(args, exact=False)
            if not channels:
                return
            self.sub_to_channel(channels[0])