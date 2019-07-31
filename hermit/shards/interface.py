import re
from prompt_toolkit import prompt, print_formatted_text, shortcuts
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
        prompt("hit enter to continue\n")
        shortcuts.clear()

    def get_password(self, name: str) -> bytes:
        print("\nEnter password for shard {}".format(name))
        pass_msg = "password> ".format(name)
        return prompt(pass_msg, is_password=True).strip().encode('ascii')

    def confirm_password(self) -> bytes:
        password = prompt("new password> ",
                          is_password=True).strip().encode('ascii')
        confirm =  prompt("     confirm> ", is_password=True).strip().encode('ascii')

        if password == confirm:
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

        return (old_password, new_password)

    def get_name_for_shard(
            self, share_id, group_index, group_threshold, groups,
            member_index, member_threshold
            ):
        print("")
        print("Family: {}, Group: {}, Shard: {}".format(share_id, group_index + 1, member_index + 1))
        return prompt('Enter name: ', **self.options).strip()

    def choose_shard(self,
                     shards) -> Optional[str]:

        if len(shards) == 0:
            return None

        shardnames = [shard.name for shard in shards]
        shardnames.sort()

        shardCompleter = WordCompleter(shardnames)

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
        print("""SLIP39 sharding has two levels.

At the top level you specify Q groups, P of which are required to
unlock the wallet (P of Q groups).

For each of the Q groups you specify m shards, n of which are required
to unlock the group (n of m shards).  You can specify a different
combination of n and m for each group.

Unlock the wallet requires unlocking P groups and unlocking each group
requires unlocking n shards for that group.
"""
        )
        group_threshold = int(
            prompt("How many groups should be required to unlock the wallet (P)? ", completer=self.SmallNumberCompleter))
        groups : List[Tuple[int,int]] = []

        print_formatted_text("""
You will now specify the shard configuration for each group.

Hit Ctrl-D or enter an empty line once you have entered all Q groups.
""")
        input_error_message = "Please enter a shard configuration in the form 'n of m' where n and m are small integers."
        while True:
            try:
                group_str = prompt(
                    "What shard configuration should be used for group {} (eg 'n of m')? ".format(len(groups) + 1), completer=self.SmallNumberCompleter)
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
                    print(
                        "The number of required shards (n) must not be larger than the total number of shards (m)")
                else:
                    groups.append((n, m))

        return (group_threshold, groups)
