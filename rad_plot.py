def plotdens(iend,istart=0,skip=1):
	figure()
	for i in arange(istart,iend+1)[::skip]:
		dat=loadtxt('gasdens.ascii_rad.%d.dat' % i)
		loglog(dat[:,0],dat[:,1])


def plotvrad(iend,istart=0,skip=1):
	figure()
	for i in arange(istart,iend+1)[::skip]:
		dat = loadtxt('gasvrad.ascii_rad.%d.dat' % i)
		semilogx(dat[:,0],dat[:,1])

def plotmdot(iend,istart=0,skip=1,logy=False):
	figure()
	for i in arange(istart,iend+1)[::skip]:
		dens = loadtxt('gasdens.ascii_rad.%d.dat' % i)
		vrad = loadtxt('gasvrad.ascii_rad.%d.dat' % i)[:,1]
		lam = 2*pi*dens[:,0]*dens[:,1]
		semilogx(dens[:,0],-lam*vrad)
	
	if logy:
		yscale('symlog',linthreshy=1e-10)


def plotall(iend,istart=0,skip=1,logx=True,logy=True):
	rho0 = loadtxt('gasdens.ascii_rad.1.dat')[:,1]

	fig,axes=subplots(2,2,sharex='col')
	
	for i in arange(istart,iend+1)[::skip]:
		rho = loadtxt('gasdens.ascii_rad.%d.dat' % i)
		vrad = loadtxt('gasvrad.ascii_rad.%d.dat' % i)
		axes[0,0].plot(rho[:,0],rho[:,1])
		axes[1,1].plot(vrad[:,0],vrad[:,1])
		axes[0,0].set_ylabel('Sigma')
		axes[1,1].set_ylabel('vr')
		axes[1,1].set_xlabel('r')
		axes[0,1].plot(rho[:,0],-2*pi*rho[:,0]*rho[:,1]*vrad[:,1])
		axes[0,1].set_ylabel('Mdot')
		axes[1,0].plot(rho[:,0], (rho[:,1]-rho0)/rho0)
		axes[1,0].set_xlabel('r')
		axes[1,0].set_ylabel('$\\frac{\\Sigma - \\Sigma_0}{\\Sigma_0}$')
		if logx:
			for ax in axes.flatten():
				ax.set_xscale('log')
		if logy:
			axes[0,0].set_yscale('log')

		
	fig.canvas.draw()

def plotorbit(dt=6.28):
	orb = loadtxt('orbit1.dat')
	t = orb[:,0]*dt
	ecc = orb[:,1]
	a = orb[:,2]
	
	fig,ax = subplots(2,2)
	ax[0,0].semilogx(t,a)
	ax[0,1].loglog(t,ecc)

	fig.canvas.draw()


def plot_scaled_dens(iend,rp=5.2,h=.05,istart=0,skip=1,ylim=1.5,scale_r=True,mp=1e-3):

	rh = (mp/3.)**(1./3)

	dens0 = loadtxt('gasdens.ascii_rad.0.dat')

	r = dens0[:,0]
	
	sig0 = dens0[r>=rp,1][0]

	fig = figure();
	ax = fig.add_subplot(111)

	ax.set_xlabel('$ \\frac{r -r_p}{H}$',fontsize=20)	
	ax.set_ylabel('$\\frac{\\Sigma}{\\Sigma_0}$',fontsize=20)

	nums = arange(istart,iend+1)[::skip]

	rho = zeros((len(r),len(nums)))
	for i,j in enumerate(nums):
		rho[:,i] = loadtxt('gasdens.ascii_rad.{0:d}.dat'.format(j))[:,1]/sig0

	H = .05*rp
	x = (r-rp)/H

	if scale_r:
		ax.plot(x,rho)
		ax.axvline(rh/h,color='k',linewidth=3)
		ax.axvline(-rh/h,color='k',linewidth=3)
		ax.set_xlim(-10,10)
		ax.set_ylim(0,ylim)
	else:
		ax.set_xlabel('$\\frac{r}{r_p}$',fontsize=20)
		ax.plot(r/rp,rho)
		ax.axvline(1+rh,color='k',linewidth=3)
		ax.axvline(1-rh,color='k',linewidth=3)
		ax.set_xlim(.3,3)
		ax.set_ylim(0,ylim)
	ax.minorticks_on()
	fig.canvas.draw()

	return x,rho
		
def gap_function(r,rp=5.2,h=.05,alpha=.001,q=1e-3):
	if type(r) == float:
		r = array([r])
	M = 1/h
	H = h*r
	delta = array([ max(H_val,abs(x-rp)) for H_val,x in zip(H,r)])
	fac = -2./9 * q*q * M*M/alpha * (rp/delta)**3
	return exp(fac)


def plot2d(num,ax=None,cartesian=True,rlim=8):
	nr,nphi = loadtxt('dims.dat')[-2:]
	r = loadtxt('used_rad.dat')
	r =(r[:-1] + r[1:])/2.
	phi = linspace(-pi,pi,nphi)

	pp,rr = meshgrid(phi,r)
	xx,yy = rr*cos(pp), rr*sin(pp)


	if ax == None:
		fig=figure();
		ax=fig.add_subplot(111)

	rho = log10(fromfile('gasdens{0:d}.dat'.format(num),dtype='float64').reshape(nr,nphi))
	
	if cartesian:
		line2d=ax.pcolormesh(xx,yy,rho,cmap='cubehelix',shading='gouraud')
		ax.set_xlim(-rlim,rlim); ax.set_ylim(-rlim,rlim);
		colorbar(line2d,ax=ax)
	else:
		line2d=ax.imshow(rho,origin='lower',cmap='cubehelix',aspect='auto',extent=(-pi,pi,r[0],r[-1]))
		colorbar(line2d,ax=ax)
	return; 

def animate2d(iend,istart=0,skip=1,cartesian=True,rlim=8,dt=6.28,ndt=10,rp=5.2,nloops=2):
	dt *= ndt
	p_rp = 6.28 * rp**(1.5)
	nr,nphi = loadtxt('dims.dat')[-2:]
	r = loadtxt('used_rad.dat')
	r =(r[:-1] + r[1:])/2.
	phi = linspace(-pi,pi,nphi)

	pp,rr = meshgrid(phi,r)
	xx,yy = rr*cos(pp), rr*sin(pp)
	
	nums = arange(istart,iend+1)[::skip]
	rho = zeros((nr,len(nums)))	
	

	rho = [log10(fromfile('gasdens{0:d}.dat'.format(i),dtype='float64').reshape(nr,nphi)) for i in nums]
	
	fig=figure();
	ax=fig.add_subplot(111)
	if cartesian:
		line2d = ax.pcolormesh(xx,yy,rho[0],cmap='cubehelix',shading='gouraud')
		ax.set_xlim(-rlim,rlim)
		ax.set_ylim(-rlim,rlim)
	else:
		line2d = ax.imshow(rho[0],cmap='cubehelix',origin='lower',aspect='auto',extent=(-pi,pi,r[0],r[-1]))
	
	for nl in range(nloops):
		for d,t in zip(rho,nums):
			if cartesian: 
				line2d.set_array(d.ravel())
			else:
				line2d.set_data(d)
			ax.set_title('t = %.2f,\t t = %.2f $P_{orb}$' % (t*dt,t*dt/p_rp))
			fig.canvas.draw()

	return












	
