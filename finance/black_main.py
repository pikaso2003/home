import numpy as np
import matplotlib.pyplot as plt
from financial_module import black
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

mklist = ['pink', 'darkviolet', 'slategrey', 'moccasin', 'olivedrab', 'goldenrod',
          'dodgerblue', 'coral', 'yellowgreen', 'skyblue', 'crimson']

F_0 = 100
vol = np.arange(0.05, 0.5, 0.025)
strike = np.arange(50., 151., 1)
expiry = np.arange(0., 10.6, 0.1)
strike, expiry = np.meshgrid(strike, expiry)
isCall = True


def pricer(F_0, strike, expiry, vol, isCall):
	ret = np.zeros(strike.shape)
	for i in range(ret.shape[0]):
		for j in range(ret.shape[1]):
			ret[i, j] = black.black(F_0, strike[i, j], expiry[i, j], vol, isCall)
	return ret


def update_plot(i, fig, ax, im, vol):
	ax.clear()
	ax = Axes3D(fig)
	ax.set_xlim([49.5, 150.5])
	ax.set_xlabel('Strike Price')
	ax.set_ylim([0., 11.])
	ax.set_ylabel('Maturity (yr)')
	ax.set_zlim([0., 80.])
	ax.set_zlabel('Price')
	vol_i = vol[i]
	if len(im) > 0:
		im[0].remove()
		im.pop()
	l = ax.plot_wireframe(strike, expiry, pricer(F_0, strike, expiry, vol_i, isCall), rstride=2, cstride=2,
	                      color=mklist[10])
	# 100,6,100
	ax.text(100, 6, 100, 'vol : %1.3f' % vol_i)
	im.append(l)


im = []
fig = plt.figure(1)
ax = Axes3D(fig)
ax.set_xlim([49.5, 150.5])
ax.set_xlabel('Strike Price')
ax.set_ylim([0., 11.])
ax.set_ylabel('Maturity (yr)')
ax.set_zlim([0., 80.])
ax.set_zlabel('Price')
ani = animation.FuncAnimation(fig, update_plot, fargs=(fig, ax, im, vol), frames=len(vol))
ani.save('black.gif', writer='imagemagick', fps=1)
plt.show()
