import numpy as np

from scipy.interpolate import splev
from matplotlib import pyplot as plt


def evaluate(x, knots, degree):
    '''Evaluate all B-spline bases.

    x : The points at which to evaluate the bases.
    knots : The knots defining the B-spline.
    degree : The degree of the polynomial pieces.

    returns : A matrix with a row for each input and a column for each
    basis.

    '''
    c = np.eye(num_bases(knots, degree))
    return np.array(splev(x, (knots, c, degree))).T


def num_bases(knots, degree):
    '''The dimension of the implied B-spline space.

    knots : The knots defining the B-spline.
    degree : The degree of the polynomial pieces.

    returns : The number of bases spanning the B-splines.

    '''
    return len(knots) - degree - 1


def uniform_knots(low, high, num_bases, degree):
    '''Create the standard uniform B-spline knots.

    low : The lower bound of the domain.
    high : The upper bound of the domain.
    num_bases : The desired number of bases.
    degree : The degree of the polynomial pieces.

    returns : An array of knots.

    '''
    num_knots = num_bases + degree + 1
    num_interior = num_knots - 2 * (degree + 1)
    
    knots = np.linspace(low, high, num_interior + 2).tolist()
    knots = degree * [low] + knots + degree * [high]
    return np.array(knots)


def pspline_penalty(knots, degree, order=1):
    '''Construct a P-spline penalty matrix for regression.

    knots : The knots defining the B-spline.
    degree : The degree of the polynomial pieces.
    order : The order of differences to take between coefficients.

    returns : A symmetric penalty matrix for B-spline coefficients.

    '''
    D = np.eye(num_bases(knots, degree))
    D = np.diff(D, order)
    return np.dot(D, D.T)


class BSplineBasis:
    '''Object interface to B-splines.

    '''
    def __init__(self, low, high, num_bases, degree):
        self.low = low
        self.high = high
        self.num_bases = num_bases
        self.degree = degree
        self.knots = uniform_knots(low, high, num_bases, degree)

    def evaluate(self, x):
        return evaluate(x, self.knots, self.degree)

    def pspline_penalty(self, order=1):
        return pspline_penalty(self.knots, self.degree, order=order)

    def plot(self):
        x = np.linspace(self.low, self.high, 200)
        B = self.evaluate(x)

        for y in B.T:
            plt.plot(x, y)
