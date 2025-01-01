"""
Page command - allows paging by both account and character name
"""
from evennia.commands.default.comms import CmdPage as DefaultCmdPage
from evennia import search_object, search_account
from evennia.utils import create
from evennia.utils.utils import make_iter
from evennia.comms.models import Msg

class CmdPage(DefaultCmdPage):
    """
    send a private message to another account

    Usage:
      page[/switches] [<account/character>,<account/character>,... = <message>]
      tell        ''
      page <number>

    Switch:
      last - shows who you last messaged
      list - show your last <number> of tells/pages (default)

    Send a message to target user (if online). If no
    argument is given, you will get a list of your latest messages.
    You can page either by account name or by character name.
    """
    key = "page"
    aliases = ["tell", "p"]

    def func(self):
        """Implement function using the parent"""
        caller = self.caller

        # Get the messages we've sent (not to channels)
        pages_we_sent = Msg.objects.get_messages_by_sender(caller).exclude(
            db_receivers_accounts__in=[caller]).order_by("-db_date_created")

        if "last" in self.switches:
            if pages_we_sent:
                recv = ",".join(obj.key for obj in pages_we_sent[0].receivers)
                self.msg(f"You last paged |c{recv}|n:{pages_we_sent[0].message}")
                return
            else:
                self.msg("You haven't paged anyone yet.")
                return

        # We are sending a new message
        if self.args:
            if self.rhs:
                # Format is: page person=message
                # Split recipients by spaces, not commas
                recipients = [r.strip() for r in self.lhs.split()]
                message = self.rhs
            else:
                # No = sign, could be either a number for history or just a message
                if self.args.isdigit():
                    # Show message history
                    number = int(self.args)
                    pages = pages_we_sent[:number]
                    if pages:
                        msg = "\n".join(
                            "|w%s|n |c%s|n: %s"
                            % (
                                msg.date_created.strftime("%Y-%m-%d %H:%M:%S"),
                                ",".join(obj.key for obj in msg.receivers),
                                msg.message,
                            )
                            for msg in pages
                        )
                        self.msg("Your last %i pages:\n%s" % (len(pages), msg))
                    else:
                        self.msg("You haven't paged anyone yet.")
                    return
                else:
                    # No = sign, just a message - send to last person paged
                    if pages_we_sent:
                        recipients = [obj.key for obj in pages_we_sent[0].receivers]
                        message = self.args
                    else:
                        self.msg("You haven't paged anyone yet.")
                        return
        else:
            # No args - show last messages
            number = 20
            pages = pages_we_sent[:number]
            if pages:
                msg = "\n".join(
                    "|w%s|n |c%s|n: %s"
                    % (
                        msg.date_created.strftime("%Y-%m-%d %H:%M:%S"),
                        ",".join(obj.key for obj in msg.receivers),
                        msg.message,
                    )
                    for msg in pages
                )
                self.msg("Your last %i pages:\n%s" % (len(pages), msg))
            else:
                self.msg("You haven't paged anyone yet.")
            return

        # Process the recipients
        account_recipients = []
        offline_recipients = []
        failed_recipients = []
        
        for recipient in recipients:
            # First try character search
            chars = search_object(recipient, exact=True)
            if chars:
                char = chars[0]
                if hasattr(char, 'account') and char.account:
                    if char.account.sessions.count():  # Check if they're online
                        account_recipients.append(char.account)
                    else:
                        offline_recipients.append(char.key)
                    continue

            # Then try account search
            accounts = search_account(recipient)
            if accounts:
                account = accounts[0]
                if account.sessions.count():  # Check if they're online
                    account_recipients.append(account)
                else:
                    offline_recipients.append(account.key)
                continue
            
            # If we get here, we couldn't find the recipient at all
            failed_recipients.append(recipient)

        if not account_recipients and (offline_recipients or failed_recipients):
            # No valid online recipients found
            if failed_recipients:
                self.msg(f"Could not find: {', '.join(failed_recipients)}")
            if offline_recipients:
                self.msg(f"Currently offline: {', '.join(offline_recipients)}")
            return

        # Create the message
        # Get caller's character name if available
        caller_name = caller.puppet.key if caller.puppet else caller.key
        
        # Tell the accounts they got a message
        received = []
        for target in account_recipients:
            if not target.access(caller, "msg"):
                self.msg(f"You are not allowed to page {target}.")
                continue
            
            # Get the character name if available, otherwise use account name
            char_name = target.puppet.key if target.puppet else target.key
            
            # Create list of recipient names including the current target
            other_recipients = [
                t.puppet.key if t.puppet else t.key 
                for t in account_recipients
                if t != target  # Exclude current target from list
            ]
            
            # Get current target's name
            target_name = target.puppet.key if target.puppet else target.key
            
            # Format the header to show all recipients
            if other_recipients:
                # Add current target to the beginning of the list
                all_recipients = [target_name] + other_recipients
                if len(all_recipients) > 1:
                    # Join all but last name with commas, then add "and" before last name
                    others = f"{', '.join(all_recipients[:-1])} and {all_recipients[-1]}"
                else:
                    others = all_recipients[0]
                header = f"(To: {others}) From afar,"
            else:
                header = "From afar,"
            
            # Handle emotes (messages starting with :)
            if message.startswith(":"):
                formatted_message = f"{caller_name} {message[1:].strip()}"
            else:
                formatted_message = f"{caller_name} pages: {message}"
                
            target.msg(f"|w{header}|n {formatted_message}")
            received.append(f"|c{char_name}|n")

        # Format the confirmation message
        if received:
            if len(received) == 1:
                # Single recipient format
                if message.startswith(":"):
                    self.msg(f"Long distance to {received[0]}: {caller_name} {message[1:].strip()}")
                else:
                    self.msg(f"You paged {received[0]} with: '{message}'")
            else:
                # Multiple recipients format
                if message.startswith(":"):
                    self.msg(f"To ({', '.join(received)}): {caller_name} {message[1:].strip()}")
                else:
                    self.msg(f"To ({', '.join(received)}) you paged: '{message}'")
            
        # Report any offline users
        if offline_recipients:
            self.msg(f"Currently offline: {', '.join(offline_recipients)}")
        
        # Report any not-found users
        if failed_recipients:
            self.msg(f"Could not find: {', '.join(failed_recipients)}")

        # Create persistent message object for history
        if account_recipients:
            # Create the persistent message
            target_perms = " or ".join([f"id({target.id})" for target in account_recipients + [caller]])
            create.create_message(
                caller,
                message,
                receivers=account_recipients,
                locks=(
                    f"read:{target_perms} or perm(Admin);"
                    f"delete:id({caller.id}) or perm(Admin);"
                    f"edit:id({caller.id}) or perm(Admin)"
                ),
                tags=[("page", "comms")],
            )