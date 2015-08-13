# SignFaster Solution
*by Javantea*  
*Aug 8, 2015*

Thanks to Reid who helped with signfastest finding an unexpected 100 point bug in their code.

SignFaster is a challenge from OpenCTF 2015 (Defcon 23). It's an RSA challenge that forces you to prove your understanding of RSA's stranger features. If you'd like to test your mettle, don't read any of the three solutions, the first of which is below. Download the challenge tarball and learn about a very difficult and interesting flaw in RSA.

The client is a very simple CTF tcp client that solves a proof of work (using scrypt), then transmits an RSA public key, and finally solves a challenge involving 1337 RSA signatures. The design of the challenge is very good because it tells you if you get it right without requiring you to get the speed correct. That means if you have a solution that is 2 seconds too slow but you don't know if it works, you can test it and make sure that you didn't goof. Two bugs in the challenge were: the public key size validator required public keys that were 4096 bits or more which means a key of 4094 bits won't work when it's a perfectly valid 4096-bit key (RSA is more liberal about key sizes so long as you're in the general area), and the use of twisted python library made the challenge less reliable than it should have been. Both of these were easily overcome.

The client they gave us takes about 40 seconds to compute the signature which is very slow. They want you to submit a solution in less than a second. Even with a fast implementation (which pycrypto is not), it's not easy to make one thousand, three hundred thirty-seven 4096-bit signatures fast.

The library [four1a.py](https://github.com/Neg9/Neg9-www-resources/blob/master/media/open_ctf-2015-writeups/resources/four1a.py) is the central part of the solution. The reason for foul naming of the class is because using this in any system is a horrible weakness and should never be used for any reason, especially not performance.
It provides fuckedRSA, a class that is able to compute Chinese Remainder Theorem quickly with an arbitrary number of prime factors.

    Say you have the primes [3, 5, 7, 11, 13, 15] as your prime factors. N is 3*5*7*11*13*15 = 225225.
    The decryption exponent d is computed from the encryption exponent e and phi which is a combination of the prime factors.
    phi = (p-1)*(q-1)*...
    In the example phi = 2*4*6*10*12*14 = 80640
    Let's say that e = 31
    d = inverse(e, phi)
    In this case, d would be 62431, a large number compared to N.
    Encryption works like this:
    ciphertext = pow(plaintext, e, N)
    Let's say our ciphertext is 110138.
    Then the decryption occurs like:
    plaintext = pow(ciphertext, d, N)
    In this case plaintext = 1337.
    In math notation:
    plaintext = (ciphertext ^ d) mod N
This is an expensive method of decrypting (or signing which is the same operation in RSA) a piece of data.
The Chinese Remainder Theorem states that you can compute the decryption with much lower exponents (and thus faster) by splitting the decryption into multiple parts and combining.
```python
    Compute:
    q_inv = Crypto.Util.number.inverse(q, p)
    m_1 = pow(ct, d_P, p)
    m_2 = pow(ct, d_Q, q)
    h = (q_inv*(m_1-m_2)) % p
    m = m_2 + h * q
```

    The d_P for each factor can be computed as d mod (p-1) where p is a factor.
    The set of d_P for our example would be [1, 3, 1, 1, 7, 5].
    q_inv is the inverse of q (the second prime) mod p.
    The first q_inv is inverse(3, 5) = 2.

In order to save time, we choose a small d and compute a valid e from it. Since e and d are inverse, you can compute e from d.
```python
    e = Crypto.Util.number.inverse(d, phi)
```
The problem is that you can't just pick an aribtrary d. Many inverses of d are 1, so you filter those out and get valid (d, e) pair.
The rest is just doing that repeatedly for any number of prime factors, which is not necessary but useful for the fasterer solution.

This is the change to the client code. See [faster_two.py](https://github.com/Neg9/Neg9-www-resources/blob/master/media/open_ctf-2015-writeups/resources/faster_two.py).

In do_pubkey:
```python
        num_cop = 20
        bits = (4096 // num_cop) + 2
        ps = [Crypto.Util.number.getPrime(bits) for i in range(num_cop)]
        N = 1
        for x in ps:
            N *= x
        #next x
        #print('e', e, len(hex(e)[2:]) * 4)
        self.v = four1a.fuckedRSA(ps, 123123123)
        print('e=', self.v.e, len(hex(self.v.e)[2:])*4)
        
        self.rsa = RSA.construct((long(N), long(self.v.e), long(self.v.d)))
```
In do_challenge:
```python
        for _ in xrange(1337):
            #s = self.rsa.sign(s - 1337, None)[0]
            s = self.v.decrypt(s - 1337)
```

The main trouble I ran into with this is that it took minutes for the server to respond. The authors told me that this was a problem with the design and that I should wait for it.

The winning entry took about 0.7 seconds to compute.

This solution required a lot of optimization and required hours of time despite having solved an RSA-CRT problem before. For an RSA-CRT problem that doesn't have a solution posted, check out [Myster Twister C3](https://www.mysterytwisterc3.org/en/challenges/level-ii/smartcard-rsa)'s Smartcard RSA challenge. It's deviously difficult and doesn't allow you to solve it until you understand the concepts thoroughly.

Running the solution looks kinda like this (the original was lost in the rush to solve fasterer):


    python faster_two.py :: 9999
    Connected
    lineReceived preauth    Please burn some cpu cycles first: mBYA6mEDFtBru1vB 8589934
    Doing proof of work...
    sendLine     pubkey     1439090922000000875
    lineReceived pubkey     Public key?
    Generating RSA key...
    ('d = ', 1L)
    ('d = ', 1L)
    ('d = ', 41L)
    ('e=', 132810465325605413594238657658330709092136982448915075703157833810006711805043838227049464668024193022554161995345977982870159681846521448267415447297706163820585594946666156276686692782738348369144771479272324107073349512604349576305684528783037048888662886743537463976752469753989598741369627101176912839143949558002921985302206310023407015827728108503825693587624977892892805604800103404948573953260592564557659182451964195976848255874603415978118336160849231045170666944123323616009233746850347273292684928213528663169507322289575466136684161084508257815949983124326819380223029190409494083457361351018687807126040974161473769221636151892636284317171049187650214572787430544553096483450457705677651780022459385494212843734067979582497018473443481308901331540113802998606182636174562375894331825899093174654477435797692243411201213991798240950324261288276319774115772098268366519829738338491939083972613702197927252947330828826971466096255762035183899175058594352925192150167445997774195358504048989583536815973433
    98951232457492053326072728766967755669982179477719429374779158508823047991196915072874120653789001054573684827639460491922006571613452438697442963566785909125861754705506671988967686180412983482722294259368335609756097561L, 4116)
    sendLine     challange  MIIEJDANBgkqhkiG9w0BAQEFAAOCBBEAMIIEDAKCAgJOVQ5YaJmM45yFLy5e73Q+qH3TAELJ1O9aEzlSgKzP7tGNoS95c+oLtOoAILoTbQSMCrbwZChgN9Dbteh9L7SLp+5WMW7POyAOA2XXokrOZXchFLJ3TO0aLKF3NF1Xmc/9B896euVw8Kjf5gaNvAXxgOVf1WqYxIfs1eB0W/qgbTwdTsLhNuFh99nWAiomUiFazQkbxBox4e0PPDrzVQpBYhQr0mgIImZ4QdCVjYwWcmtzAmQfKxB9NZj6rD9/zzAq0C6JFs6n/u47Vh+SFJChTqJzX4n1Z1WgyEqz1q/6X8lA5RwWEKXq0ufU3Y+zLprtd8AqIUpEQxJzbjJ73Tg0hyRl8U/iex7j+kM1bFoXj5m51cAe8dkQzY2GOdeC0F/CGd/rv91v2vjyZZO+ocw37iYmG+SLIFo7aYis5hujyosqMeEvCCmPBBtNiURHlWVxdP+aUqCYm6sz6DAfq1esqi3T1z0J2DE+HPdtLjFgSlR1xBtSrGj0PUue+dAIYWNe2ZkZniQXoHiZmu5pK+yJ8fncwG9nIADmP2OwBU15oUnik2bi8/untgtRaVqEoHoHzcJ9U9gbdZKJ7ZKkeFTf3k2CMdLhrgGMoC6xefRBYaJhbhocNRuTBkMoEHSruKTeh0Er+TeMy9hLoLoo8+lyeePpO1j2fgxRzZVBJX6z/4HZAoICAjGsknaAxUac06WhCqyX2VNxF5iJiAMc4rXpnxqlDI2lYUrRvDRMPYoAqfosie1snbuFmdY5sAin8+29PihmChO8VCBlX6axSKaxKfnLtP7iEPxTrqdKrrMdltP918f+RO7TkHSqoMdQTTv/ntjn2TEE6Z13SWvlSES0TnF2a9hBiqP2boIdyF4SsWBr4GKNT9zjc2H5U3nQCqHXh72II4vLWHyOQUyE9BPzP9XLHS6Grx6hl3sM7KdPhOicn/
    C13vZgm0fEWKynTzBepbs8l10hlFoFOYaYiZ6fWUDvmvnVyr8gdZwCB+ThbVx/gUdeOm/VuKC0EmH1u2IyoQKrBSSSLmfN0VR6lofgK+SynbIGADKQ1UzJo7pCvGV/YDLeWYJxGsaHVfevYYbNXLIjTD4G5OjWq35TjFe6FN1+KbAVAd8n60/ON7JzmpvGh6NK9cKO8jPvPEqSY86cCXRmOSpsSQeIJ7IbCjM3NCFd3zK4/SEvrbP91xvsTffT1JGquR1/xwDwExpLRLGIfg0cK2YddHweIbrV0m230qBt+vU1H+i9iqDSmCUsNm9oGKP0e6hpDqq59Bv3QgUBuprnJ6R29s8234AuRwMj7xIzqlwhIM9lC+hxZE8QBrWFI1ElJQQ13X1Xs3pQm6yuArVvg/vMJy3ilb0rp24zgaTZ+cGPnBk=
    lineReceived challange  Okay, make it quick, your challange is: 9Yq1dnwaa+K8ha5AKt78xOVoQ+oARJJllMAWPGP5yL4=
    ('do challenge!', '9Yq1dnwaa+K8ha5AKt78xOVoQ+oARJJllMAWPGP5yL4=')
    sssssssssssss 19686943148567019369591368791148169247298395422433484234705921678774697705537792228355462026041172907768850850542497570732821272723577458605550712900863572157976814651441316694572604216623508713666888710939278370563683098976698956194647594908873248749888245685515633213012743550968264889835436417353472055799571739552160919695717597147495329171749994208779253178102339642376878021509524357202953241110573439884715517563874838556882218714799836218070291865685511162013200213219629784656924663342223575684747839159354134664308306930600883178588653686770642960230629707421015060598064762788414857435948879403410701642489081531026316349327745404929160231886481556018013534367447480603955672263142701369079863641833791894680456319416752496523515230841679160058301816956559632591659480403571037195616109642250406233120125568408804927738218492080307084146034646059748002111357033905089501669553720321091205755067046892739768401688850175804041216501126572070148190776038138973475643111075978049308464614359200240173523
    1775698260375490533417555352115404260375210555647006611064779650505290648980798034176326827344296064799446825656650535122826103688415742095925543116688988151059277748881873530466426210101616472296046669952331494536135462721756253962337392474338858122580503124731707750084698434455655209472
    x 0.980815887451
    sendLine     print      Aco5GwZ8VeYv4TKDNQYQQEFnPeTX+urhksXcI4/vIEUMwkWpLwWvQdg6F/H16ze45ule4iYcSJ4ZAfD0IRz19YQCVaf8zNAh0H+lfqbWq6+yO/fCqaja4/2cD8GG7a3HB3gOnVFbsfS9CGwYh90SCLkTFoflDI0HkmSTHDEZSHO2kgfkYedEF4ZBLbcWhLEy2PD0iME9Wbsqux/rJHsZBGKiYEdbdGhIwrTIMLU2AB+nTOzsrDgaAFuuuncB3a69fYuaV2MSOWJuGxT4mr8FjAooKj28Cx3SDDQ5tAfN0qDk9gJ9t1TjEHLG5CNYLwKa63ht9s1Eev+JE5mJh7C+9TsOBGwUkQVywIvfXMIaM5hFY6ozgA4gqCxYdIW9t+/nKhtZUvyUR04C14w2IHm8hRxtPNzmC2tFNf0bsz371SjKP6XwwPx5umGnTpo1gcWKNH47CiRFzh9Lukm3HrHnJ52AAZSOUzT6LECFPNRfq0r+YYlGZVTjBnOIK7RcAMXtGCd8F2SRk2VyhKLXg5uSG6ZZOfWHmUtMR8VR6XzP+CjG2grdeXD6pes23HKtj1HxHbAb5klitnKWUUdZ9ww554LdN0/rHs9+CardufW2yBbPNmV2MeU2xbeMOGxoW22NJtGVtOFbZFbDoJGJjZDQVZN7yzD+X8uvi/yqRob0QHfH+1n7GQ1KUKNOcI9/TQP0kCcKHxLKpKAcyNoA
    lineReceived print      Solution verified sucessfully!
    This is what they gave us: 'Solution verified sucessfully!'
    lineReceived print      You took 0.025278 seconds.
    This is what they gave us: 'You took 0.025278 seconds.'
    lineReceived print      Your flag is: computation_is_easy_when_someone_else_does_the_work
    This is what they gave us: 'computation_is_easy_when_someone_else_does_the_work'

This solution earned Neg9 200 points out of our total 2710 (7.4%).


