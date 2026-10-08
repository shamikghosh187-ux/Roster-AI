import pytest
from roster.tool_catalog import ToolCatalog
from roster.tool_contract import ToolContract

def test_catalog_discovers_registered_tools():
    catalog=ToolCatalog(); catalog.register(ToolContract("search","Search"))
    assert catalog.names()==("search",)
    assert catalog.get(" SEARCH ").name=="search"

def test_catalog_rejects_duplicates():
    catalog=ToolCatalog(); catalog.register(ToolContract("search","Search"))
    with pytest.raises(ValueError): catalog.register(ToolContract("SEARCH","Other"))
