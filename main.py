from controller import *
from mask import Mask
import matplotlib.pyplot as plt

if __name__ == "__main__":
    c = Controller()
    m = Mask(c.gdf)

    m.visualize()