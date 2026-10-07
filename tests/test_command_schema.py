import pytest
from roster.command_schema import Command
def test_command_normalizes_and_copies_arguments():
    args={"path":"notes.txt"}; c=Command(" read_file ",args,"req").normalized()
    assert c.name=="READ_FILE" and c.arguments==args and c.arguments is not args
def test_command_requires_name():
    with pytest.raises(ValueError): Command("")
