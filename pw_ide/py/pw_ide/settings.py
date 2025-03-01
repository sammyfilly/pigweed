# Copyright 2022 The Pigweed Authors
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.
"""pw_ide settings."""

import enum
from inspect import cleandoc
import os
from pathlib import Path
from typing import Any, cast, Dict, List, Literal, Optional, Tuple, Union
import yaml

from pw_cli.env import pigweed_environment
from pw_cli.yaml_config_loader_mixin import YamlConfigLoaderMixin

env = pigweed_environment()
env_vars = vars(env)

PW_IDE_DIR_NAME = '.pw_ide'
PW_IDE_DEFAULT_DIR = Path(env.PW_PROJECT_ROOT) / PW_IDE_DIR_NAME

_DEFAULT_BUILD_DIR_NAME = 'out'
_DEFAULT_BUILD_DIR = env.PW_PROJECT_ROOT / _DEFAULT_BUILD_DIR_NAME

_DEFAULT_TARGET_INFERENCE = '?'

SupportedEditorName = Literal['vscode']


class SupportedEditor(enum.Enum):
    VSCODE = 'vscode'


_DEFAULT_SUPPORTED_EDITORS: Dict[SupportedEditorName, bool] = {
    'vscode': True,
}

_DEFAULT_CONFIG: Dict[str, Any] = {
    'cascade_targets': False,
    'clangd_additional_query_drivers': [],
    'compdb_search_paths': [_DEFAULT_BUILD_DIR_NAME],
    'default_target': None,
    'editors': _DEFAULT_SUPPORTED_EDITORS,
    'sync': ['pw --no-banner ide cpp --process'],
    'targets': [],
    'target_inference': _DEFAULT_TARGET_INFERENCE,
    'working_dir': PW_IDE_DEFAULT_DIR,
}

_DEFAULT_PROJECT_FILE = Path('$PW_PROJECT_ROOT/.pw_ide.yaml')
_DEFAULT_PROJECT_USER_FILE = Path('$PW_PROJECT_ROOT/.pw_ide.user.yaml')
_DEFAULT_USER_FILE = Path('$HOME/.pw_ide.yaml')


def _expand_any_vars(input_path: Path) -> Path:
    """Expand any environment variables in a path.

    Python's ``os.path.expandvars`` will only work on an isolated environment
    variable name. In shell, you can expand variables within a larger command
    or path. We replicate that functionality here.
    """
    outputs = []

    for token in input_path.parts:
        expanded_var = os.path.expandvars(token)

        if expanded_var == token:
            outputs.append(token)
        else:
            outputs.append(expanded_var)

    # pylint: disable=no-value-for-parameter
    return Path(os.path.join(*outputs))
    # pylint: enable=no-value-for-parameter


def _expand_any_vars_str(input_path: str) -> str:
    """`_expand_any_vars`, except takes and returns a string instead of path."""
    return str(_expand_any_vars(Path(input_path)))


def _parse_dir_path(input_path_str: str) -> Path:
    if (path := Path(input_path_str)).is_absolute():
        return path

    return Path.cwd() / path


def _parse_compdb_search_path(
    input_data: Union[str, Tuple[str, str]], default_inference: str
) -> Tuple[Path, str]:
    if isinstance(input_data, (tuple, list)):
        return _parse_dir_path(input_data[0]), input_data[1]

    return _parse_dir_path(input_data), default_inference


class PigweedIdeSettings(YamlConfigLoaderMixin):
    """Pigweed IDE features settings storage class."""

    def __init__(
        self,
        project_file: Union[Path, bool] = _DEFAULT_PROJECT_FILE,
        project_user_file: Union[Path, bool] = _DEFAULT_PROJECT_USER_FILE,
        user_file: Union[Path, bool] = _DEFAULT_USER_FILE,
        default_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.config_init(
            config_section_title='pw_ide',
            project_file=project_file,
            project_user_file=project_user_file,
            user_file=user_file,
            default_config=_DEFAULT_CONFIG
            if default_config is None
            else default_config,
            environment_var='PW_IDE_CONFIG_FILE',
        )

    @property
    def working_dir(self) -> Path:
        """Path to the ``pw_ide`` working directory.

        The working directory holds C++ compilation databases and caches, and
        other supporting files. This should not be a directory that's regularly
        deleted or manipulated by other processes (e.g. the GN ``out``
        directory) nor should it be committed to source control.
        """
        return Path(self._config.get('working_dir', PW_IDE_DEFAULT_DIR))

    @property
    def compdb_search_paths(self) -> List[Tuple[Path, str]]:
        """Paths to directories to search for compilation databases.

        If you're using a build system to generate compilation databases, this
        may simply be your build output directory. However, you can add
        additional directories to accommodate compilation databases from other
        sources.

        Entries can be just directories, in which case the default target
        inference pattern will be used. Or entries can be tuples of a directory
        and a target inference pattern. See the documentation for
        ``target_inference`` for more information.
        """
        return [
            _parse_compdb_search_path(search_path, self.target_inference)
            for search_path in self._config.get(
                'compdb_search_paths', _DEFAULT_BUILD_DIR
            )
        ]

    @property
    def targets(self) -> List[str]:
        """The list of targets that should be enabled for code analysis.

        In this case, "target" is analogous to a GN target, i.e., a particular
        build configuration. By default, all available targets are enabled. By
        adding targets to this list, you can constrain the targets that are
        enabled for code analysis to a subset of those that are available, which
        may be useful if your project has many similar targets that are
        redundant from a code analysis perspective.

        Target names need to match the name of the directory that holds the
        build system artifacts for the target. For example, GN outputs build
        artifacts for the ``pw_strict_host_clang_debug`` target in a directory
        with that name in its output directory. So that becomes the canonical
        name for the target.
        """
        return self._config.get('targets', [])

    @property
    def target_inference(self) -> str:
        """A glob-like string for extracting a target name from an output path.

        Build systems and projects have varying ways of organizing their build
        directory structure. For a given compilation unit, we need to know how
        to extract the build's target name from the build artifact path. A
        simple example:

        .. code-block:: none

           clang++ hello.cc -o host/obj/hello.cc.o

        The top-level directory ``host`` is the target name we want. The same
        compilation unit might be used with another build target:

        .. code-block:: none

           gcc-arm-none-eabi hello.cc -o arm_dev_board/obj/hello.cc.o

        In this case, this compile command is associated with the
        ``arm_dev_board`` target.

        When importing and processing a compilation database, we assume by
        default that for each compile command, the corresponding target name is
        the name of the top level directory within the build directory root
        that contains the build artifact. This is the default behavior for most
        build systems. However, if your project is structured differently, you
        can provide a glob-like string that indicates how to extract the target
        name from build artifact path.

        A ``*`` indicates any directory, and ``?`` indicates the directory that
        has the name of the target. The path is resolved from the build
        directory root, and anything deeper than the target directory is
        ignored. For example, a glob indicating that the directory two levels
        down from the build directory root has the target name would be
        expressed with ``*/*/?``.

        Note that the build artifact path is relative to the compilation
        database search path that found the file. For example, for a compilation
        database search path of ``{project dir}/out``, for the purposes of
        target inference, the build artifact path is relative to the ``{project
        dir}/out`` directory. Target inference patterns can be defined for each
        compilation database search path. See the documentation for
        ``compdb_search_paths`` for more information.
        """
        return self._config.get('target_inference', _DEFAULT_TARGET_INFERENCE)

    @property
    def default_target(self) -> Optional[str]:
        """The default target to use when calling ``--set-default``.

        This target will be selected when ``pw ide cpp --set-default`` is
        called. You can define an explicit default target here. If that command
        is invoked without a default target definition, ``pw_ide`` will try to
        infer the best choice of default target. Currently, it selects the
        target with the broadest compilation unit coverage.
        """
        return self._config.get('default_target', None)

    @property
    def sync(self) -> List[str]:
        """A sequence of commands to automate IDE features setup.

        ``pw ide sync`` should do everything necessary to get the project from
        a fresh checkout to a working default IDE experience. This defines the
        list of commands that makes that happen, which will be executed
        sequentially in subprocesses. These commands should be idempotent, so
        that the user can run them at any time to update their IDE features
        configuration without the risk of putting those features in a bad or
        unexpected state.
        """
        return self._config.get('sync', [])

    @property
    def clangd_additional_query_drivers(self) -> List[str]:
        """Additional query driver paths that clangd should use.

        By default, ``pw_ide`` supplies driver paths for the toolchains included
        in Pigweed. If you are using toolchains that are not supplied by
        Pigweed, you should include path globs to your toolchains here. These
        paths will be given higher priority than the Pigweed toolchain paths.
        """
        return self._config.get('clangd_additional_query_drivers', [])

    def clangd_query_drivers(self) -> List[str]:
        drivers = [
            *[
                _expand_any_vars_str(p)
                for p in self.clangd_additional_query_drivers
            ],
        ]

        if (env_var := env_vars.get('PW_PIGWEED_CIPD_INSTALL_DIR')) is not None:
            drivers.append(str(Path(env_var) / 'bin' / '*'))

        if (env_var := env_vars.get('PW_ARM_CIPD_INSTALL_DIR')) is not None:
            drivers.append(str(Path(env_var) / 'bin' / '*'))

        return drivers

    def clangd_query_driver_str(self) -> str:
        return ','.join(self.clangd_query_drivers())

    @property
    def editors(self) -> Dict[str, bool]:
        """Enable or disable automated support for editors.

        Automatic support for some editors is provided by ``pw_ide``, which is
        accomplished through generating configuration files in your project
        directory. All supported editors are enabled by default, but you can
        disable editors by adding an ``'<editor>': false`` entry.
        """
        return self._config.get('editors', _DEFAULT_SUPPORTED_EDITORS)

    def editor_enabled(self, editor: SupportedEditorName) -> bool:
        """True if the provided editor is enabled in settings.

        This module will integrate the project with all supported editors by
        default. If the project or user want to disable particular editors,
        they can do so in the appropriate settings file.
        """
        return self._config.get('editors', {}).get(editor, False)

    @property
    def cascade_targets(self) -> bool:
        """Mix compile commands for multiple targets to maximize code coverage.

        By default (with this set to ``False``), the compilation database for
        each target is consistent in the sense that it only contains compile
        commands for one build target, so the code intelligence that database
        provides is related to a single, known compilation artifact. However,
        this means that code intelligence may not be provided for every source
        file in a project, because some source files may be relevant to targets
        other than the one you have currently set. Those source files won't
        have compile commands for the current target, and no code intelligence
        will appear in your editor.

        If this is set to ``True``, compilation databases will still be
        separated by target, but compile commands for *all other targets* will
        be appended to the list of compile commands for *that* target. This
        will maximize code coverage, ensuring that you have code intelligence
        for every file that is built for any target, at the cost of
        consistency—the code intelligence for some files may show information
        that is incorrect or irrelevant to the currently selected build target.

        The currently set target's compile commands will take priority at the
        top of the combined file, then all other targets' commands will come
        after in order of the number of commands they have (i.e. in the order of
        their code coverage). This relies on the fact that ``clangd`` parses the
        compilation database from the top down, using the first compile command
        it encounters for each compilation unit.
        """
        return self._config.get('cascade_targets', False)


def _docstring_set_default(
    obj: Any, default: Any, literal: bool = False
) -> None:
    """Add a default value annotation to a docstring.

    Formatting isn't allowed in docstrings, so by default we can't inject
    variables that we would like to appear in the documentation, like the
    default value of a property. But we can use this function to add it
    separately.
    """
    if obj.__doc__ is None:
        return
    default = str(default)

    if literal:
        if lines := default.splitlines():
            default = (
                f'Default: ``{lines[0]}``'
                if len(lines) == 1
                else 'Default:\n\n.. code-block::\n\n  ' + '\n  '.join(lines)
            )
        else:
            return
    doc = cast(str, obj.__doc__)
    obj.__doc__ = f'{cleandoc(doc)}\n\n{default}'


_docstring_set_default(
    PigweedIdeSettings.working_dir, PW_IDE_DIR_NAME, literal=True
)
_docstring_set_default(
    PigweedIdeSettings.compdb_search_paths,
    [_DEFAULT_BUILD_DIR_NAME],
    literal=True,
)
_docstring_set_default(
    PigweedIdeSettings.targets, _DEFAULT_CONFIG['targets'], literal=True
)
_docstring_set_default(
    PigweedIdeSettings.default_target,
    _DEFAULT_CONFIG['default_target'],
    literal=True,
)
_docstring_set_default(
    PigweedIdeSettings.cascade_targets,
    _DEFAULT_CONFIG['cascade_targets'],
    literal=True,
)
_docstring_set_default(
    PigweedIdeSettings.target_inference,
    _DEFAULT_CONFIG['target_inference'],
    literal=True,
)
_docstring_set_default(
    PigweedIdeSettings.sync, _DEFAULT_CONFIG['sync'], literal=True
)
_docstring_set_default(
    PigweedIdeSettings.clangd_additional_query_drivers,
    _DEFAULT_CONFIG['clangd_additional_query_drivers'],
    literal=True,
)
_docstring_set_default(
    PigweedIdeSettings.editors,
    yaml.dump(_DEFAULT_SUPPORTED_EDITORS),
    literal=True,
)
