def test_builtin_module_imports_without_desktop_session():
    import roster.tools.builtin
    assert roster.tools.builtin.ToolExecutor

def test_local_provider_contract():
    from roster.providers.local import LocalProvider
    assert LocalProvider("test").model == "test"
