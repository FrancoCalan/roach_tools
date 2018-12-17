import numpy as np
import matplotlib.pyplot as plt

# init calanfigure
fig = plt.figure()

# create axis
ax = fig.add_subplot('111')
line = ax.plot([], [], lw=2)[0]
ax.set_xlim((0,9))
ax.set_ylim((0,81))

# plot axis
x = np.arange(10)

# show in script
for i in np.linspace(1,2,100):
    line.set_data(x, x**i)
    plt.pause(0.00001)
plt.show()
