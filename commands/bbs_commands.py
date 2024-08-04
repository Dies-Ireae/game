# commands/bbs_commands.py

from evennia import default_cmds
from typeclasses.bbs_controller import BBSController

from evennia import default_cmds
from evennia import create_object
from typeclasses.bbs_controller import BBSController

class CmdCreateBoard(default_cmds.MuxCommand):
    """
    Create a new board.

    Usage:
      +bbs/create <name> = <description> / public | private
    """
    key = "+bbs/create"
    locks = "cmd:perm(Builder)"
    help_category = "BBS"

    def func(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: +bbs/create <name> = <description> / public | private")
            return
        name_desc, privacy = self.args.rsplit("/", 1)
        name, description = [arg.strip() for arg in name_desc.split("=", 1)]
        public = privacy.strip().lower() == "public"

        # Ensure BBSController exists
        try:
            controller = BBSController.objects.get(db_key="BBSController")
        except BBSController.DoesNotExist:
            controller = create_object(BBSController, key="BBSController")
            controller.db.boards = {}  # Initialize with an empty boards dictionary if needed
            self.caller.msg("BBSController created.")

        # Create the board
        controller.create_board(name, description, public)
        self.caller.msg(f"Board '{name}' created as {'public' if public else 'private'} with description: {description}")


class CmdPost(default_cmds.MuxCommand):
    """
    Post a message on a board.

    Usage:
      +bbs/post <board_name_or_number>/<title> = <content>
    """
    key = "+bbs/post"
    locks = "cmd:all()"
    help_category = "BBS"

    def func(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: +bbs/post <board_name_or_number>/<title> = <content>")
            return
        board_ref, post_data = [arg.strip() for arg in self.args.split("/", 1)]
        title, content = [arg.strip() for arg in post_data.split("=", 1)]

        controller = BBSController.objects.get(db_key="BBSController")
        if not controller:
            self.caller.msg("BBSController not found.")
            return

        try:
            board_ref = int(board_ref)  # Try converting to an integer
        except ValueError:
            pass

        board = controller.get_board(board_ref)
        if not board:
            self.caller.msg(f"No board found with the name or number '{board_ref}'.")
            return
        if board.get('locked', False):
            self.caller.msg(f"The board '{board['name']}' is locked. No new posts can be made.")
            return
        if not controller.has_write_access(board_ref, self.caller.key):
            self.caller.msg(f"You do not have write access to post on the board '{board['name']}'.")
            return
        controller.create_post(board_ref, title, content, self.caller.key)
        self.caller.msg(f"Post '{title}' added to board '{board['name']}'.")

class CmdReadBBS(default_cmds.MuxCommand):
    """
    List all boards or posts in a board, or read a specific post.

    Usage:
      +bbs
      +bbs <board_name_or_number>
      +bbs <board_number>/<post_number>
    """
    key = "+bbs"
    locks = "cmd:all()"
    help_category = "BBS"

    def func(self):
        controller = BBSController.objects.get(db_key="BBSController")
        if not controller:
            self.caller.msg("BBSController not found.")
            return

        if not self.args:
            self.list_boards(controller)
        else:
            arg = self.args.strip()
            if "/" in arg:
                # Handle reading a specific post: +bbs <board_id>/<post_id>
                board_ref, post_number = arg.split("/", 1)
                try:
                    board_ref = int(board_ref)
                    post_number = int(post_number)
                    self.read_post(controller, board_ref, post_number)
                except ValueError:
                    self.caller.msg("Usage: +bbs <board_id>/<post_id> where both are numbers.")
            else:
                # List posts in a board
                try:
                    board_ref = int(arg)
                except ValueError:
                    board_ref = arg

                self.list_posts(controller, board_ref)

    def list_boards(self, controller):
        """List all available boards."""
        boards = controller.db.boards
        if not boards:
            self.caller.msg("No boards available.")
            return

        # Table Header
        output = []
        output.append("=" * 78)
        output.append("{:<5} {:<10} {:<30} {:<20} {:<15}".format("ID", "Access", "Group Name", "Last Post", "# of messages"))
        output.append("-" * 78)

        for board_id, board in boards.items():
            access_type = "Private" if not board['public'] else "Public"
            read_only = "*" if controller.has_access(board_id, self.caller.key) and not controller.has_write_access(board_id, self.caller.key) else " "
            last_post = max((post['created_at'] for post in board['posts']), default="No posts")
            num_posts = len(board['posts'])
            output.append(f"{board_id:<5} {access_type:<10} {read_only} {board['name']:<30} {last_post:<20} {num_posts:<15}")

        # Table Footer
        output.append("-" * 78)
        output.append("* = read only")
        output.append("=" * 78)

        self.caller.msg("\n".join(output))

    def list_posts(self, controller, board_ref):
        """List all posts in the specified board."""
        board = controller.get_board(board_ref)
        if not board:
            self.caller.msg(f"No board found with the name or number '{board_ref}'.")
            return
        if not controller.has_access(board_ref, self.caller.key):
            self.caller.msg(f"You do not have access to view posts on the board '{board['name']}'.")
            return

        posts = board['posts']
        pinned_posts = [post for post in posts if post.get('pinned', False)]
        unpinned_posts = [post for post in posts if not post.get('pinned', False)]

        # Table Header
        output = []
        output.append("=" * 78)
        output.append(f"{'*' * 20} {board['name']} {'*' * 20}")
        output.append("{:<5} {:<40} {:<20} {:<15}".format("ID", "Message", "Posted", "By"))
        output.append("-" * 78)

        # List pinned posts first with correct IDs
        for i, post in enumerate(pinned_posts):
            post_id = posts.index(post) + 1
            output.append(f"{board['id']}/{post_id:<5} [Pinned] {post['title']:<40} {post['created_at']:<20} {post['author']}")

        # List unpinned posts with correct IDs
        for post in unpinned_posts:
            post_id = posts.index(post) + 1
            output.append(f"{board['id']}/{post_id:<5} {post['title']:<40} {post['created_at']:<20} {post['author']}")

        # Table Footer
        output.append("=" * 78)

        self.caller.msg("\n".join(output))

    def read_post(self, controller, board_ref, post_number):
        """Read a specific post in a board."""
        board = controller.get_board(board_ref)
        if not board:
            self.caller.msg(f"No board found with the name or number '{board_ref}'.")
            return
        if not controller.has_access(board_ref, self.caller.key):
            self.caller.msg(f"You do not have access to view posts on the board '{board['name']}'.")
            return
        posts = board['posts']
        if post_number < 1 or post_number > len(posts):
            self.caller.msg(f"Invalid post number. Board '{board['name']}' has {len(posts)} posts.")
            return
        post = posts[post_number - 1]
        edit_info = f"(edited on {post['edited_at']})" if post['edited_at'] else ""

        self.caller.msg(f"{'-'*40}")
        self.caller.msg(f"Title: {post['title']}")
        self.caller.msg(f"Author: {post['author']}")
        self.caller.msg(f"Date: {post['created_at']} {edit_info}")
        self.caller.msg(f"{'-'*40}")
        self.caller.msg(f"{post['content']}")
        self.caller.msg(f"{'-'*40}")







class CmdEditPost(default_cmds.MuxCommand):
    """
    Edit a post in a board.

    Usage:
      +bbs/editpost <board_name>/<post_number> = <new_content>
    """
    key = "+bbs/editpost"
    locks = "cmd:all()"
    help_category = "BBS"

    def func(self):
        if not self.args or "/" not in self.args:
            self.caller.msg("Usage: +bbs/editpost <board_name>/<post_number> = <new_content>")
            return
        board_name, post_data = [arg.strip() for arg in self.args.split("/", 1)]
        post_number, new_content = [arg.strip() for arg in post_data.split("=", 1)]

        controller = BBSController.objects.get(db_key="BBSController")
        if not controller:
            self.caller.msg("BBSController not found.")
            return

        board = controller.get_board(board_name)
        if not board:
            self.caller.msg(f"No board found with the name '{board_name}'.")
            return
        if board.get('locked', False):
            self.caller.msg(f"The board '{board_name}' is locked. No edits can be made.")
            return
        if not controller.has_write_access(board_name, self.caller.key):
            self.caller.msg(f"You do not have write access to edit posts on the board '{board_name}'.")
            return
        try:
            post_number = int(post_number)
        except ValueError:
            self.caller.msg("Post number must be an integer.")
            return
        posts = board['posts']
        if post_number < 1 or post_number > len(posts):
            self.caller.msg(f"Invalid post number. Board '{board_name}' has {len(posts)} posts.")
            return
        post = posts[post_number - 1]
        if not (self.caller.key == post['author'] or self.caller.is_superuser):
            self.caller.msg("You do not have permission to edit this post.")
            return

        controller.edit_post(board_name, post_number - 1, new_content)
        self.caller.msg(f"Post {post_number} in board '{board_name}' has been updated.")


class CmdDeletePost(default_cmds.MuxCommand):
    """
    Delete a post from a board.

    Usage:
      +bbs/deletepost <board_name>/<post_number>
    """
    key = "+bbs/deletepost"
    locks = "cmd:all()"
    help_category = "BBS"

    def func(self):
        if not self.args or "/" not in self.args:
            self.caller.msg("Usage: +bbs/deletepost <board_name>/<post_number>")
            return
        board_name, post_number = [arg.strip() for arg in self.args.split("/", 1)]

        controller = BBSController.objects.get(db_key="BBSController")
        if not controller:
            self.caller.msg("BBSController not found.")
            return

        board = controller.get_board(board_name)
        if not board:
            self.caller.msg(f"No board found with the name '{board_name}'.")
            return
        if not controller.has_access(board_name, self.caller.key):
            self.caller.msg(f"You do not have access to delete posts on the board '{board_name}'.")
            return
        try:
            post_number = int(post_number)
        except ValueError:
            self.caller.msg("Post number must be an integer.")
            return
        posts = board['posts']
        if post_number < 1 or post_number > len(posts):
            self.caller.msg(f"Invalid post number. Board '{board_name}' has {len(posts)} posts.")
            return
        post = posts[post_number - 1]
        if not (self.caller.key == post['author'] or self.caller.is_superuser):
            self.caller.msg("You do not have permission to delete this post.")
            return

        controller.delete_post(board_name, post_number - 1)
        self.caller.msg(f"Post {post_number} has been deleted from board '{board_name}'.")

class CmdDeleteBoard(default_cmds.MuxCommand):
    """
    Delete a board and all its posts.

    Usage:
      +bbs/deleteboard <board_name>
    """
    key = "+bbs/deleteboard"
    locks = "cmd:perm(Builder)"
    help_category = "BBS"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: +bbs/deleteboard <board_name>")
            return
        board_name = self.args.strip()

        controller = BBSController.objects.get(db_key="BBSController")
        if not controller:
            self.caller.msg("BBSController not found.")
            return

        board = controller.get_board(board_name)
        if not board:
            self.caller.msg(f"No board found with the name '{board_name}'.")
            return

        controller.delete_board(board_name)
        self.caller.msg(f"Board '{board_name}' and all its posts have been deleted.")

class CmdRevokeAccess(default_cmds.MuxCommand):
    """
    Revoke access to a private board.

    Usage:
      +bbs/revokeaccess <board_name> = <character_name>
    """
    key = "+bbs/revokeaccess"
    locks = "cmd:perm(Builder)"
    help_category = "BBS"

    def func(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: +bbs/revokeaccess <board_name> = <character_name>")
            return
        board_name, character_name = [arg.strip() for arg in self.args.split("=", 1)]

        controller = BBSController.objects.get(db_key="BBSController")
        if not controller:
            self.caller.msg("BBSController not found.")
            return

        board = controller.get_board(board_name)
        if not board:
            self.caller.msg(f"No board found with the name '{board_name}'.")
            return
        if board['public']:
            self.caller.msg(f"Board '{board_name}' is public; access control is not required.")
            return
        if character_name not in board['access_list']:
            self.caller.msg(f"{character_name} does not have access to board '{board_name}'.")
            return
        controller.revoke_access(board_name, character_name)
        self.caller.msg(f"Access for {character_name} has been revoked from board '{board_name}'.")

class CmdListAccess(default_cmds.MuxCommand):
    """
    List all users who have access to a private board.

    Usage:
      +bbs/listaccess <board_name>
    """
    key = "+bbs/listaccess"
    locks = "cmd:perm(Builder)"
    help_category = "BBS"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: +bbs/listaccess <board_name>")
            return
        board_name = self.args.strip()

        controller = BBSController.objects.get(db_key="BBSController")
        if not controller:
            self.caller.msg("BBSController not found.")
            return

        board = controller.get_board(board_name)
        if not board:
            self.caller.msg(f"No board found with the name '{board_name}'.")
            return
        if board['public']:
            self.caller.msg(f"Board '{board_name}' is public; access list is not applicable.")
            return
        access_list = board.get('access_list', [])
        if not access_list:
            self.caller.msg(f"No users have access to the private board '{board_name}'.")
        else:
            self.caller.msg(f"Users with access to '{board_name}': {', '.join(access_list)}")

class CmdLockBoard(default_cmds.MuxCommand):
    """
    Lock a board to prevent new posts.

    Usage:
      +bbs/lockboard <board_name>
    """
    key = "+bbs/lockboard"
    locks = "cmd:perm(Builder)"
    help_category = "BBS"

    def func(self):
        if not self.args:
            self.caller.msg("Usage: +bbs/lockboard <board_name>")
            return
        board_name = self.args.strip()

        controller = BBSController.objects.get(db_key="BBSController")
        if not controller:
            self.caller.msg("BBSController not found.")
            return

        board = controller.get_board(board_name)
        if not board:
            self.caller.msg(f"No board found with the name '{board_name}'.")
            return

        if board.get('locked', False):
            self.caller.msg(f"Board '{board_name}' is already locked.")
            return

        controller.lock_board(board_name)
        self.caller.msg(f"Board '{board_name}' has been locked. No new posts can be made.")

class CmdPinPost(default_cmds.MuxCommand):
    """
    Pin a post to the top of a board.

    Usage:
      +bbs/pinpost <board_name_or_number>/<post_number>
    """
    key = "+bbs/pinpost"
    locks = "cmd:perm(Builder)"
    help_category = "BBS"

    def func(self):
        if not self.args or "/" not in self.args:
            self.caller.msg("Usage: +bbs/pinpost <board_name_or_number>/<post_number>")
            return
        board_ref, post_number = [arg.strip() for arg in self.args.split("/", 1)]

        controller = BBSController.objects.get(db_key="BBSController")
        if not controller:
            self.caller.msg("BBSController not found.")
            return

        # Determine if board_ref is a name or a number
        try:
            board_ref = int(board_ref)
        except ValueError:
            pass

        board = controller.get_board(board_ref)
        if not board:
            self.caller.msg(f"No board found with the name or number '{board_ref}'.")
            return

        try:
            post_number = int(post_number)
        except ValueError:
            self.caller.msg("Post number must be an integer.")
            return
        posts = board['posts']
        if post_number < 1 or post_number > len(posts):
            self.caller.msg(f"Invalid post number. Board '{board['name']}' has {len(posts)} posts.")
            return

        controller.pin_post(board['id'], post_number - 1)
        self.caller.msg(f"Post {post_number} in board '{board['name']}' has been pinned to the top.")


class CmdUnpinPost(default_cmds.MuxCommand):
    """
    Unpin a pinned post from the top of a board.

    Usage:
      +bbs/unpinpost <board_name_or_number>/<post_number>
    """
    key = "+bbs/unpinpost"
    locks = "cmd:perm(Builder)"
    help_category = "BBS"

    def func(self):
        if not self.args or "/" not in self.args:
            self.caller.msg("Usage: +bbs/unpinpost <board_name_or_number>/<post_number>")
            return
        board_ref, post_number = [arg.strip() for arg in self.args.split("/", 1)]

        controller = BBSController.objects.get(db_key="BBSController")
        if not controller:
            self.caller.msg("BBSController not found.")
            return

        # Determine if board_ref is a name or a number
        try:
            board_ref = int(board_ref)
        except ValueError:
            pass

        board = controller.get_board(board_ref)
        if not board:
            self.caller.msg(f"No board found with the name or number '{board_ref}'.")
            return

        try:
            post_number = int(post_number)
        except ValueError:
            self.caller.msg("Post number must be an integer.")
            return
        posts = board['posts']
        if post_number < 1 or post_number > len(posts):
            self.caller.msg(f"Invalid post number. Board '{board['name']}' has {len(posts)} posts.")
            return

        controller.unpin_post(board['id'], post_number - 1)
        self.caller.msg(f"Post {post_number} in board '{board['name']}' has been unpinned.")


class CmdEditBoard(default_cmds.MuxCommand):
    """
    Edit the settings or description of a board.

    Usage:
      +bbs/editboard <board_name> = <field>, <new_value>

    Example:
      +bbs/editboard Announcements = description, A board for official announcements.
      +bbs/editboard Announcements = public, true
    """
    key = "+bbs/editboard"
    locks = "cmd:perm(Builder)"
    help_category = "BBS"

    def func(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: +bbs/editboard <board_name> = <field>, <new_value>")
            return
        board_name, updates = [arg.strip() for arg in self.args.split("=", 1)]
        field, new_value = [arg.strip() for arg in updates.split(",", 1)]

        controller = BBSController.objects.get(db_key="BBSController")
        if not controller:
            self.caller.msg("BBSController not found.")
            return

        board = controller.get_board(board_name)
        if not board:
            self.caller.msg(f"No board found with the name '{board_name}'.")
            return

        if field == "description":
            board['description'] = new_value
        elif field == "public":
            board['public'] = new_value.lower() in ["true", "yes", "1"]
        else:
            self.caller.msg(f"Invalid field '{field}'. You can edit 'description' or 'public'.")
            return

        controller.save_board(board_name, board)
        self.caller.msg(f"Board '{board_name}' has been updated. {field.capitalize()} set to '{new_value}'.")

class CmdResetBBS(default_cmds.MuxCommand):
    """
    Reinitialize the BBSController, wiping away all boards and posts.

    Usage:
      +bbs/reset

    This command will delete all existing boards and their posts,
    effectively resetting the BBS system. Use with caution.
    """
    key = "+bbs/reset"
    locks = "cmd:perm(Builder)"
    help_category = "BBS"

    def func(self):
        # Confirm the user's intention
        confirmation = self.caller.ndb.confirmation if hasattr(self.caller, 'ndb') else None
        if not confirmation or confirmation != "yes":
            self.caller.msg("This will wipe all boards and posts. Type '+bbs/reset yes' to confirm.")
            self.caller.ndb.confirmation = "yes"
            return

        # Reset the confirmation
        self.caller.ndb.confirmation = None

        # Find or create the BBSController
        try:
            controller = BBSController.objects.get(db_key="BBSController")
        except BBSController.DoesNotExist:
            controller = create_object(BBSController, key="BBSController")
            self.caller.msg("BBSController created.")

        # Reset the boards and initialize next_board_id
        controller.db.boards = {}
        controller.db.next_board_id = 1  # Initialize next_board_id to 1
        self.caller.msg("BBSController has been reset. All boards and posts have been deleted.")

class CmdGrantAccess(default_cmds.MuxCommand):
    """
    Grant access to a private board.

    Usage:
      +bbs/grantaccess <board_name> = <character_name> [/readonly]

    This command grants full access to a character by default. If "/readonly" is specified,
    the character is granted read-only access instead.

    Examples:
      +bbs/grantaccess Announcements = John
      +bbs/grantaccess Announcements = John /readonly
    """
    key = "+bbs/grantaccess"
    locks = "cmd:perm(Builder)"
    help_category = "BBS"

    def func(self):
        if not self.args or "=" not in self.args:
            self.caller.msg("Usage: +bbs/grantaccess <board_name> = <character_name> [/readonly]")
            return
        board_name, args = [arg.strip() for arg in self.args.split("=", 1)]
        character_name, *options = [arg.strip() for arg in args.split(" ")]

        # Determine access level
        access_level = "read_only" if "/readonly" in options else "full_access"

        controller = BBSController.objects.get(db_key="BBSController")
        if not controller:
            self.caller.msg("BBSController not found.")
            return

        board = controller.get_board(board_name)
        if not board:
            self.caller.msg(f"No board found with the name '{board_name}'.")
            return

        controller.grant_access(board_name, character_name, access_level=access_level)
        access_type = "read-only" if access_level == "read_only" else "full access"
        self.caller.msg(f"Granted {access_type} to {character_name} for board '{board_name}'.")
