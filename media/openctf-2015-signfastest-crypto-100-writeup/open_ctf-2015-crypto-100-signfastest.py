#!/usr/bin/env python

import pow

import sys
import time

from Crypto.PublicKey import RSA
import Crypto.Util.number

from binascii import hexlify, unhexlify
from base64 import b64encode as b64e, b64decode as b64d

from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor, protocol
from twisted.protocols import basic
import four1a

def hex_to_b64(h):
    return b64e(unhexlify(h))

def b64_to_hex(b):
    return hexlify(b64d(b))

def int_to_b64(i):
    return hex_to_b64(hex(i)[2:-1])

def b64_to_int(b):
    return long(b64_to_hex(b), 16)

class SignFaster(basic.LineReceiver):
    delimiter = "\n"

    def __init__(self):
        self.state = 'preauth'
    
    def connectionMade(self):
        print "Connected"

    def sendLine(self, data):
        print "sendLine    ", self.state, "\t", data
        basic.LineReceiver.sendLine(self, data)

    def lineReceived(self, data):
        print "lineReceived", self.state, "\t", data
        if self.state and hasattr(self, "do_" + self.state):
            data = data.rstrip("\r\n")
            idx = data.find(": ")
            if idx >= 0:
                data = data[idx+2:]
            getattr(self, "do_" + self.state)(data.rstrip("\r\n"))
        else:
            self.disconnect("Unhandled PEBCAK exception!")

    def disconnect(self, message=None):
        if message is not None:
            print message
        self.transport.loseConnection()
        reactor.stop()

    def do_preauth(self, data):
        print "Doing proof of work..."
        (nonce, target) = data.split(" ")
        counter = pow.generate(nonce, int(target))
        self.state = 'pubkey'
        self.sendLine(str(counter))

    def do_pubkey(self, data):
        print "Generating RSA key..."
        #self.rsa = RSA.generate(4096)
        # If you find p and q which this is fast for, put them in here.
        p, q = Crypto.Util.number.getPrime(2048), Crypto.Util.number.getPrime(2048) #379, Crypto.Util.number.getPrime(4095)
        e = 1
        N = p*q
        d = Crypto.Util.number.inverse(e, (q-1)*(p-1))
        self.rsa = RSA.construct((long(N), long(e), long(d), long(p), long(q)))
        pub = self.rsa.publickey()
        self.state = 'challange'
        self.sendLine(b64e(pub.exportKey(format='DER')))

    def do_challange(self, data):
        print("do challenge!", data)
        s = b64_to_int(data)

        t1 = time.time()
        for _ in xrange(1337):
            s = self.rsa.sign(s - 1337, None)[0]

        print time.time() - t1
        self.state = 'print'
        self.sendLine(int_to_b64(s))

    def do_print(self, data):
        print "This is what they gave us:", repr(data)

def main():
    factory = ClientFactory()
    factory.protocol = SignFaster
    reactor.connectTCP(sys.argv[1], int(sys.argv[2]), factory)
    reactor.run()

if __name__ == '__main__':
    main()
