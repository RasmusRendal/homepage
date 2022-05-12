---
title: "DDC 2022: Crypto Writeups"
date: 2022-05-09T17:39:36+02:00
draft: false
katex: true
---
DDC 2022 was held this weekend.
This time around, I pretty much only did cryptography exercises (And a few blockchain ones).
This post contains writeups for all the cryptography challenges I did.

Each of these sections include a link to a zip file containing the challenge. Thus, the challenge is not rendered as a part of the post.
You probably have to download and look at the zip to know what I'm talking about, and that doesn't really guarantee anything either.
# Riot Prrl 3 - Friends
Riot Prrl 3 was a exercise which followed an OSINT and a forensics exercise, so it's not as clear as with other self-contained challenges what the challenge files are.
But some of them I uploaded [here](/files/ddccrypto/prrl.zip).
In isolation, what we basically have is:
* A series of ciphertexts with a timestamp
* A known plaintext/ciphertext pair
* Encryption and decryption scripts

In the `.bash_history`, we find the following interesting entry:
```bash
chmod +x encrypt.py decrypt.py
./encrypt.py "Hej prrl!"
sudo pacman -S python-mpmath
./encrypt.py "Hej prrl!"
```
This corresponds to the ciphertext of the first sent message:
```
Astrid Mågensdal            (06-04-22 22:07)    2ebc1637e6b559d539892502de8c6eec
```
The encryption cipher can best be described as XOR, with the addition that every eight output bytes are also xored with the previous eight output bytes.
The first eight output bytes are xored with eight random bytes, generated with `random.randint()`, and seeded by the timestamp.
The key is acquired from a function we are not given, `get_key_with_length(n)`.
Thus, knowing a timestamp, we can recover the IV like so:
```python
def parse_message(s):
    timestamp, msg = s.split(")")
    msg = bytes.fromhex(msg.split(" ")[-1])
    timestamp = timestamp[1:]
    date, time = timestamp.split(" ")
    day, month, year = date.split("-")
    year = "20" + year
    hour, minute = time.split(":")
    timestamp = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute)).timestamp()
    return timestamp, msg

def get_iv(timestamp):
    random.seed(timestamp // 3600 * 3600)
    return bytes([random.randint(0, 255) for x in range(block_size)])
```

Knowing a plaintext/ciphertext pair with a corresponding pair, we can now extract the key:
```python
def pad(plaintext):
    padding_length = -len(plaintext) % block_size
    return plaintext + b'\x00' * padding_length

def extract_key(iv, msg, known):
    assert len(msg) == len(known), (msg, known, len(msg), len(known))
    key = b""
    last_block = iv
    for b, c in zip(block_split(msg), block_split(known)):
        key += byte_xor(last_block, byte_xor(b, c))
        last_block = c
    return key

timestamp, c = parse_message("(06-04-22 22:07)	2ebc1637e6b559d539892502de8c6eec")
plain = pad(b"Hej prrl!")
print(extract_key(get_iv(timestamp), plain, c))
```
Giving us the key: `3.14159265358979`.
From here it was simply a wild guess that the key generation function would return the first `n` digits of pi in ASCII. This lets us decrypt the whole conversation, and get the flag.

# CBC Time!
A CBC oracle/timing attack. The challenge files are [here](/files/ddccrypto/cbctime.zip).

You were given the encrypted flag, and an endpoint which would decrypt the data, and if no padding errors occurred, wait 3 seconds before responding to the request.
This basically gave us a padding oracle.
Padding oracles are pretty well known at this point, so I'll not describe it in detail. But here is the solution code:
```python
import requests
from tqdm import tqdm

TargetUrl = "http://cbctime.hkn:8080/submitdata"

def upload_data(encrypted_bytes):
    encrypted_data = encrypted_bytes.hex()
    payload = {}
    payload["submitted_data"] = encrypted_data
    resp = requests.post(TargetUrl, data=payload)
    timetaken = resp.elapsed.total_seconds()
    return timetaken > 3

enc_flag = bytes.fromhex("ecbfc6f3c6e8cc2c0b6c6dc8f2cfeaa37234af4717e6f27c2fa38ed590034fa9b40979871195134ecd80f10d08429c3a3d32e211c3bc0e847372212b54967e13")

blocks = [enc_flag[i:i+16] for i in range(0, len(enc_flag), 16)]
assert b"".join(blocks) == enc_flag

# Previous dec_block, current block
def find_pad(block, dec_block):
    pad = len(dec_block)+1
    new_block = bytearray(block[:])
    for i in range(1, pad):
        new_block[-i] ^= dec_block[-i] ^ pad
    return bytes(new_block)

fake_block = b"\x05"*16
assert find_pad(fake_block, b"") == fake_block

def byte_xor(b1, b2):
    return bytes([x1 ^ x2 for x1, x2 in zip(b1, b2)])

def decrypt_block(block):
    zeroing = b"\x00"*16
    for i in range(1, 17):
        lzero = [x^i if 15 -i != index else x for index, x in enumerate(zeroing)]
        for b in tqdm(range(256)):
            lzero = bytearray(lzero)
            lzero[-i] = b
            lzero = bytes(lzero)
            if (upload_data(lzero + block)):
                zeroing = bytearray(zeroing)
                zeroing[-i] = b ^ i
                zeroing = bytes(zeroing)
                break
        else:
            raise Exception("Oh no")
    return zeroing

decrypted = b""
for i in range(1, len(blocks)):
    dec_block = decrypt_block(blocks[i])
    decdec = byte_xor(blocks[i-1], dec_block)
    decrypted += decdec
print(decrypted)
```
# Kidz 2 - Symmetric Boogaloo
A hashing function based on DES. The challenge files are [here](/files/ddccrypto/kidz2.zip).
The goal in this exercise is to break the hashing system by producing data starting with `sudo cat flag.txt`, while having a hash of 0.

## Key schedule:
In the function `Hash(secret_key, message)`, we could see how several blocks of data were getting encrypted prior to the compression part.
By just giving it a null key, we can see that the key schedule ends up being \\(k_1, k_2, \bar{k_1}, \bar{k_2}, \ldots\\) with \\(\bar{k}\\) representing
the binary complement of \\(k\\).

## The complementary property of DES
DES has a very weird property called the complementary property:
$$ E_K(M) = \overline{E_{\bar{K}}(\bar{M})} $$
If you take the complement of the key and message before encrypting, it will have the same result as if you just took the complemnet of the result.

Combined with the key schedule above, that means that if you encrypt \\(m_1 \mid m_2 \mid \bar{m_1} \mid \bar{m_2}\\), the output would be \\(c_1 \mid c_2 \mid \bar{c_1} \mid \bar{c_2}\\), with \\(\mid\\) representing concatenation.

## The compression step
The final step of the hashing algorithm, and the part that allows us to really break it is the compression step.
Essentially, every eight input blocks get XOR'ed together to one output block. Combined with the properties above, the eight input blocks:
$$ b_1 \mid b_2 \mid b_3 \mid b_4 \mid \bar{b_3} \mid \bar{b_4} \mid \bar{b_2} \mid \bar{b_1} $$
are hashed into the block 0. For the first eight blocks, we set \\( b_1 \mid b_2 \mid b_3 \\) to `sudo cat flag.txt`, and fill the rest of \\(b_3\\) and \\(b_4\\) with random data.
For the three other blocks, we fill all four free blocks with random data. This gives us a correct hash, and the solution to the challenge!

# Zero2Hero
This challenge is based on Shamir's Secret Sharing. The challenge files are [here](/files/ddccrypto/zerotohero.zip).
To share a secret \\(s\\) amongst \\(N\\) people, such that at least \\(k \leq N\\) must be present
to reconstruct it, we simply construct a polynomial (in a finite field) of order \\(k-1\\) of the form \\(f\(x\) = s + a_{1} x + a_2 x^2 ...\\).
As you need at least \\(k\\) points to reconstruct the polynomial, and \\(k-1\\) points give you no information, this is a great scheme.

An important part of course is that no one can have the point at zero, because \\(f(0) = s\\). And the script checks for that!
However, it does not check for \\(p\\), and since the polynomial is defined over a finite field of size \\(p\\), \\(p \equiv 0\\). Thus, submitting \\(p\\) returns the secret.

# Vive le Fromage!
Challenge files [here](files/ddccrypto/fromage.zip).

I really recommend trying to run the challenge script yourself, just to experience the beautiful effects.
It was also all in french. The challenge was that given a list of encrypted prices of specific cheeses, a number for each cheese representing how many you are buying, and a number representing how much money you will be spending on wine, you have to produce the encrypted total cost.
Initially, the server will tell you `Mise en place "La Fromagerie de Monsieur Paillier", S'il Vous Plait Tenez Madame...`.
Paillier is the name of [a cryptosystem](https://en.wikipedia.org/wiki/Paillier_cryptosystem)
This cryptosystem has homomorphic properties, specifically that:
 * \\( D(E(m_1, r_1)^{m_2}\ \mathrm{mod}\ n^2) = m_1 \cdot m_2 \\)
 * \\( D(E(m_1, r_1) \cdot E(m_2, r_2) \mathrm{mod}\ n^2) = m_1 + m_2 \\)

With these properties, we can create the encrypted total cost, without ever knowing how much we are paying.
I used the following script for calculating the prices. I did not write a completely automated solve script, because I anticipated difficulties from the animations.
```python
def solve(prix, cours, vin, n, g):
    def mul(c, m):
        return pow(c, m, n*n)

    def add(c1, c2):
        return (c1 * c2) % (n * n)

    cost = enc(n, g, vin)
    for i in range(len(cours)):
        cost = add(cost, mul(prix[i], cours[i]))
    return cost
```

# BuDDHa Wisdom
I did not solve this one at the actual CTF. After the CTF, I was told it was something to do with Weil pairings, and then it still took me about five hours to get it.
Challenge files [here](/files/ddccrypto/buddha.zip).

The challenge is basically a [Decisional Diffie Hellman](https://en.wikipedia.org/wiki/Decisional_Diffie%E2%80%93Hellman_assumption) problem.
The Decisional Diffie Hellman problem is basically that given a triple \\(\(Ga, Gb, Gc\)\\), you have to be able to distinguish the case where \\(c = a + b\\) from the case where \\(c \neq a + b\\) with a reasonable probability[^1].
[^1]: The reason that this description of DDH looks different from Wikipedia is that I adapted it for elliptical curves.

Given a plaintext message \\(M\\), an [ElGamal](https://en.wikipedia.org/wiki/ElGamal_encryption) encrypted ciphertext \\((C_1, C_2)\\), the generator \\(G\\), and public key \\(P\\), we know that
\\(P = s\ G\\), \\(C_1 = y\ G\\), \\(C_2 - M = s\ y\ G\\), giving us a DDH triple.

## Weil Pairings
For our purposes, a Weil Pairing is a function that given two members of the torsion group \\(E[m]\\)[^2] that produces an \\(m\\)th root of unity.
[^2]: A torsion group \\(E[m]\\) is just the set of points \\(P\\) in the elliptic curve \\(E\\) such that \\(m\ P = \mathcal{O}\\).

Weil Pairings are a bilinear map, which means they have the property:
$$ e_m(aP, bQ) = e_m(P, Q)^{ab} $$

From this we can gather that the statement:
$$ e_m(P, C_1) = e_m(G, C_2 - M) $$
$$ e_m(sG, yG) = e_m(G, syG) $$
is true if \\(C_2 = C_1 + M\\)

## Distortion maps
The problem with Weil Pairings that it is degenerate in the case of points generated by the same generator:
$$ e_m(aP, bP) = e_m(P, P)^{a b} = 1^{a b} = 1 $$

This basically means that an unmodified Weil Pairing is useless for the DDH problem.
To actually solve the DDH problem, you have to use something called a distortion map.

A distortion map \\(\phi: E \rightarrow E\\) has the following properties:[^3]
 * \\( e_m(P, \phi(P))^r = 1 \\) if and only if \\( e | r \\)
 * \\( \phi(nP) = n \phi(P) \\)

The first property fixes our issues with all the pairings being one. And the second property ensures that the pairing is still worth something.
So now we end up with the property that:
$$ e_k(\phi(P), C_1) = e_k(\phi(G), C_2 - M) \leftrightarrow dec_s(C_1, C_2) = M $$

There is no known algorithm for finding distortion maps in the general case.
However, since the curve is supersingular there exists
a relatively simple distortion map in the curve, if it is extended to \\(\mathbb{F}_{p^k}\\)[^4]:
$$ \phi(x, y) = (-x, \sqrt{-1}y) $$
[^4]: \\(k\\) is the smallest integer such that \\(l \mid (p^k -1) \\), where \\(l\\) is the order of the generator

With the distortion map, we have the solution to the DDH problem:
```python
import pwn
from challenge import *
from tqdm import tqdm

# Compute the embedding degree
order = E.order()
k = 1
while (p**k - 1) % order:
    k += 1
K.<a> = GF(p**k)
EK = E.base_extend(K)

a1 = sqrt(K(-1))
def distortion_map(P):
    return EK(-P.xy()[0], a1 * P.xy()[1])

assert distortion_map(G*100) == distortion_map(G)*100

#remote = pwn.remote("buddha.hkn", 13337)
remote = pwn.process(["/run/current-system/sw/bin/sage", "challenge.sage"])
remote.recvuntil(b"The public key is (")
Pk = remote.recvline().split(b" : ")
Pk = E(int(Pk[0]), int(Pk[1]))

def matches(m, c1, c2):
    M = encode_msg(m)
    return distortion_map(Pk).weil_pairing(EK(c1), r * h) == distortion_map(G).weil_pairing(EK(c2 - M), r * h)

for i in tqdm(range(50)):
    remote.recvuntil(b"The first message is ")
    m1 = int(remote.recvline()[:-1])
    remote.recvuntil(b"The second message is ")
    m2 = int(remote.recvline()[:-1])
    remote.recvuntil(b"c1 = (")
    c1 = remote.recvline().split(b" : ")
    c1 = E(int(c1[0]), int(c1[1]))
    remote.recvuntil(b"c2 = (")
    c2 = remote.recvline().split(b" : ")
    c2 = E(int(c2[0]), int(c2[1]))
    remote.recvuntil(b"What is your guess (0 or 1)?")
    if matches(m1, c1, c2):
        remote.sendline(b"0")
    elif matches(m2, c1, c2):
        remote.sendline(b"1")
    else:
        raise Exception("Something is broken")
remote.recvline()
print(remote.recvall().decode('ascii'))
```

[^2]: Hoffstein 2014: An Introduction to Mathematical Cryptography, pp 350.
