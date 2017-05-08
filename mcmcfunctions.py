#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May  7 22:52:26 2017

@author: ethan
"""

import numpy as np
import random as rand
import sys

def mcmc(n,likelihood,zbias,mubias,OMi,H0i,wi,omstep,H0step,wstep,filein,fileout,status):
    
    ###############Data manipulation###############
    
    if zbias == 'nobias':
        columnz = 0
    elif zbias == 'bias':
        columnz = 1
    
    if mubias == 'nobias':
        columnmu = 3
    elif mubias == 'bias':
        columnmu = 4
    
    z_obs,mu_obs = np.loadtxt(filein,usecols=[columnz,columnmu],unpack=True)
    
    rand.seed(7)
    
    
    ###############MCMC code (bias)###############
    
    omlist = [] #create empty list
    H0list = []
    wlist = []
    
    om_current = OMi #starting values
    H0_current = H0i
    w_current = wi
    
    omlist.append(om_current) #append first value to list
    H0list.append(H0_current)
    wlist.append(w_current)
    
    sig_tau = 0.2
    
    accept = 0
    log_like_proposed = 0
    accept_list = []
    
    print('Generating posterior')
    
    fout = open(fileout,'w')
    fout.write('#o_m \t H0 \t w \n')
    for i in range(0,n-1):
        #current position:
        if i == 0:
            log_like_current = likelihood(z_obs,mu_obs,sig_tau,om_current,H0_current,w_current)
        elif accept == 1:
            log_like_current = log_like_proposed
            
        om_proposed =  rand.gauss(om_current,omstep)
        while om_proposed >= 1 or om_proposed <= 0:         #keeps Omega_matter in (0,1) 
            om_proposed =  rand.gauss(om_current,omstep)    #for numerical reasons
        H0_proposed =  rand.gauss(H0_current,H0step)
        while H0_proposed >= 200 or H0_proposed <= 10:
            H0_proposed =  rand.gauss(H0_current,H0step)
        w_proposed =  rand.gauss(w_current,wstep)
        while w_proposed >= 4 or w_proposed <= -6:
            w_proposed =  rand.gauss(w_current,wstep)
            
        #proposed position:
        log_like_proposed = likelihood(z_obs,mu_obs,sig_tau,om_proposed,H0_proposed,w_proposed)
        
        #decision:
        r = np.exp(log_like_proposed - log_like_current)
        
        MC = rand.random()
        
        if r < 1 and MC > r:
            omlist.append(om_current)
            H0list.append(H0_current)
            wlist.append(w_current)
            accept = 0
        else:
            omlist.append(om_proposed)
            H0list.append(H0_proposed)
            wlist.append(w_proposed)
            accept = 1
            
        om_current = omlist[i+1]
        H0_current = H0list[i+1]
        w_current = wlist[i+1]
        accept_list.append(accept)
        
        fout.write(str(om_current)+'\t'+str(H0_current)+'\t'+str(w_current)+'\n')
        
        if status==True:
            inc100 = np.int64(i/(n-2)*100)
            inc50 = np.int64(i/(n-2)*50)
            sys.stdout.write('\r')
            sys.stdout.write('[' + '#'*inc50 + ' '*(50-inc50) + ']' + str(inc100) + '%')
            sys.stdout.flush()
            
    fout.close()
    print('\ndone')


def mcmc_spec(n,likelihood,mubias,OMi,H0i,wi,omstep,H0step,wstep,filein,fileout,status):
    
    ###############Data manipulation###############
    
    if mubias == 'nobias':
        columnmu = 3
    elif mubias == 'bias':
        columnmu = 4
    
    z_obs,z_obs2,mu_obs = np.loadtxt(filein,usecols=[0,1,columnmu],unpack=True)
    
    rand.seed(7)
    
    
    ###############MCMC code (bias)###############
    
    omlist = [] #create empty list
    H0list = []
    wlist = []
    
    om_current = OMi #starting values
    H0_current = H0i
    w_current = wi
    
    omlist.append(om_current) #append first value to list
    H0list.append(H0_current)
    wlist.append(w_current)
    
    P_gamma = 0.91
    P_tau = 0.95
    offset = 2
    sig_tau1 = 0.2
    sig_tau2 = 1.5
    
    accept = 0
    log_like_proposed = 0
    accept_list = []
    
    print('Generating posterior')
    
    fout = open(fileout,'w')
    fout.write('#o_m \t H0 \t w \n')
    for i in range(0,n-1):
        #current position:
        if i == 0:
            log_like_current = likelihood(z_obs,z_obs2,mu_obs,sig_tau1,sig_tau2,
                                          P_gamma,P_tau,offset,om_current,H0_current,w_current)
        elif accept == 1:
            log_like_current = log_like_proposed
            
        om_proposed =  rand.gauss(om_current,omstep)
        while om_proposed >= 1 or om_proposed <= 0:         #keeps Omega_matter in (0,1) 
            om_proposed =  rand.gauss(om_current,omstep)    #for numerical reasons
        H0_proposed =  rand.gauss(H0_current,H0step)
        while H0_proposed >= 200 or H0_proposed <= 10:
            H0_proposed =  rand.gauss(H0_current,H0step)
        w_proposed =  rand.gauss(w_current,wstep)
        while w_proposed >= 4 or w_proposed <= -6:
            w_proposed =  rand.gauss(w_current,wstep)
            
        #proposed position:
        log_like_proposed = likelihood(z_obs,z_obs2,mu_obs,sig_tau1,sig_tau2,
                                       P_gamma,P_tau,offset,om_proposed,H0_proposed,w_proposed)
        
        #decision:
        r = np.exp(log_like_proposed - log_like_current)
        
        MC = rand.random()
        
        if r < 1 and MC > r:
            omlist.append(om_current)
            H0list.append(H0_current)
            wlist.append(w_current)
            accept = 0
        else:
            omlist.append(om_proposed)
            H0list.append(H0_proposed)
            wlist.append(w_proposed)
            accept = 1
            
        om_current = omlist[i+1]
        H0_current = H0list[i+1]
        w_current = wlist[i+1]
        accept_list.append(accept)
        
        fout.write(str(om_current)+'\t'+str(H0_current)+'\t'+str(w_current)+'\n')
        
        if status==True:
            inc100 = np.int64(i/(n-2)*100)
            inc50 = np.int64(i/(n-2)*50)
            sys.stdout.write('\r')
            sys.stdout.write('[' + '#'*inc50 + ' '*(50-inc50) + ']' + str(inc100) + '%')
            sys.stdout.flush()
            
    fout.close()
    print('\ndone')