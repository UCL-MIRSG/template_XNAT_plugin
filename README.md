# Template XNAT Plugin

This repository provides a template for an xnat plugin including:

- github actions for automated release (as a github release with attached jars,
  as well as to
  [Github Packages](https://docs.github.com/en/packages/learn-github-packages/introduction-to-github-packages)
  )
- github actions for linting with [pre-commit](https://pre-commit.com/)
- github actions + python files for running automated tests via
  [`xnat4tests`](https://github.com/Australian-Imaging-Service/xnat4tests)
- A framework for downloading test data from Zenodo with
  [`pooch`](https://www.fatiando.org/pooch/latest/) and caching with github
  actions

See the [`xnat-mrd`](https://github.com/SyneRBI/xnat-mrd) or
[`xnat-interfile`](https://github.com/SyneRBI/xnat-interfile) repositories, for
examples of plugins that use this template.

This template was created as part of the
[SyneRBI project](https://github.com/SyneRBI).

## Setting up the template

Click the green 'Use this template' button at the top right of the
[repository main page](https://github.com/UCL-MIRSG/template_XNAT_plugin) to
make a new repository.

### Update Gradle files

Update your plugin details in `build.gradle`:

- Change the group from `group "org.nrg.xnatx.plugins"` to a value appropriate
  for your project. Follow the
  [standard naming conventions](https://maven.apache.org/guides/mini/guide-naming-conventions.html).

- Update the `description` to describe what your plugin does.

- At the bottom of the file, update the publishing url to match the github
  organisation and repository name of your project.

  ```Gradle
  publishing {
    publications {
        ...
    }
    repositories {
      maven {
        // UPDATE THIS URL LINE
        url = "https://maven.pkg.github.com/ORGANISATION/REPOSITORY"
        ...
      }
    }
  }
  ```

Update the `rootProject.name` in the `settings.gradle` file.

### Populate the `src` directory

Fill the `/src` directory with your plugin files. You can find examples in the
official
[`xnat-template-plugin repository`](https://bitbucket.org/xnatx/xnat-template-plugin/src/master/),
or in the [`xnat-mrd`](https://github.com/SyneRBI/xnat-mrd) /
[`xnat-interfile`](https://github.com/SyneRBI/xnat-interfile) repositories.

### Update python test files

These files handle spinning up xnat in a Docker container (via `xnat4tests`),
and running automated tests. This uses [`xnatpy`](https://xnat.readthedocs.io/en/latest/) to handle calls to the xnat API.

Update `python/tests/conftest.py`:

- update the `jar_path` fixture to match the name of your built jar:

  ```python
  # e.g. to match a jar called test-VERSION-xpl.jar, update to:
  jar_path = list(jar_dir.glob("test-*xpl.jar"))[0]
  ```

- update the `plugin_version` fixture to match the jar path:

  ```python
  # e.g. to match a jar called test-VERSION-xpl.jar, update to:
  match_version = re.search("test-(.+?)-xpl.jar", jar_path.name)
  ```

Update `python/tests/test_server.py`:

- In `test_server.py`, a single example test is provided to verify the installed
  plugin version. You will need to update `"xnatPlugin"` and the expected value
  of `xnat_plugin.name` to match the `value` / `name` set in your `@XnatPlugin`
  java class (part of the plugin files in the `/src` directory).

- Expand `test_server.py` with additional automated tests for your plugin. E.g.
  see the [`xnat-mrd`](https://github.com/SyneRBI/xnat-mrd) /
  [`xnat-interfile`](https://github.com/SyneRBI/xnat-interfile) repositories for
  further test examples.

Update `python/pyproject.toml`. Note: this handles dependencies installed via
`pip`. If your tests depend on packages only available via `conda`, you will
need to specify those dependencies separately. See the
[`xnat-interfile`](https://github.com/SyneRBI/xnat-interfile) repository for an
example of a project with `conda` dependencies.

- Update the author email / name

- Update the description / name (optional)

- Add any extra python dependencies needed for your tests. These can be added to
  the `dependencies` or `dev` lists.

Update `python/src/xnat_plugin/fetch_datasets.py`:
- If you don't need test datasets, you can remove this file.
- Otherwise, edit the examples in this file to use your own `zenodo` doi links and image names. See the [`xnat-mrd`](https://github.com/SyneRBI/xnat-mrd) /
  [`xnat-interfile`](https://github.com/SyneRBI/xnat-interfile) repositories for examples of how to use these test datasets in tests.

### Update github actions workflows

- For the `.github/workflows/linting.yaml` workflow, you need to
[follow the instructions](https://github.com/pre-commit-ci/lite-action#setup)
for setting up the pre-commit.ci lite add-on for the
`Auto-fixes commit and push (pre-commit-ci-lite)` step.

- For `.github/workflows/test.yaml` to pass successfully, you will need to make one release on `main`.
  See [the release instructions](./docs/developer-docs.md#creating-a-new-release). 

- If you need additional conda dependencies then you can add another step after
`Set up Python` in `.github/workflows/test.yaml`:

```yaml
- name: Set up Miniconda
  uses: conda-incubator/setup-miniconda@v3
  with:
    python-version: 3.12
    auto-update-conda: true
    environment-file: python/environment.yml
    activate-environment: xnat-plugin-env
```

You would also need to add the following line to the `Install dependencies` and
`Run tests with pytest` steps:

```yaml
shell: bash -l {0} # required to load conda properly
```

An example of this can be found in the
[xnat-interfile reposistory](https://github.com/SyneRBI/xnat-interfile) with the
[.github/workflows/test.yaml](https://github.com/SyneRBI/xnat-interfile/blob/main/.github/workflows/test.yaml)
including the steps stated above and the other required
[python/environment.yml](https://github.com/SyneRBI/xnat-interfile/blob/main/python/environment.yml)
file.

## Developing the plugin

[Developer documentation](./docs/developer-docs.md) is provided for:
- building the plugin locally
- running tests locally
- making new releases on github
- running pre-commit locally
- updating versions of dependencies
