import re
from prompt_toolkit import prompt, print_formatted_text, shortcuts, HTML
from prompt_toolkit.completion import WordCompleter
from hermit.wordlists import WalletWords, ShardWords
from hermit.errors import HermitError
from typing import List, Dict, Optional, Tuple


class ShardWordUserInterface(object):
    """ShardWordUserInterface

    This class represents all of the interactions that the shard
    classes need to have with the user.
    """
    YesNoCompleter = WordCompleter(["no", "yes"])
    WalletWordCompleter = WordCompleter(WalletWords)
    ShardWordCompleter = WordCompleter(ShardWords)
    SmallNumberCompleter = WordCompleter([str(n) for n in range(1, 16)])

    def __init__(self) -> None:
        self.options: Dict = {}

    def get_line_then_clear(self) -> None:
        prompt(HTML("Hit <b>ENTER</b> to continue...\n"))
        shortcuts.clear()

    def get_password(self, name: str) -> bytes:
        print_formatted_text(HTML("\nEnter password for shard {}".format(name)))
        pass_msg = "password> ".format(name)
        password = prompt(pass_msg, is_password=True).strip().encode('ascii')

        # Empty string means do not encrypt with a password
        if len(password) == 0:
            return None
            
        return password
        
    def confirm_password(self) -> bytes:
        password = prompt("new password> ",
                          is_password=True).strip().encode('ascii')
        confirm =  prompt("     confirm> ", is_password=True).strip().encode('ascii')

        if password == confirm:
            # Empty string means do not encrypt
            if len(password) == 0:
                return None
            return password

        raise HermitError("Passwords do not match.")

    def get_change_password(self, name: str) -> Tuple[bytes, bytes]:
        # promt_toolkit's 'is_password' option
        # replaces input with '*' characters
        # while getpass echos nothing.

        print_formatted_text("\nChange password for shard {}".format(name))
        old_password: bytes = prompt(
            "old password> ", is_password=True).strip().encode('ascii')
        new_password = self.confirm_password()

        # Empty string means do not encrypt    
        if len(old_password) == 0:
            old_password = None

        if len(new_password) == 0:
            new_password = None

        return (old_password, new_password)

    def get_name_for_shard(
            self, share_id, group_index, group_threshold, groups,
            member_index, member_threshold, shards
            ):

        print_formatted_text("")
        print_formatted_text("Family: {}, Group: {}, Shard: {}".format(share_id, group_index + 1, member_index + 1))

        while True:
            name = prompt('Enter name: ', **self.options).strip()
            if name not in shards:
                return name

            print_formatted_text("Sorry, but a shard with that name already exists. Try again.")

    def choose_shard(self,
                     shards) -> Optional[str]:

        if len(shards) == 0:
            raise HermitError("Not enough shards to reconstruct secret.")

        shardnames = [shard.name for shard in shards]
        shardnames.sort()

        shardCompleter = WordCompleter(shardnames, sentence=True)

        while True:
            prompt_string = "Choose shard\n(options: {} or <enter> to quit)\n> "
            prompt_msg = prompt_string.format(", ".join(shardnames))
            shard_name = prompt(prompt_msg,
                                completer=shardCompleter,
                                **self.options).strip()

            if shard_name in shardnames:
                return shard_name

            if shard_name == '':
                return None

            print("Shard not found.")

    def confirm_delete_shard(self, shard_name: str) -> bool:
        return prompt("Really delete shard {0}? ".format(shard_name),
                      completer=self.YesNoCompleter) == "yes"

    def confirm_initialize_file(self) -> bool:
        return prompt("Really initialize the shard file? ",
                      completer=self.YesNoCompleter) == "yes"

    def choose_shard_name(self, number: int) -> str:
        prompt_msg = "\nEnter name for shard {0}: ".format(number)
        return prompt(prompt_msg, **self.options).strip()

    def enter_shard_words(self, name: str) -> str:
        print(("\nEnter SLIP39 phrase for shard {} below (CTRL-D to submit):".format(name)))
        lines: List = []
        while True:
            try:
                line = prompt("", completer=self.ShardWordCompleter,
                              **self.options).strip()
            except EOFError:
                break
            # Test against wordlist
            words = line.lower().split()
            if set(words).issubset(ShardWords):
                lines += words
            else:
                for word in words:
                    if word not in ShardWords:
                        print(("{} is not a valid shard word, "
                               + "ignoring last line").format(word))
        shortcuts.clear()
        return ' '.join(lines)

    def enter_wallet_words(self) -> str:
        print("\nEnter BIP39 phrase for wallet below (CTRL-D to submit): ")
        lines: List = []
        while True:
            try:
                line = prompt("", completer=self.WalletWordCompleter,
                              **self.options).strip()
            except EOFError:
                break

            words = line.lower().split()
            if set(words).issubset(WalletWords):
                lines += words
            else:
                for word in words:
                    if word not in ShardWords:
                        print(("{} is not a valid wallet word, "
                               + "ignoring last line").format(word))
        shortcuts.clear()
        return ' '.join(lines)

    def enter_group_information(self) -> Tuple[int, List[Tuple[int,int]]]:
        print_formatted_text(HTML("""SLIP39 sharding has two levels.

At the upper level you specify <i>Q</i> groups, <i>P</i> of which are required to
unlock the wallet (<i>P of Q</i> groups).
"""))
        group_threshold = int(
            prompt(HTML("<b>How many groups should be required to unlock the wallet (<i>P</i>)?</b> "), completer=self.SmallNumberCompleter))
        groups : List[Tuple[int,int]] = []

        print_formatted_text(HTML("""
Each of the <i>Q</i> groups is itself broken into <i>m</i> shards, <i>n</i> of which are
required to unlock the group (<i>n of m</i> shards).

Unlocking the wallet requires unlocking <i>P</i> groups and unlocking each
group requires unlocking <i>n</i> shards for that group.

You must now specify a shard configuration (such as '<i>2 of 3</i>')
for each of the Q groups.

Hit <b>Ctrl-D</b> or enter an empty line once you have entered
shard configurations for all <i>Q</i> groups.
"""))
        input_error_message = HTML("Please enter a shard configuration in the form '<i>n of m</i>' where <i>n</i> and <i>m</i> are small integers.")
        while True:
            try:
                group_str = prompt(
                    HTML("<b>What shard configuration should be used for <i>Group {}</i>?</b> ".format(len(groups) + 1)), completer=self.SmallNumberCompleter)
            except EOFError:
                if group_threshold > len(groups):
                    print_formatted_text(input_error_message)
                    continue
                else:
                    break

            if group_str == '' and len(groups) >= group_threshold:
                break
            match = re.match(r'^\s*(\d+)\s*of\s*(\d+)', group_str)
            if not match:
                print_formatted_text(input_error_message)
            else:
                (n, m) = match.groups()

                n = int(n)
                m = int(m)
                if(n > m):
                    print_formatted_text(HTML(
                        "The number of required shards (<i>n</i>) must not be larger than the total number of shards (<i>m</i>)"))
                else:
                    groups.append((n, m))

        return (group_threshold, groups)
