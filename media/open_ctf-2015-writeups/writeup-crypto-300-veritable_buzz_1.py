#! /usr/bin/env python

import hashlib
import binascii
import sys
import re
import base64
from socket import socket
from ecdsa import SigningKey, NIST384p
from ecdsa import VerifyingKey
from ecdsa.numbertheory import inverse_mod

def string_to_number(tstr):
    return int(binascii.hexlify(tstr), 16)
    
def sha1(content):
    sha1_hash = hashlib.sha1()
    sha1_hash.update(content)
    hash = sha1_hash.digest()
    return hash

def recover_key(c1,sig1,c2,sig2,pubkey):
	#using the same variable names as in: 
	#http://en.wikipedia.org/wiki/Elliptic_Curve_DSA

	curve_order = pubkey.curve.order

	n = curve_order
	s1 = string_to_number(sig1[-48:])
	print "s1: " + str(s1)
	s2 = string_to_number(sig2[-48:])
	print "s2: " + str(s2)
	r = string_to_number(sig1[-96:--48])
	print "r: " + str(r)
	print "R values match: " + str(string_to_number(sig2[-96:--48]) == r)

	z1 = string_to_number(sha1(c1))
	z2 = string_to_number(sha1(c2))

	sdiff_inv = inverse_mod(((s1-s2)%n),n)
	k = ( ((z1-z2)%n) * sdiff_inv) % n
	r_inv = inverse_mod(r,n)
	da = (((((s1*k) %n) -z1) %n) * r_inv) % n

	print "Recovered Da: " + hex(da)

	recovered_private_key_ec = SigningKey.from_secret_exponent(da, curve=NIST384p)
	return recovered_private_key_ec.to_pem()


def test():
	priv = SigningKey.generate(curve=NIST384p)
	pub = priv.get_verifying_key()

	print "Private key generated:"
	generatedKey = priv.to_pem()
	print generatedKey

	txt1 = "Dedication"
	txt2 = "Do you have it?"

	#K chosen by a fair roll of a 1d10000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 
	sig1 = priv.sign(txt1, k=4444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444)
	print "Signature 1: " + str(sig1.encode('hex'))
	sig2 = priv.sign(txt2, k=4444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444)
	print "Signature 2: " + str(sig2.encode('hex'))

	print "Signature 1 verification: " + str(pub.verify(sig1, txt1))
	print "Signature 2 verification: " + str(pub.verify(sig2, txt2))

	key = recover_key(txt1, sig1, txt2, sig2, pub)
	print "Private key recovered:"
	print key

	print "Equality of generated & recovered keys: " + str(generatedKey == key)

public_key_ec_pem = '''
-----BEGIN PUBLIC KEY-----
MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEYlsc6dc6ucsFVJavUphpKc350ISuwGUh
uD1MYO9TpbdF+KghCWkbBCDdK7lt5VKdOnYZKaIQ8n7J2kHaFQnVsk7Drh9zDL09
CDEqLYiqU9qRSd14/TCda1fAIH4vgRO1
-----END PUBLIC KEY-----
'''.strip()

def recover():
	txt1 = "Students reported that students post to discussion forums more frequently and are irrevocable provided the stated conditions are met."
	sig1 = '''a0289c0fa7e87f1ab1e94b577f43691ebd70c04b0e62ca7eaaf1791983d512e7bbc843ee3a2a0430455e9f755f832ccdcd7a46d769ee43467a01453214868094ca228cb5eebc953a39fb9bbaf865f4dbe1dad9b5f9f1bed75671e0db5433f0ed'''.strip().decode('hex')

	txt2 = "But is this enough? And what new threats could be using it as a friend or fan.[2]"
	sig2 = '''a0289c0fa7e87f1ab1e94b577f43691ebd70c04b0e62ca7eaaf1791983d512e7bbc843ee3a2a0430455e9f755f832ccd54d4f8306fe11bd4a28a491ddf596c64cd98c93d7fa9a05acead17e42e96ed1a190a2fddd7c695b8d9bce43f221b4e1b'''.strip().decode('hex')

	public_key_ec = VerifyingKey.from_pem(public_key_ec_pem)
	print "Verify1: " + str(public_key_ec.verify(sig1, txt1))
	print "Verify2: " + str(public_key_ec.verify(sig2, txt2))
	print "curve order:", public_key_ec.curve.order

	key = recover_key(txt1, sig1, txt2, sig2, public_key_ec)
	print key


if __name__ == "__main__":
	print "---Performing test attack on known private key---"
	test()
	print
	print "---Attempting to recover unknown key---"
	recover()
	print "---Done!---"