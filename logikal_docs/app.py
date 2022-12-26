"""
A tool for building and managing Python documentation.
"""
import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from importlib import import_module, metadata
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Dict, Sequence, Union

import tomli
from packaging.version import parse
from sphinx.application import Sphinx
from sphinx.cmd.build import jobs_argument


def _get_config_overrides(
    config_path: Path,
    default_config: Dict[str, Any],
    default_extension_config: Dict[str, Dict[str, Any]],
    base_config: Dict[str, Any],
) -> Dict[str, Any]:

    overrides = {**default_config, **base_config}
    if config_path.exists():
        sys.path.append(str(config_path.parents[1].absolute()))
        config = import_module(str(config_path.with_suffix('')).replace('/', '.'))

        if hasattr(config, 'html_baseurl'):
            raise RuntimeError(
                'Use the `projects.urls.Documentation` field '
                'in your `pyproject.toml` file to specify the base URL'
            )

        # Override default configuration
        for name in default_config:
            if hasattr(config, name):
                overrides[name] = getattr(config, name)

        # Extend base configuration
        for name, value in base_config.items():
            if isinstance(value, list):
                overrides[name].extend(getattr(config, name, []))
            elif isinstance(value, dict):
                overrides[name].update(getattr(config, name, {}))

        # Use extension default configurations
        for extension in overrides['extensions']:
            for name, value in default_extension_config.get(extension, {}).items():
                if not hasattr(config, name):
                    overrides[name] = value

    return overrides


def build(args: argparse.Namespace, project: str, author: str, version: str, base_url: str) -> int:
    process = subprocess.run(  # nosec: secure, not using untrusted input
        ['git', 'tag', '-l', 'v*'],
        cwd=str(args.source_path),
        capture_output=True, text=True, check=True,
    )
    tags = [tag[1:] for tag in process.stdout.splitlines()]
    tags = ['latest'] + list(sorted(tags, key=parse, reverse=True))

    if args.clear:
        print(f'Clearing "{args.output_path}"')
        shutil.rmtree(args.output_path, ignore_errors=True)

    # Configuration overrides
    extensions = ['sphinx_rtd_theme']
    if find_spec('jupyter_sphinx'):
        extensions.append('jupyter_sphinx')

    config_path = args.source_path / 'conf.py'
    config_overrides = _get_config_overrides(
        config_path=config_path,
        default_config={
            # Project information
            'project': project,
            'author': author,
            'copyright': f'{datetime.now().year}, {author}',
            'version': f'v{version}',
            'release': f'v{version}',
            # General configuration
            'nitpicky': True,
            'pygments_style': 'friendly',
            # Output configuration
            'html_theme': 'sphinx_rtd_theme',
            'html_baseurl': f'{base_url.rstrip("/")}/{version}/',
            'html_favicon': str((Path(__file__).parent / 'static/favicon.png').resolve()),
            'html_copy_source': False,
            'html_show_sphinx': False,
        },
        default_extension_config={
            'sphinx.ext.autosectionlabel': {'autosectionlabel_prefix_document': True},
            'sphinx.ext.autodoc': {
                'autoclass_content': 'both',
                'autodoc_default_options': {
                    'members': True, 'member-order': 'bysource', 'inherited-members': True,
                },
            },
            'sphinx.ext.napoleon': {'napoleon_numpy_docstring': False},
            'sphinx.ext.intersphinx': {'intersphinx_timeout': 15},
        },
        base_config={
            'extensions': extensions,
            'templates_path': [str((Path(__file__).parent / 'templates').resolve())],
            'html_static_path': [str((Path(__file__).parent / 'static').resolve())],
            'html_css_files': ['css/logikal_docs.css'],
            'html_context': {
                'current_version': version,
                'versions': ','.join(tags),
                'baseurl': base_url.rstrip("/"),
            },
        },
    )

    # Building
    app = Sphinx(
        srcdir=str(args.source_path),
        confdir=str(args.source_path) if config_path.exists() else None,
        outdir=str(args.output_path),
        doctreedir=str(args.output_path / '.doctrees'),
        buildername='html',
        confoverrides=config_overrides,
        warningiserror=True,
        parallel=jobs_argument('auto'),
        keep_going=True,
    )
    app.build()
    return app.statuscode


def main(args: Sequence[str] = tuple(sys.argv[1:])) -> Union[int, str]:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_argument_group(title='actions').add_mutually_exclusive_group()
    group.add_argument('-o', '--open', action='store_true', help='open documentation (default)')
    group.add_argument('-b', '--build', action='store_true', help='build documentation')
    group.add_argument('-v', '--version', action='store_true', help='show version')
    parser.add_argument('-c', '--clear', action='store_true', help='clear output directory')
    parser.add_argument('--source', metavar='PATH', dest='source_path', default='docs',
                        type=Path, help='source files (default: docs)')
    parser.add_argument('--output', metavar='PATH', dest='output_path', default='docs/build',
                        type=Path, help='build output (default: docs/build)')
    parsed_args = parser.parse_args(args)
    try:
        pyproject_path = parsed_args.source_path.parent / 'pyproject.toml'
        pyproject = tomli.loads(pyproject_path.read_text(encoding='utf-8'))
        project = pyproject['project']['name']
        version = (pyproject['project'].get('version') or metadata.version(project)).split('+')[0]

        if parsed_args.build:
            return build(
                args=parsed_args,
                project=project,
                author=', '.join(author['name'] for author in pyproject['project']['authors']),
                version=version,
                base_url=pyproject['project']['urls']['Documentation'],
            )

        if parsed_args.version:
            print(metadata.version('logikal-docs'))
            return 0

        index_path = str(parsed_args.output_path / 'index.html')
        print(f'Opening "{index_path}"')
        process = subprocess.run(['xdg-open', index_path], check=False)  # nosec: trusted input
        return process.returncode

    except KeyboardInterrupt:
        return 1
    except RuntimeError as error:
        return f'Error: {error}'
