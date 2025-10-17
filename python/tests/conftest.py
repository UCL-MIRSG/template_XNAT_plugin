import os
import re
import subprocess
from pathlib import Path

import pytest
import xnat4tests
from xnat_mrd.fetch_datasets import get_singledata, get_multidata

from tests.utils import delete_data, XnatConnection


@pytest.fixture
def mrd_file_path():
    """Provides the mrd_data filepath"""

    mrd_data = get_singledata()

    return mrd_data


@pytest.fixture
def mrd_file_multidata_path():
    """Provides the mrd_data filepath"""

    mrd_data = get_multidata()

    return mrd_data


@pytest.fixture(scope="session")
def xnat_version():
    try:
        version = os.environ["XNAT_VERSION"]
    except KeyError:
        version = "1.9.2"

    return version


@pytest.fixture(scope="session")
def xnat_container_service_version():
    try:
        version = os.environ["XNAT_CS_VERSION"]
    except KeyError:
        version = "3.7.2"

    return version


@pytest.fixture
def ensure_mrd_project(xnat_connection):
    project_id = "mrd"
    xnat_session = xnat_connection.session
    if project_id not in xnat_session.projects:
        xnat_session.put(f"/data/archive/projects/{project_id}")
        xnat_session.projects.clearcache()


@pytest.fixture
def remove_test_data(xnat_connection):
    yield
    delete_data(xnat_connection.session)


@pytest.fixture(scope="session")
def xnat_config(xnat_version, xnat_container_service_version):
    xnat_root_dir = Path(__file__).parents[2] / ".xnat4tests" / "root"
    docker_build_dir = Path(__file__).parents[2] / ".xnat4tests" / "build"
    xnat_root_dir.mkdir(parents=True, exist_ok=True)
    docker_build_dir.mkdir(parents=True, exist_ok=True)

    return xnat4tests.Config(
        xnat_root_dir=xnat_root_dir,
        docker_build_dir=docker_build_dir,
        docker_image="xnat_mrd_xnat4tests",
        docker_container="xnat_mrd_xnat4tests",
        build_args={
            "xnat_version": xnat_version,
            "xnat_cs_plugin_version": xnat_container_service_version,
        },
    )


@pytest.fixture(scope="session")
def jar_path():
    """Path of jar built by gradlew"""

    jar_dir = Path(__file__).parents[2] / "build" / "libs"
    jar_path = list(jar_dir.glob("mrd-*xpl.jar"))[0]

    if not jar_path.exists():
        raise FileNotFoundError(f"Plugin JAR file not found at {jar_path}")

    return jar_path


@pytest.fixture(scope="session")
def plugin_dir():
    """Path to plugin directory inside the container"""

    return Path("/data/xnat/home/plugins")


@pytest.fixture(scope="session")
def plugin_version(jar_path):
    match_version = re.search("mrd-(.+?)-xpl.jar", jar_path.name)

    if match_version is None:
        raise NameError(
            "Jar name contains no version - did you pull the latest tags from github before running gradlew?"
        )
    else:
        return match_version.group(1)


@pytest.fixture(scope="session")
def xnat_connection(xnat_config, jar_path, plugin_dir):
    xnat4tests.start_xnat(xnat_config)
    connection = XnatConnection(xnat_config)

    # Install Mrd plugin by copying the jar into the container
    status = subprocess.run(
        [
            "docker",
            "exec",
            "xnat_mrd_xnat4tests",
            "ls",
            plugin_dir.as_posix(),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    plugins_list = status.stdout.split("\n")

    if jar_path.name not in plugins_list:
        try:
            subprocess.run(
                [
                    "docker",
                    "cp",
                    str(jar_path),
                    f"xnat_mrd_xnat4tests:{(plugin_dir / jar_path.name).as_posix()}",
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Command {e.cmd} returned with error code {e.returncode}: {e.output}"
            ) from e

        connection.restart_xnat()

    yield connection

    # Allow the docker container to be re-used when the XNAT4TEST_KEEP_INSTANCE environment variable is set.
    # This is useful for fast local development, where we don't want to wait for the long Docker startup times
    # between every test run.
    if os.environ.get("XNAT4TEST_KEEP_INSTANCE", "False").lower() == "false":
        connection.close()
        xnat4tests.stop_xnat(xnat_config)
    else:
        delete_data(connection.session)
        connection.close()
