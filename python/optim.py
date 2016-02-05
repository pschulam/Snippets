"""Tools for optimization.

This module does not (yet) implement any optimization algorithms; many
such algorithms can be imported from scipy.optimize (or other
optimization libraries). Instead, it provides a suite of tools that
are useful when prototyping and debugging an optimization problem. In
the future, some simple algorithms like gradient descent (GD) and
stochastic GD may be added.

"""
import numpy as np
import scipy.linalg as la


_DEFAULT_STEP = 1e-8
"""Default step size when taking forward finite differences."""


def check_gradient(f, g, x):
    """Use finite differences to check an analytic gradient.

    Parameters
    ----------
    f : The function.
    g : The gradient function.
    x : The location to check the gradient.

    Returns
    -------
    The max absolute difference (infinity-norm) between the analytic
    and numerical gradients.

    """
    x = np.asarray(x)
    return np.max(g(x) - gradient(f, x))


def check_rand_gradient(f, g, x, s=_DEFAULT_STEP):
    """Check the directional derivative of an analytic gradient.
    
    Parameters
    ----------
    f : The function.
    g : The gradient function.
    x : The location to check the gradient.

    Returns
    -------
    The absolute difference between the analytic and numerical
    directional derivative.

    """
    x = np.asarray(x)
    v = _rand_direction(len(x), np.random)
    d_hat = directional_deriv(f, x, v, s)
    return abs(v @ g(x) - d_hat)


def gradient(f, x, s=_DEFAULT_STEP):
    """Approximate the gradient using forward finite differences.

    Parameters
    ----------
    f : The function.
    x : The point at which to approximate the gradient.
    s : Step size to take in each direction.

    Returns
    -------
    An approximate gradient.

    """
    x = np.asarray(x)
    n = len(x)
    e = np.eye(n)

    forw = np.zeros(n)
    for i in range(n):
        forw[i] = f(x + s*e[i])

    g = (forw - f(x)) / s
    return g


def directional_deriv(f, x, v, s=_DEFAULT_STEP):
    """Approximate the derivative of a function in a direction.

    Parameters
    ----------
    f : The function.
    x : The point at which to approximate the derivative.
    v : Vector representing the direction.
    s : Step size to take along the vector.

    Returns
    -------
    An approximate derivative (single scalar).

    """
    v = np.asarray(v)
    v = v / la.norm(v)
    return (f(x + s*v) - f(x)) / s


def hessian(f, x, s=_DEFAULT_STEP):
    """Approximate the Hessian using forward finite differences.

    Parameters
    ----------
    f : The function.
    x : The point at which to approximate the gradient.
    s : Step size to take in each direction.

    Returns
    -------
    An approximate Hessian.

    """
    x = np.asarray(x)
    n = len(x)
    e = s * np.eye(n)

    forw1 = np.zeros(n)
    forw2 = np.zeros((n, n))
    for i in range(n):
        forw1[i] = f(x + e[i])
        for j in range(i, n):
            forw2[i, j] = forw2[j, i] = f(x + e[i] + e[j])

    H = (forw2 - _colvec(forw1) - _rowvec(forw1) + f(x)) / s**2
    return H


def rosenbrock(p, a=1.0, b=100.0):
    """Rosenbrock's banana function."""
    x, y = p
    return (a - x)**2 + b * (y - x**2)**2


def rosenbrock_grad(p, a=1.0, b=100.0):
    """Rosenbrock's banana function's gradient."""
    x, y = p
    gx = - 2*(a - x) - 2*b * (y - x**2)* 2*x
    gy = 2*b * (y - x**2)
    return np.array([gx, gy])


def _rand_direction(dim, rand):
    """Return a random direction (unit length vector)."""
    direction = rand.normal(size=dim)
    return direction / la.norm(direction)


def _colvec(x):
    """Return 1D array as a column vector."""
    x = np.atleast_1d(x)
    return x[:, None]


def _rowvec(x):
    """Return 1D array as a row vector."""
    return _colvec(x).transpose()
