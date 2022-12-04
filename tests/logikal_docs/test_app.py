import subprocess
from pathlib import Path
from typing import List, NamedTuple

from pytest import CaptureFixture
from pytest_logikal.browser import Browser, set_browser
from pytest_mock import MockerFixture
from selenium.webdriver.common.by import By

from logikal_docs import app


def test_package_interface() -> None:
    command = ['/usr/bin/env', 'python3', '-m', 'logikal_docs', '-v']
    subprocess.run(command, check=True)  # nosec: trusted input


@set_browser(
    dict(name='desktop', width=1800),
    dict(name='mobile', width=600, mobile=True),
)
def test_build(browser: Browser, mocker: MockerFixture, tmp_path: Path) -> None:
    Tag = NamedTuple('Tag', [('name', str)])
    mocker.patch('logikal_docs.app.metadata.version', return_value='1.10.0')
    mocker.patch(
        'logikal_docs.app.git.Repo.tags',
        [Tag('v1.0.0'), Tag('v1.1.0'), Tag('v1.2.0'), Tag('v1.10.0')],
    )
    target_path = tmp_path / 'latest'  # ensures that we test the logic for the latest version
    app.main(['--build', '--output', str(target_path), '--clear'])
    browser.get(f'file://{target_path / "index.html"}')
    if browser.name == 'desktop':
        browser.find_element(By.CLASS_NAME, 'rst-versions').click()
    browser.check()


def test_version(capsys: CaptureFixture[str], mocker: MockerFixture) -> None:
    version = '1.0.0'
    mocker.patch('logikal_docs.app.metadata.version', return_value=version)
    app.main(['--version'])
    assert capsys.readouterr().out == f'{version}\n'


def test_open(mocker: MockerFixture) -> None:
    run = mocker.patch('logikal_docs.app.subprocess.run')
    run.return_value.returncode = 0
    assert app.main(['--open']) == 0
    assert run.called


def test_errors(mocker: MockerFixture) -> None:
    mocker.patch('logikal_docs.app.subprocess.run', side_effect=KeyboardInterrupt)
    assert app.main([]) == 1

    mocker.patch('logikal_docs.app.subprocess.run', side_effect=RuntimeError('Test'))
    assert app.main([]) == 'Error: Test'


def test_config_merging(mocker: MockerFixture) -> None:
    mocker.patch('logikal_docs.app.Path.exists', return_value=True)
    sphinx_main = mocker.patch('logikal_docs.app.Sphinx')
    import_module = mocker.patch('logikal_docs.app.import_module')

    Config = NamedTuple('Config', [('author', str), ('extensions', List[str])])
    config = Config(author='Test Author', extensions=['sphinx.ext.autodoc'])
    import_module.return_value = config
    app.main(['--build'])
    expected_extensions = ['sphinx_rtd_theme', 'jupyter_sphinx'] + config.extensions
    assert sphinx_main.call_args.kwargs['confoverrides']['extensions'] == expected_extensions
    assert sphinx_main.call_args.kwargs['confoverrides']['author'] == config.author

    InvalidConfig = NamedTuple('InvalidConfig', [('html_baseurl', str)])
    import_module.return_value = InvalidConfig(html_baseurl='Test')
    assert 'Error' in str(app.main(['--build']))
