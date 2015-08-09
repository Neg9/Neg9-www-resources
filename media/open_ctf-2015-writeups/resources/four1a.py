#!/usr/bin/python3
"""
Sign Fasterer or Fuck RSA with x primes
by Javantea
Aug 8, 2015

Any RSA implementation with more than 2 primes is very fucked.
This uses x primes.

The main efficiency is to make d very small.
By making d small, you are doing pow(ct, d, N) to sign/decrypt.

The thing that makes this script much more complex (and 2x faster) is the CRT with x primes. Who does that? I do.

"""

import Crypto.Util.number
import time
import fractions

class fuckedRSA:
	def __init__(self, p, e):
		#self.e = e
		d_test = 37
		while d_test < 10000:
			self.p = p
			phi = 1
			for x in p:
				phi *= (x-1)
			#next x
			self.e = Crypto.Util.number.inverse(d_test, phi)
			self.N = 1
			for x in p:
				self.N *= x
			#next x
			self.d = Crypto.Util.number.inverse(self.e, phi)
			print("d = ", self.d)
			if self.d > 1: break
			d_test += 2
		#loop
		self.dp = [self.d % (x-1) for x in p]
		
		p_i = self.p[0]
		self.q_inv = [0]
		self.p_i_precomp = [self.p[0]]
		for i in range(1, len(self.p)):
			q_i = self.p[i]
			self.q_inv.append(Crypto.Util.number.inverse(q_i, p_i))
			p_i *= q_i
			self.p_i_precomp.append(p_i)
		#next i
	
	def decrypt(self, ct):
		
		#d_P = d % (p-1)
		#d_Q = d % (q-1)  
		#d_7 = d % (7-1)  
		#d_191 = d % (191-1)  
		
		m_1 = pow(ct, self.dp[0], self.p[0])
		#p_i = self.p[0]

		for i in range(1, len(self.p)):
			p_i = self.p_i_precomp[i]
			q_i = self.p[i]
			#q_inv = Crypto.Util.number.inverse(q_i, p_i)
			q_inv = self.q_inv[i]
			m_2 = pow(ct, self.dp[i], q_i)
			h = (q_inv*(m_1-m_2)) % p_i
			m = m_2 + h * q_i
			m_1 = m
			#p_i *= q_i
		#next i
		return m
	
	def encrypt(self, plaint):
		return pow(plaint, self.e, self.N)

def main():
	
	ct = 12345678
	
	#p = 30398585109980725750981070617608984180980802439632903439832634279348595099453491921850380365351803366952002592926748691931147980998236813420665658374766553356830341464401202480482841511398536499433683168316868358921366844163235490440739399308209883695062145423263882435614876424993881734631470949543576978505176270787529413962994769977784313861349316234651800458060310781802351739034479740463029782363377801389217534232359282155861463908028561937200271372850487535107470247869729734222153438766986879068929498295919179466592263091339286529705922192332877852354368435461522178302032903764006283090464493604952019321343
	#q = 423028865593401386182179136467005549464053414296141956570334113640286101466048850561363735156451628560694284385579000819109832916400560780352405474603200036148919144281254259069164237978198995504667447730428483328966866702028443745504920322080005768319866733854114064638495681770597355702841475459337737232266723709306066225653032093256682960451576927378244695177173380479124345458712791344122413687678097827368230229207694839043232099424492633553514471977407895626196925296715432402983782938011045024261301047108569208553728377515821559999528692691554363767925104838957530449319762360116227243746122786647260927
	#N = p*q*7*191
	# NO
	#e = 65537
	x = 10
	bits = 4096 // x
	ps = [Crypto.Util.number.getPrime(bits) for i in range(x)]
	N = 1
	for x in ps:
		N *= x
	#next x
	
	#v = fuckedRSA([p, q, 7, 191], e)
	v = fuckedRSA(ps, 98282992929292929299281818181818)
	
	sig = v.decrypt(ct)
	print(pow(sig, v.e, N))
	
	start = time.time()
	s = 1234567899012093910239102309123
	for i in range(1337):
		s = v.decrypt(s - 1337)
	#next i
	end = time.time()
	print("%3.3f" % (end - start))
	print("result:", s)
#end def main()

if __name__ == '__main__':
	main()
#end if


































