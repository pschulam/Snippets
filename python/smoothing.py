"""Nonparametric regression."""

import numpy as np
import scipy.linalg as la

__all__ = ['KernelSmoother', 'box_kernel', 'gaussian_kernel']


class KernelSmoother:
    """Estimate a smooth function given noisy samples."""

    def __init__(self, x, y, kernel, bandwidth=1.0, degree=1):
        self._x = np.array(x)
        self._y = np.array(y)
        self._h = bandwidth
        self._d = degree
        self._kernel = kernel

    @property
    def bandwidth(self):
        """The smoothing bandwidth of the estimator."""
        return self._h

    @property
    def degree(self):
        """The degree of the local polynomials."""
        return self._d

    def __call__(self, xnew):
        """Compute the value of the estimated function."""
        xnew = np.atleast_1d(xnew)
        numx = len(xnew)
        ynew = np.zeros(numx)

        for i in range(numx):
            X = self._design(xnew[i])
            w = self._weights(xnew[i])
            ynew[i] = _weighted_least_squares(self._y, X, w)[0]

        return ynew

    def _design(self, x):
        """Compute the centered polynomial design matrix for an input."""
        return _polynomial(self._x - x, self._d)

    def _weights(self, x):
        """Compute the weights of the training data for an input."""
        z = (self._x - x) / self._h
        return self._kernel(z) / self._h


def smooth(x, y, xnew, kernel, bandwidth, degree):
    """Estimate a smooth function at input using noisy measurements.

    Parameters
    ----------
    x : Locations of observed measurements.
    y : Values of observed measurements.
    xnew : Locations of estimated function values.
    kernel : Function to compute weights based on distance.
    bandwidth : Controls the flexibility of the estimate.
    degree : The degree of the local polynomials.

    Returns
    -------
    An array of estimated values.

    """
    yhat = KernelSmoother(x, y, kernel, bandwidth, degree)
    return yhat(xnew)


def estimate_bandwidth(x, y, kernel, bandwidths, degree):
    """Choose the best bandwidth using LOO cross validation.

    Parameters
    ----------
    x : Locations of observed measurements.
    y : Values of observed measurements.
    kernel : Function to compute weights based on distance.
    bandwidths : The bandwidth options.
    degree : The degree of the local polynomials.

    Returns
    -------
    The bandwidth minimizing the LOO cross validation mean squared error.

    """
    mse = np.zeros(len(bandwidths))

    for i, bandwidth in enumerate(bandwidths):
        yhat = loo_estimates(x, y, kernel, bandwidth, degree)
        mse[i] = np.mean((y - yhat)**2)

    return bandwidths[np.argmin(mse)]


def loo_estimates(x, y, kernel, bandwidth, degree):
    """Compute leave-one-out estimates of the data.

    Parameters
    ----------
    x : Locations of observed measurements.
    y : Values of observed measurements.
    kernel : Function to compute weights based on distance.
    bandwidth : Controls the flexibility of the estimate.
    degree : The degree of the local polynomials.

    Returns
    -------
    Estimates of each observation computed using all other observations.

    """
    numx = len(x)
    mask = np.arange(numx)
    yhat = np.zeros(numx)

    def smoother(x, y, xnew):
        """Smooth using the enclosed parameters."""
        return smooth(x, y, xnew, kernel, bandwidth, degree)

    for i in range(numx):
        holdout = mask == i
        yhat[i] = smoother(x[~holdout], y[~holdout], x[holdout])

    return yhat


def box_kernel(x):
    """Compute the box kernel."""
    return np.where(np.abs(x) < 1.0, 0.5, 0.0)


def gaussian_kernel(x):
    """Compute the Gaussian kernel."""
    return np.exp(-x**2)


def _weighted_least_squares(y, X, w):
    """Compute the weighted least squares coefficient estimate."""
    W = np.diag(w)
    A = X.T @ W @ X
    b = X.T @ W @ y
    return la.solve(A, b)


def _polynomial(x, degree):
    """Create a polynomial design matrix."""
    x = np.atleast_1d(x)
    return np.array([x**p for p in range(degree + 1)]).T
