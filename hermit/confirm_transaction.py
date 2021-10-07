#from prompt_toolkit.layout import ScrollablePane, HSplit, BufferControl, FormattedTextControl, Window, Container

from prompt_toolkit.widgets import Label, Button, Dialog, TextArea

from prompt_toolkit.application.current import get_app

from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings

#from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.key_binding.defaults import load_key_bindings

from prompt_toolkit.key_binding.bindings.focus import focus_next, focus_previous

from prompt_toolkit.application import Application
from prompt_toolkit.layout import Layout

from prompt_toolkit.key_binding.bindings.scroll import (
    scroll_forward, scroll_backward,
    scroll_half_page_up, scroll_half_page_down,
    scroll_one_line_up, scroll_one_line_down,
)
from prompt_toolkit.styles import Style

confirm_style = Style.from_dict({
    'dialog':             'bg:#000000',
    'dialog frame.label': 'bg:#000000 #ffffff',
    'dialog.body':        'bg:#000000 #ffffff',
    'dialog shadow':      'bg:#000000',
    'text-area':          'bg:#888888 #ffffff',
    'text-area.prompt':   'bg:#888888 #ffffff',

})


def confirm_transaction_dialog(title=None, transaction=None, style=None):
    """
    Display a Yes/No dialog showing the descriptions of the transaction.

    Return a boolean.
    """
    style = style or confirm_style

    # Set up handlers for events that signal that we do want to sign the
    # transaction.

    def yes_handler(event=None):
        get_app().exit(result=True)

    def no_handler(event=None):
        get_app().exit(result=False)

    title = title or "Sign this Transaction?"

    if transaction is None:
        transaction = '\n'.join(f"This is line {i}" for i in range (100))

    # Display the transaction description in a big, read only TextArea control.
    body = TextArea(
        text=transaction,
        multiline=True,
        read_only=True,
        scrollbar=True,
    )


    dialog = Dialog(
        title=title,
        body=body,
        buttons=[
            Button(
                text='Yes', handler=yes_handler, width=8,
                # left_symbol='[', right_symbol=']',
            ),
            Label('    '),
            Button(
                text='No', handler=no_handler, width=8,
                # left_symbol='[', right_symbol=']',
            ),
        ],
        with_background=False,
    )

    # Key bindings.
    bindings = KeyBindings()
    bindings.add("tab")(focus_next)
    bindings.add("s-tab")(focus_previous)
    bindings.add("pagedown")(scroll_forward)
    bindings.add("pageup")(scroll_backward)
    bindings.add("up")(scroll_one_line_up)
    bindings.add("down")(scroll_one_line_down)
    bindings.add("s-up")(scroll_one_line_up)
    bindings.add("s-down")(scroll_one_line_down)
    bindings.add("c-up")(scroll_half_page_up)
    bindings.add("c-down")(scroll_half_page_down)

    bindings.add("y")(yes_handler)
    bindings.add("n")(no_handler)

    return Application(
        layout=Layout(dialog),
        key_bindings=merge_key_bindings([load_key_bindings(), bindings]),
        mouse_support=True,
        style=style,
        full_screen=True,
    )

if __name__ == '__main__':
    print(confirm_transaction_dialog().run())
