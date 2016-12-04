# -*- coding: utf-8 -*-
"""
Copyright (c) 2015-2016 Thomas Mertz

THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR IMPLIED 
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF 
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, 
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE 
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from __future__ import division
import numpy as np
import math
import os, sys

pyVERSION = float(sys.version[:3])

if pyVERSION >= 3:
	xrange = range

__version__ = '0.1'
factorial = math.factorial

def sign(x):
	return 1 if x>=0 else -1
	#return x / abs(x)

def pfaff(A):
	
	pass
	assert len(A.shape) == 2
	assert A.shape[0] == A.shape[1]
	
	dim = A.shape[0]
	
	if dim % 2 != 0:
		return 0
	
	pf_A = 0
	
	dims = [dim-i for i in xrange(0,dim)]
	
	#for p in np.ndindex(*((dim,)*dim)):
	for n in np.ndindex(*dims):
		ind = range(dim)
		p = []
		
		for i in xrange(dim):
			p.append(ind.pop(n[i]))
			
		N = 0
		for i in xrange(dim):
			for j in xrange(i+1,dim):
				if p[i] > p[j]:
					N += 1
				else:
					pass
		sgn_p = (-1)**N
		
		# beware: mathematical indices
		i_odd = range(0,dim,2)
		i_even = range(1,dim+1,2)
		
		p1 = np.asarray(p)
		
		prod_p = A[p1[i_odd],p1[i_even]].prod()
		
		#print(prod_p)
		if False:
			if prod_p != 0:
				print(p)
				
		if False:
			print((p,sgn_p))
		
		pf_A += sgn_p * prod_p
	
	pf_A /= 2**(dim/2) * factorial(dim/2)
	
	return pf_A
	
def rand_skew_symm_mat(dim=2,cmplx=False):
	import numpy.random as rnd
	
	A = rnd.random([dim,dim])
	if cmplx:
		B = rnd.random([dim,dim])
		
		A = A + 1j * B
	
	return A - A.transpose()
	
def test_pfaff(dim=2,num=10,accuracy=1e-5):
	part = "-"*10
	log_txt = "Testing...\n\n{3}\n\ndim {0}\nnum {1}\nacc {2}\n\n{3}\n".format(dim,num,accuracy,part)
	print(log_txt)
	for i in xrange(num):
		A = rand_skew_symm_mat(dim,cmplx=True)
		if abs(np.linalg.det(A) - pfaff(A)**2) > accuracy:
			print("Test failed!")
			return 1
	print("Test successful!")
	return 0
	
def linear_interp(f,x,x_eval):
	# return the function value f(x_eval) by connecting the two points given

	assert len(f) == len(x) == 2
	assert x[0] != x[1]
	m = (f[1] - f[0]) / (x[1] - x[0])
	
	return x[0] + m * (x_eval - x[0])
	
def ishermitian(A):
	return True if (A == A.transpose().conjugate()).all() else False
	
def poly_interp(f,x,x_eval):
	pass
	
def format_time(t, format_spec='dhms'):
	"""
	Return a formatted time string describing the duration of 
	the input in seconds in terms of days,hours,minutes and seconds.
	"""
	if format_spec == '':
		sb, mb, hb, db = True, True, True, True
	else:
		sb = 's' in format_spec
		mb = 'm' in format_spec
		hb = 'h' in format_spec
		db = 'd' in format_spec
	
	t = round(t, 2)
	if t >= 60 and (mb or hb or db):
		m = t // 60
		s = t - m*60
		if m >= 60 and (hb or db):
			h = m // 60
			m = m - h*60
			if h >= 24 and db:
				d = h // 24
				h = h - d*24
			else:
				d = 0
		else:
			h,d = 0,0
	else:
		s = t
		m,h,d = 0,0,0
	
	time_str = ""
	#if format_spec == 's':
	#	time_str += "{}s".format(t)
	if format_spec == '':
		if not d == 0:
			db, hb, mb = True, True, True
		elif not h == 0:
			db = False
			hb, mb = True, True
		elif not m == 0:
			db, hb = False, False
			mb = True
		else:
			db, hb, mb = False, False, False
		#db = not d == 0
		#hb = not h == 0
		#mb = not m == 0
		#sb = not s == 0
		sb = True
	if not (db or hb or mb or sb):
		sb = True
		
	if db:
		time_str += "{:.0f}d ".format(d)
	if hb:
		time_str += "{: =2.0f}h ".format(h)
	if mb:
		time_str += "{: =2.0f}m ".format(m)
	if sb:
		"""
		if not (db or hb or mb):
			if s < 0.1:
				if s > 0:
					digits = abs(math.floor(math.log(s) / math.log(10)))
					time_str += "{{: =4.{0}f}}s".format(digits).format(s)
				else:
					time_str += "{}s".format(s)

		else:
			time_str += "{: =4.1f}s".format(s)
		"""
		time_str += "{: =4.1f}s".format(s)
	#return "{}d {}h {}m {}s".format(d,h,m,s)
	return time_str

def assert_dir(path):
	if not os.access(path, os.F_OK):
		os.mkdir(path)
		
def isiterable(var):
	return hasattr(var, "__iter__")