"""Tools for optimization."""
import numpy as np
import scipy.linalg as la


def check_grad(f, g, x, delta=1e-5, tol=1e-5, random=False):
    """Use finite differences to check a analytic gradient.

    Parameters
    ----------
    f : The function.
    g : The gradient function.
    x : The location to check the gradient.
    random : Should we check a random direction? Or each individually?

    Returns
    -------
    True if the difference between the numerical and analytic gradient
    is below the given threshold.

    """
    if random:
        directions = [_rand_direction(len(x), np.random)]
    else:
        directions = np.eye(len(x))

    for direction in directions:
        g_analytic = g(x)
        g_numerical = (f(x + delta * direction) - f(x)) / delta

        if la.norm(g_numerical - g_analytic) > tol:
            return False

    return True


def _rand_direction(dim, rand):
    """Return a random direction (unit length vector)."""
    direction = rand.normal(size=dim)
    return direction / la.norm(direction)
