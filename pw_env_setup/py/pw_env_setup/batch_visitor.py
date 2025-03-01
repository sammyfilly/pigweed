# Copyright 2021 The Pigweed Authors
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
"""Serializes an Environment into a batch file."""

# Disable super() warnings since this file must be Python 2 compatible.
# pylint: disable=super-with-arguments

# goto label written to the end of Windows batch files for exiting a script.
_SCRIPT_END_LABEL = '_pw_end'


class BatchVisitor(object):  # pylint: disable=useless-object-inheritance
    """Serializes an Environment into a batch file."""

    def __init__(self, *args, **kwargs):
        pathsep = kwargs.pop('pathsep', ':')
        super(BatchVisitor, self).__init__(*args, **kwargs)
        self._replacements = ()
        self._outs = None
        self._pathsep = pathsep

    def serialize(self, env, outs):
        """Write a batch file based on the given environment.

        Args:
            env (environment.Environment): Environment variables to use.
            outs (file): Batch file to write.
        """
        try:
            self._replacements = tuple(
                (key, env.get(key) if value is None else value)
                for key, value in env.replacements
            )
            self._outs = outs
            self._outs.write('@echo off\n')

            env.accept(self)

            outs.write(f':{_SCRIPT_END_LABEL}\n')

        finally:
            self._replacements = ()
            self._outs = None

    def _apply_replacements(self, action):
        value = action.value
        for var, replacement in self._replacements:
            if var != action.name:
                value = value.replace(replacement, f'%{var}%')
        return value

    def visit_set(self, set):  # pylint: disable=redefined-builtin
        value = self._apply_replacements(set)
        self._outs.write(
            'set {name}={value}\n'.format(name=set.name, value=value)
        )

    def visit_clear(self, clear):
        self._outs.write('set {name}=\n'.format(name=clear.name))

    def visit_remove(self, remove):
        pass  # Not supported on Windows.

    def _join(self, *args):
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        return self._pathsep.join(args)

    def visit_prepend(self, prepend):
        value = self._apply_replacements(prepend)
        value = self._join(value, f'%{prepend.name}%')
        self._outs.write(
            'set {name}={value}\n'.format(name=prepend.name, value=value)
        )

    def visit_append(self, append):
        value = self._apply_replacements(append)
        value = self._join(f'%{append.name}%', value)
        self._outs.write(
            'set {name}={value}\n'.format(name=append.name, value=value)
        )

    def visit_echo(self, echo):
        if echo.newline:
            if not echo.value:
                self._outs.write('echo.\n')
            else:
                self._outs.write(f'echo {echo.value}\n')
        else:
            self._outs.write(f'<nul set /p="{echo.value}"\n')

    def visit_comment(self, comment):
        for line in comment.value.splitlines():
            self._outs.write(f':: {line}\n')

    def visit_command(self, command):
        # TODO(mohrr) use shlex.quote here?
        self._outs.write(f"{' '.join(command.command)}\n")
        if not command.exit_on_error:
            return

        # Assume failing command produced relevant output.
        self._outs.write(f'if %ERRORLEVEL% neq 0 goto {_SCRIPT_END_LABEL}\n')

    def visit_doctor(self, doctor):
        self._outs.write('if "%PW_ACTIVATE_SKIP_CHECKS%"=="" (\n')
        self.visit_command(doctor)
        self._outs.write(') else (\n')
        self._outs.write(
            'echo Skipping environment check because '
            'PW_ACTIVATE_SKIP_CHECKS is set\n'
        )
        self._outs.write(')\n')

    def visit_blank_line(self, blank_line):
        del blank_line
        self._outs.write('\n')

    def visit_function(self, function):
        pass  # Not supported on Windows.

    def visit_hash(self, hash):  # pylint: disable=redefined-builtin
        pass  # Not relevant on Windows.
