from roster.computer_control import (
    ComputerCommand,
    ComputerCommandError,
    execute_computer_command,
    parse_computer_command,
)


class FakePyAutoGUI:
    def __init__(self):
        self.calls = []

    def __getattr__(self, name):
        def record(*args, **kwargs):
            self.calls.append((name, args, kwargs))
        return record


def test_parser_supports_human_desktop_operations():
    assert parse_computer_command("click 100,200") == ComputerCommand("click", "100,200")
    assert parse_computer_command("double_click 100,200").operation == "double_click"
    assert parse_computer_command("drag 10,20 to 30,40").value == "10,20 to 30,40"
    assert parse_computer_command("hotkey ctrl+shift+esc").operation == "hotkey"


def test_parser_rejects_unknown_operations():
    try:
        parse_computer_command("shell whoami")
    except ComputerCommandError as exc:
        assert "unsupported" in str(exc)
    else:
        raise AssertionError("unknown operations must be rejected")


def test_click_is_allow_listed_and_structured():
    fake = FakePyAutoGUI()
    result = execute_computer_command(
        parse_computer_command("click 12,34"),
        pyautogui_module=fake,
    )
    assert result == "Clicked at (12, 34)."
    assert fake.calls[0][0] == "click"
    assert fake.calls[0][1] == (12, 34)


def test_hotkey_and_scroll_are_bounded():
    fake = FakePyAutoGUI()
    execute_computer_command(parse_computer_command("hotkey ctrl+s"), pyautogui_module=fake)
    execute_computer_command(parse_computer_command("scroll -5"), pyautogui_module=fake)
    assert fake.calls[0][0] == "hotkey"
    assert fake.calls[0][1] == ("ctrl", "s")
    assert fake.calls[1][0] == "scroll"
    assert fake.calls[1][1] == (-5,)


def test_scroll_rejects_extreme_values():
    fake = FakePyAutoGUI()
    try:
        execute_computer_command(parse_computer_command("scroll 21"), pyautogui_module=fake)
    except ComputerCommandError:
        pass
    else:
        raise AssertionError("extreme scroll values must be rejected")
