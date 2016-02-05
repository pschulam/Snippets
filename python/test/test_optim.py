"""Test optim.py module."""

from imp import reload
from time import sleep

import numpy as np

import optim
reload(optim)

np.random.seed(0)

n = 100
f = optim.rosenbrock
g = optim.rosenbrock_grad
X = np.random.normal(scale=2.0, size=(n, 2))

for i, x in enumerate(X):
    print('Starting example {}'.format(i + 1))

    d1 = optim.check_gradient(f, g, x)
    print('Max. difference in gradient is {:11.08f}'.format(d1))

    d2 = optim.check_rand_gradient(f, g, x)
    print('Max. difference along random direction is {:11.08f}'.format(d2))

    print()

    sleep(1)
