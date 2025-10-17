import pytest

@pytest.mark.usefixtures("remove_test_data")
def test_xnatPlugin_installed(xnat_connection, plugin_version):
    assert "xnatPlugin" in xnat_connection.session.plugins
    xnat_plugin = xnat_connection.session.plugins["xnatPlugin"]
    assert xnat_plugin.version == f"{plugin_version}-xpl"
    assert xnat_plugin.name == "XNAT plugin" #XNAT 1.8 ISMRMRD plugin from plugin java class
