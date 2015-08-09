# -*- coding: utf-8 -*-
#
from scipy import *
from scipy.linalg import *
from scipy.fftpack import fft,ifft,fft2,ifft2,fftshift
from pylab import *
from scipy.signal import *
from mpl_toolkits.mplot3d import Axes3D
import codecs


# 4*(x-20)^2+5*(y-20)^2
n=300
x,y=meshgrid(arange(n+1),arange(n+1))
x=(x+0.-n/2)/n*3
y=(y+0.-n/2)/n*2+0.8
phi=100*(y-x**2)**2+(1-x)**2


pp=raw_input("Input step scaling factor(0.45 recommended):")
xi=-1.2
yi=1
loop=6000
Gx=-400*xi*(yi-xi**2)-2*(1-xi)
Gy=200*(yi-xi**2)
p=1/sqrt(Gx**2+Gy**2)*float(pp)


logx=[]
logy=[]

logx.append(xi)
logy.append(yi)

##
for ii in range(loop):
	Gx=-400*xi*(yi-xi**2)-2*(1-xi)
	Gy=200*(yi-xi**2)
	xi=xi-Gx*p
	yi=yi-Gy*p
	logx.append(xi)
	logy.append(yi)
	print(xi,yi)


#figure(1).clf()
#fig=Axes3D(figure(1))
#fig.plot_wireframe(x,y,phi)
#axis([-0.8,0.8,-0.8,0.8])
#fig.set_xlabel("x")
#fig.set_ylabel("y")
#fig.set_zlabel("phi")
#figure(1).show()

print(loop)

figure(2).clf()
interval=arange(0,100,5)
contour(x,y,phi,interval)
plot(logx,logy,"k-h", markersize=5)
colorbar()
figure(2).show()
