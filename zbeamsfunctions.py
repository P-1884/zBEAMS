# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 12:06:21 2017

@author: ethan
"""

import numpy as np
from scipy.integrate import quad
from scipy import interpolate


def mu_w(z,OM,H0,w):
    def H(z,OM,H0,w):
        if w==-1:
            #Eqn 2.3 of zBEAMS paper, assuming O_k = 0 and w=-1.
            return H0*np.sqrt(OM*(1+z)**3+(1-OM))
        else:
            #Eqn 2.3 of zBEAMS paper, assuming O_k = 0.
            return H0*np.sqrt(OM*(1+z)**3+(1-OM)*(1+z)**(3*(w+1)))
            
    def dL(z,OM,H0,w):
        c=2.99792e5 #c in km/s
        #Luminosity distance for a flat universe (O_k=0) - see here https://en.wikipedia.org/wiki/Distance_measure
        return (1+z)*quad(lambda x:c/H(x,OM,H0,w),0,z)[0]
    #NOTE, THIS SEEMS TO BE IN THE WRONG UNITS - SHOULD BE IN Mpc (See Eqn 2.1 of zBEAMS)?
    return 5*np.log10(dL(z,OM,H0,w))+25


def likelihood_phot(z,muo,sigmuo,OM,H0,w,zo,sigzo,b):
    def mu_interp(z,OM,H0,w):
        def H(z,OM,H0,w):
            if w==-1:
                return H0*np.sqrt(OM*(1+z)**3+(1-OM))
            else:
                return H0*np.sqrt(OM*(1+z)**3+(1-OM)*(1+z)**(3*(w+1)))
                
        def dL(z,OM,H0,w):
            c=2.99792e5
            return (1+z)*quad(lambda x:c/H(x,OM,H0,w),0,z)[0]
            
        def mu_w(z,OM,H0,w):
            return 5*np.log10(dL(z,OM,H0,w))+25
        #The purpose of np.vectorize is to transform functions which are not numpy-aware (e.g. take floats
        #as input and return floats as output) into functions that can operate on (and return) numpy arrays.        
        mu_w_vectorized = np.vectorize(mu_w)
                
        z_spl = np.linspace(np.min(z),np.max(z),50)
        mu_spl = mu_w_vectorized(z_spl,OM,H0,w)
        tck = interpolate.splrep(z_spl, mu_spl)
        mu_int = interpolate.splev(z, tck)
        return mu_int
    
    mu_theory = mu_interp(z,OM,H0,w)
    chi2 = ((muo-mu_theory)/sigmuo)**2
    chi3 = ((z-zo)/sigzo)**2
    chi4 = np.log(z) - b*z
    likeli = -0.5*sum(chi2)
    prior = -0.5*sum(chi3)
    priorz = sum(chi4)
    return likeli + prior + priorz
        

def likelihood_spec(z,z2,muo,sigmuo,sigmuo2,P_gamma,P_tau,offset,OM,H0,w):
    def mu_interp(z,OM,H0,w):
        def H(z,OM,H0,w):
            if w==-1:
                return H0*np.sqrt(OM*(1+z)**3+(1-OM))
            else:
                return H0*np.sqrt(OM*(1+z)**3+(1-OM)*(1+z)**(3*(w+1)))
                
        def dL(z,OM,H0,w):
            c=2.99792e5
            return (1+z)*quad(lambda x:c/H(x,OM,H0,w),0,z)[0]
            
        def mu_w(z,OM,H0,w):
            return 5*np.log10(dL(z,OM,H0,w))+25
                
        mu_w_vectorized = np.vectorize(mu_w)
                
        z_spl = np.linspace(np.min(z),np.max(z),50)
        mu_spl = mu_w_vectorized(z_spl,OM,H0,w)
        tck = interpolate.splrep(z_spl, mu_spl)
        mu_int = interpolate.splev(z, tck)
        return mu_int
    
    mu_theory1 = mu_interp(z,OM,H0,w)
    mu_theory2 = mu_interp(z2,OM,H0,w)
    chi2_1 = ((muo-mu_theory1)/sigmuo)**2
    chi2_2 = ((muo-mu_theory2)/sigmuo)**2
    chi2_3 = ((muo-mu_theory1)/sigmuo2)**2
    chi2_4 = ((muo-mu_theory2)/sigmuo2)**2
    
    L1 = P_tau*P_gamma*((1/np.sqrt(2*np.pi*sigmuo**2))*np.exp(-chi2_1/2))
    L2 = P_tau*(1-P_gamma)*((1/np.sqrt(2*np.pi*sigmuo**2))*np.exp(-chi2_2/2))
    L3 = (1-P_tau)*(P_gamma)*((1/np.sqrt(2*np.pi*sigmuo2**2))*np.exp(-chi2_3/2))
    L4 = (1-P_tau)*(1-P_gamma)*((1/np.sqrt(2*np.pi*sigmuo2**2))*np.exp(-chi2_4/2))
    return np.sum(np.log(L1 + L2 + L3 + L4))


def likelihood(z,muo,sigmuo,OM,H0,w):
    print([np.shape(elem) for elem in [z,muo,sigmuo,OM,H0,w]])
    def mu_interp(z,OM,H0,w):
        def H(z,OM,H0,w):
            if w==-1:
                return H0*np.sqrt(OM*(1+z)**3+(1-OM))
            else:
                return H0*np.sqrt(OM*(1+z)**3+(1-OM)*(1+z)**(3*(w+1)))
                
        def dL(z,OM,H0,w):
            c=2.99792e5
            return (1+z)*quad(lambda x:c/H(x,OM,H0,w),0,z)[0]
            
        def mu_w(z,OM,H0,w):
            return 5*np.log10(dL(z,OM,H0,w))+25
                
        mu_w_vectorized = np.vectorize(mu_w)  # <numpy.vectorize object at 0x12e74be20>
                
        z_spl = np.linspace(np.min(z),np.max(z),50) # numpy array between min(z) and max(z)
        mu_spl = mu_w_vectorized(z_spl,OM,H0,w) # numpy array of mu values
        tck = interpolate.splrep(z_spl, mu_spl) # Finds a cubic spline
        mu_int = interpolate.splev(z, tck) # Evaluates the cubic spline, for provided z values
        return mu_int
    
    mu_theory = mu_interp(z,OM,H0,w)
    chi2 = ((muo-mu_theory)/sigmuo)**2
    likeli = -0.5*sum(chi2)
    return likeli


def contour(chain,p,**kwargs):
    def findconfidence(H):
        H2 = H.ravel()
        H2 = np.sort(H2)
        
        #Cut out the very low end
        #H2 = H2[H2>100]
        
        #Loop through this flattened array until we find the value in the bin 
        #which contains 95% of the points
        tot = sum(H2)
        tot95=0
        tot68=0
        
        #Changed this to 68% and 30% C.I
        for i in range(len(H2)):
            tot95 += H2[i]
            if tot95 >= 0.05*tot:
                N95 = H2[i]
                #print i
                break
            
        for i in range(len(H2)):
            tot68 += H2[i]
            if tot68>=0.32*tot:
                N68 = H2[i]
                break   
        return max(H2),N95,N68
    
    binsize=50
    H, xedges, yedges = np.histogram2d(chain[:,p[0]],chain[:,p[1]], bins=(binsize,binsize))
    
    x=[]
    y=[]
    z=[]
    for i in range(len(xedges[:-1])):
        for j in range(len(yedges[:-1])):
            x.append(xedges[:-1][i])
            y.append(yedges[:-1][j])
            z.append(H[i, j])

    if 'smooth' in kwargs:
        SMOOTH=True
        smth=kwargs['smooth']
        if smth==0:
            SMOOTH=False
    else:
        SMOOTH=True
        smth=10e5
    if SMOOTH:
        sz=50
        spl = interpolate.bisplrep(x, y, z,  s=smth)
        X = np.linspace(min(xedges[:-1]), max(xedges[:-1]), sz)
        Y = np.linspace(min(yedges[:-1]), max(yedges[:-1]), sz)
        Z = interpolate.bisplev(X, Y, spl)
    else:
        X=xedges[:-1]
        Y=yedges[:-1]
        Z=H
    
    #I think this is the weird thing I have to do to make the contours work properly
    X1=np.zeros([len(X), len(X)])
    Y1=np.zeros([len(X), len(X)])
    for i in range(len(X)):
        X1[ :, i]=X
        Y1[i, :]=Y
    X=X1
    Y=Y1
    
    N100,N95,N68 = findconfidence(Z)
    
    return N100,N95,N68,X,Y,Z
