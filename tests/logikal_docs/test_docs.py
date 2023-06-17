import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, NamedTuple

from pytest import CaptureFixture
from pytest_logikal.browser import Browser, set_browser
from pytest_mock import MockerFixture
from selenium.webdriver.common.by import By

from logikal_docs.docs import main


def test_package_interface() -> None:
    command = ['/usr/bin/env', 'python3', '-m', 'logikal_docs', '-v']
    subprocess.run(command, check=True)  # nosec: trusted input


@set_browser(
    dict(name='desktop', width=1800),
    dict(name='mobile', width=600, mobile=True),
)
def test_build(browser: Browser, mocker: MockerFixture, tmp_path: Path) -> None:
    # Note: pytest-freezer causes jupyter-sphinx to hang, so we're patching the module instead
    mock_datetime = mocker.patch('logikal_docs.docs.datetime')
    mock_datetime.now.return_value = datetime(2022, 10, 1)

    mocker.patch('logikal_docs.docs.metadata.version', return_value='1.10.0')
    run = mocker.patch('logikal_docs.docs.subprocess.run')
    run.return_value.stdout = '\n'.join(['v1.0.0', 'v1.1.0', 'v1.2.0', 'v1.10.0'])
    target_path = tmp_path / 'latest'  # ensures that we test the logic for the latest version
    main(['--build', '--output', str(target_path), '--clear'])
    browser.get(f'file://{target_path / "index.html"}')
    if browser.name == 'desktop':
        browser.find_element(By.CLASS_NAME, 'rst-versions').click()
    browser.check()


def test_version(capsys: CaptureFixture[str], mocker: MockerFixture) -> None:
    version = '1.0.0'
    mocker.patch('logikal_docs.docs.metadata.version', return_value=version)
    main(['--version'])
    assert capsys.readouterr().out == f'{version}\n'


def test_open(mocker: MockerFixture) -> None:
    run = mocker.patch('logikal_docs.docs.subprocess.run')
    run.return_value.returncode = 0
    assert not main(['--open'])
    assert run.called


def test_errors(mocker: MockerFixture) -> None:
    mocker.patch('logikal_docs.docs.subprocess.run', side_effect=KeyboardInterrupt)
    assert main([]) == 1

    mocker.patch('logikal_docs.docs.subprocess.run', side_effect=RuntimeError('Test'))
    assert main([]) == 'Error: Test'


def test_config_merging(mocker: MockerFixture) -> None:
    mocker.patch('logikal_docs.docs.Path.exists', return_value=True)
    sphinx_main = mocker.patch('logikal_docs.docs.Sphinx')
    import_module = mocker.patch('logikal_docs.docs.import_module')

    Config = NamedTuple('Config', [('author', str), ('extensions', List[str])])
    config = Config(author='Test Author', extensions=['sphinx.ext.autodoc'])
    import_module.return_value = config
    main(['--build'])
    expected_extensions = ['sphinx_rtd_theme', 'jupyter_sphinx'] + config.extensions
    assert sphinx_main.call_args.kwargs['confoverrides']['extensions'] == expected_extensions
    assert sphinx_main.call_args.kwargs['confoverrides']['author'] == config.author

    InvalidConfig = NamedTuple('InvalidConfig', [('html_baseurl', str)])
    import_module.return_value = InvalidConfig(html_baseurl='Test')
    assert 'Error' in str(main(['--build']))
