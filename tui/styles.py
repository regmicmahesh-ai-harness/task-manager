"""TUI stylesheet — Textual CSS for the task manager."""

APP_CSS = """
Screen {
    background: $surface;
}

#board-selector {
    dock: top;
    height: 3;
    background: $primary-darken-2;
    padding: 0 2;
    content-align: center middle;
}

BoardSelector {
    width: 1fr;
    height: 3;
    color: $text;
    text-style: bold;
    text-align: center;
    content-align: center middle;
}

BoardSelector:focus {
    background: $accent;
    color: $text;
    text-style: bold underline;
}

#no-connection {
    width: 1fr;
    height: 1fr;
    content-align: center middle;
    text-align: center;
    color: $error;
}

BoardView {
    width: 1fr;
    height: 1fr;
    overflow-x: auto;
}

ListColumn {
    width: 36;
    min-width: 32;
    max-width: 42;
    height: 1fr;
    margin: 1;
    background: $surface-darken-1;
    border: tall $primary-background;
}

ListColumn:focus-within {
    border: tall $accent;
}

ColumnHeader {
    width: 1fr;
    height: 3;
    background: $primary;
    color: $text;
    text-align: center;
    text-style: bold;
    padding: 1 0;
}

ColumnHeader:focus {
    background: $accent;
    color: $text;
    text-style: bold underline;
}

.card-scroll {
    height: 1fr;
}

CardWidget {
    width: 1fr;
    height: auto;
    margin: 1 1 0 1;
    padding: 1;
    background: $surface-lighten-1;
    border: round $primary-background-lighten-1;
}

CardWidget:focus {
    border: round $warning;
    background: $surface-lighten-2;
}

.empty-list {
    width: 1fr;
    color: $text-disabled;
    text-align: center;
    margin: 2;
}

/* Modal styles */
ModalScreen {
    align: center middle;
}

#modal-dialog {
    width: 60;
    height: auto;
    max-height: 80%;
    background: $surface;
    border: thick $primary;
    padding: 1 2;
}

#modal-dialog Label {
    margin: 1 0 0 0;
}

#modal-dialog Input {
    margin: 0 0 1 0;
}

#modal-dialog Select {
    margin: 0 0 1 0;
}

#modal-buttons {
    height: 3;
    align: center middle;
    margin: 1 0 0 0;
}

#modal-buttons Button {
    margin: 0 1;
}

#modal-title {
    text-style: bold;
    text-align: center;
    width: 1fr;
    margin: 0 0 1 0;
    color: $text;
}

#modal-dialog Button {
    width: 1fr;
    margin: 0 0 1 0;
}
"""
