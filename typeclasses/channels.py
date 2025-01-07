"""
Channel

The channel class represents the out-of-character chat-room usable by
Accounts in-game. It is mostly overloaded to change its appearance, but
channels can be used to implement many different forms of message
distribution systems.

Note that sending data to channels are handled via the CMD_CHANNEL
syscommand (see evennia.syscmds). The sending should normally not need
to be modified.

"""

from evennia.comms.models import ChannelDB
from evennia.typeclasses.models import TypeclassBase


class Channel(ChannelDB, metaclass=TypeclassBase):
    """
    Custom channel class to handle message formatting and delivery.
    """
    
    @property
    def mutelist(self):
        """Get the list of accounts/objects muting this channel."""
        return self.db.muted or []

    def at_channel_creation(self):
        """Called when the channel is created."""
        self.db.muted = []
        
        # Ensure channel has a valid name
        if not self.key or not self.key.strip():
            raise ValueError("Channel must have a valid name")
    
    def mute(self, subscriber):
        """Add an account/object to the mute list."""
        if not self.db.muted:
            self.db.muted = []
        if subscriber not in self.db.muted:
            self.db.muted.append(subscriber)
    
    def unmute(self, subscriber):
        """Remove an account/object from the mute list."""
        if self.db.muted and subscriber in self.db.muted:
            self.db.muted.remove(subscriber)
    
    def msg(self, message, senders=None, **kwargs):
        """
        Send message to all connected accounts.
        
        Args:
            message (str): Message to send
            senders (Object, Account or list): Sender of message
            **kwargs: Extra parameters
        """
        # Format the message
        if senders:
            if not isinstance(senders, (list, tuple)):
                senders = [senders]
            # Get the first sender (we typically only have one)
            sender = senders[0]
            
            # Handle poses/emits with white sender name and proper spacing
            if message.startswith(':') or message.startswith(';'):
                formatted_msg = f"[{self.key}] |w{sender.name}|n {message[1:]}"
            elif message.startswith('|'):
                # Handle traditional MU* style poses
                formatted_msg = f"[{self.key}] |w{sender.name}|n {message}"
            else:
                formatted_msg = f"[{self.key}] |w{sender.name}|n: {message}"
        else:
            formatted_msg = f"[{self.key}] {message}"
            
        # Send to all connected accounts except sender and muted accounts
        for account in self.subscriptions.all():
            if account not in self.mutelist and (not senders or account not in senders):
                account.msg(formatted_msg)
            
        # Send to sender separately to avoid double messaging
        if senders:
            for sender in senders:
                if sender in self.subscriptions.all() and sender not in self.mutelist:
                    sender.msg(formatted_msg)

    def rename(self, new_name, rename_aliases=True):
        """
        Rename the channel.
        
        Args:
            new_name (str): New name for the channel
            rename_aliases (bool): If True, update user aliases to match new name
            
        Returns:
            bool: True if rename successful, False otherwise
        """
        old_name = self.key
        
        # Store current subscribers and their aliases
        subscribers = {}
        if rename_aliases:
            for account in self.subscriptions.all():
                aliases = account.nicks.get(category="channel", return_list=True) or []
                if aliases:
                    subscribers[account] = [alias for alias in aliases if alias.lower().endswith(old_name.lower())]
        
        try:
            # Update channel name
            self.key = new_name
            self.save()
            
            # Update subscriber aliases if requested
            if rename_aliases:
                for account, aliases in subscribers.items():
                    for old_alias in aliases:
                        # Create new alias with same prefix but new channel name
                        prefix = old_alias[:-(len(old_name))]
                        new_alias = prefix + new_name
                        account.nicks.add(new_alias, old_name, category="channel")
                        
            # Announce the change
            self.msg(f"Channel {old_name} has been renamed to {new_name}.")
            return True
            
        except Exception as e:
            self.msg(f"Error renaming channel: {e}")
            return False
