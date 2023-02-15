import sys
import os

sys.path.append(os.getcwd())

from grpphati.results import Result
import numpy as np
import matplotlib.pyplot as plt

res = Result(barcode=[[0, 0.3], [0, 1], [0, 3], [0, np.inf], [0, np.inf]])
x_range = np.linspace(0, 4, 1000)
y_range = res.compute_betti_curve(x_range)
plt.plot(x_range, y_range)
plt.show()
