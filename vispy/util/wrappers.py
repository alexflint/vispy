# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
"""
Some wrappers to avoid circular imports, or make certain calls easier.
"""

"""
The idea of a 'global' vispy.use function is that although vispy.app
and vispy.gloo.gl can be used independently, they are not complely
independent for some configureation. E.g. when using real ES 2.0,
the app backend should use EGL and not a desktop OpenGL context. Also,
we probably want it to be easy to configure vispy to use the ipython
notebook backend, which requires specifc config of both app and gl.

This module does not have to be aware of the available app and gl
backends, but it should be(come) aware of (in)compatibilities between
them.
"""

import subprocess
import inspect


def use(app=None, gl=None):
    """ Set the usage options for vispy

    Specify what app backend and GL backend to use. Also see
    ``vispy.app.use_app()`` and ``vispy.gloo.gl.use_gl()``.

    Parameters
    ----------
    app : str
        The app backend to use (case insensitive). Standard backends:
            * 'PyQt4': use Qt widget toolkit via PyQt4.
            * 'PySide': use Qt widget toolkit via PySide.
            * 'PyGlet': use Pyglet backend.
            * 'Glfw': use Glfw backend (successor of Glut). Widely available
              on Linux.
            * 'SDL2': use SDL v2 backend.
            * 'Glut': use Glut backend. Widely available but limited.
              Not recommended.
        Additional backends:
            * 'ipynb_vnc': render in the IPython notebook via a VNC approach
              (experimental)
    gl : str
        The gl backend to use (case insensitive). Options are:
            * 'desktop': use Vispy's desktop OpenGL API.
            * 'pyopengl': use PyOpenGL's desktop OpenGL API. Mostly for
              testing.
            * 'angle': (TO COME) use real OpenGL ES 2.0 on Windows via Angle.
              Availability of ES 2.0 is larger for Windows, since it relies
              on DirectX.
            * If 'debug' is included in this argument, vispy will check for
              errors after each gl command.

    Notes
    -----
    If the app option is given, ``vispy.app.use_app()`` is called. If
    the gl option is given, ``vispy.gloo.use_gl()`` is called.

    If an app backend name is provided, and that backend could not be
    loaded, an error is raised.

    If no backend name is provided, Vispy will first check if the GUI
    toolkit corresponding to each backend is already imported, and try
    that backend first. If this is unsuccessful, it will try the
    'default_backend' provided in the vispy config. If still not
    succesful, it will try each backend in a predetermined order.
    """
    if app is None and gl is None:
        raise TypeError('Must specify at least one of "app" or "gl".')

    # Example for future. This wont work (yet).
    if app == 'ipynb_webgl':
        app = 'headless'
        gl = 'webgl'

    # Apply now
    if app:
        import vispy.app
        vispy.app.use_app(app)
    if gl:
        import vispy.gloo
        vispy.gloo.gl.use_gl(gl)


def run_subprocess(command, return_code=False, **kwargs):
    """Run command using subprocess.Popen

    Run command and wait for command to complete. If the return code was zero
    then return, otherwise raise CalledProcessError.
    By default, this will also add stdout= and stderr=subproces.PIPE
    to the call to Popen to suppress printing to the terminal.

    Parameters
    ----------
    command : list of str
        Command to run as subprocess (see subprocess.Popen documentation).
    return_code : bool
        If True, the returncode will be returned, and no error checking
        will be performed (so this function should always return without
        error).
    **kwargs : dict
        Additional kwargs to pass to ``subprocess.Popen``.

    Returns
    -------
    stdout : str
        Stdout returned by the process.
    stderr : str
        Stderr returned by the process.
    code : int
        The command exit code. Only returned if ``return_code`` is True.
    """
    # code adapted with permission from mne-python
    use_kwargs = dict(stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    use_kwargs.update(kwargs)

    p = subprocess.Popen(command, **use_kwargs)
    stdout_, stderr = p.communicate()
    stdout_ = stdout_.decode('utf-8') if stdout_ is not None else ''
    stderr = stderr.decode('utf-8') if stderr is not None else ''
    output = (stdout_, stderr)
    if not return_code and p.returncode:
        print(stdout_)
        print(stderr)
        err_fun = subprocess.CalledProcessError.__init__
        if 'output' in inspect.getargspec(err_fun).args:
            raise subprocess.CalledProcessError(p.returncode, command, output)
        else:
            raise subprocess.CalledProcessError(p.returncode, command)
    if return_code:
        output = output + (p.returncode,)
    return output
