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
            
        # Send to all connected accounts except sender
        for account in self.subscriptions.all():
            if not senders or account not in senders:
                account.msg(formatted_msg)
            
        # Send to sender separately to avoid double messaging
        if senders:
            for sender in senders:
                if sender in self.subscriptions.all():
                    sender.msg(formatted_msg)
