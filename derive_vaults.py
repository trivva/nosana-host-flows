"""
Derives the NOS vault (PDA) of each Nosana GPU market.
Vault = PDA of the Jobs program with seeds [market address, NOS mint].
Verified: market nvidia-3090 -> Dqx5MbcAGQo2vgWaUau81joSJwDTaMzdRt1CEX8xzxUj (the address paying 3090 hosts on-chain).
Output: data/market_vaults.csv. Pure Python, no dependencies.
"""
import hashlib
A='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def b58d(s):
    n=0
    for c in s: n=n*58+A.index(c)
    b=n.to_bytes((n.bit_length()+7)//8,'big')
    return b'\0'*(len(s)-len(s.lstrip('1')))+b
def b58e(b):
    n=int.from_bytes(b,'big'); s=''
    while n: n,r=divmod(n,58); s=A[r]+s
    return '1'*(len(b)-len(b.lstrip(b'\0')))+s
p=2**255-19; d=-121665*pow(121666,p-2,p)%p
def on_curve(b):
    y=int.from_bytes(b,'little')&((1<<255)-1)
    if y>=p: return False
    u=(y*y-1)%p; v=(d*y*y+1)%p
    x2=u*pow(v,p-2,p)%p
    if x2==0: return True
    return pow(x2,(p-1)//2,p)==1
def pda(seeds,prog):
    for bump in range(255,-1,-1):
        h=hashlib.sha256(b''.join(seeds)+bytes([bump])+prog+b'ProgramDerivedAddress').digest()
        if not on_curve(h): return b58e(h),bump
jobs=b58d('nosJhNRqr2bc9g1nfGDcXXTXvYUmxD4cVwy2pMWhrYM')
mint=b58d('nosXBVoaCTtYdLvKY6Csb4AC8JCdQKKAaWYtx2ZMoo7')
m=b58d('CA5pMpqkYFKtme7K31pNB1s62X2SdhEv1nN9RdxKCpuQ')
print('3090 vault:', pda([m,mint],jobs)[0])

markets = """nvidia-pro-6000-cc EuYwNdSDduvFuTTS4fEgNL23rZRaTMbecM1J6fJJoQR1
nvidia-3070 RXP7JK8MTY4uPJng4UjC9ZJdDDSG6wGr8pvVf3mwgXF
nvidia-4060 47LQHZwT7gfVoBDYnRYhsYv6vKk8a1oW3Y3SdHAp1gTr
nvidia-5090 6Xt8hgVLLL2PSHC9NtJP8E8oTdA5ZJc95hZEnHcdqKqb
nvidia-5080 9HnJacS25TnErsKMYJmKqWeCAMYuwY7gzhz9Eqhp5VE7
nvidia-3090 CA5pMpqkYFKtme7K31pNB1s62X2SdhEv1nN9RdxKCpuQ
nvidia-5090-community 8pr3btRVcbqqGxaZspd18QWm41eByTjZR1cB58nVWiNg
4090-reserved 5CRDSHGzMtGCohobfvLU3p1h7uKvAzuLpGKrfutLz3U5
nvidia-a100-80gb-community 9qTcReKjb7LKndq2J4pxd2gCgC9ux3z2jF4oUTWhQovZ
nvidia-a4000-community BykxcqsPpMLo2nYZJfFHSUwi1fJNWDKFYi5idJfQ4hgk
nvidia-5070 5eX3kWkrcbwejEc1svbfP4F7NKYjtPDuyU5KnV1hUBKg
nvidia-5080-community 9fgU7Btd5gXB3xzAFmT322KdkdUuMjX7GG1LeNT5qFj4
nvidia-3060 7AtiXMSH6R1jjBxrcYjehCkkSF7zvYWte63gwEDBcGHq
nvidia-8x-a5000 3XGECQon74HQwPJuZjgCwqdQ5Nt3wktZ9fcavcDN9qB2
zephyr-skyline-4090 An4tqwD3mTzRipAdVxqSNrTtGfiqRh9DSgUjZ86zNrDa
nvidia-pro6000-6x 37VPcEfrA34vLRygFQd7bWiosBwv3a5jPv4hcXdumytC
nvidia-a40 BLqSzPzcXMX5gseNXE4Ma45f31Eo6tNFVYoRmPG7kxP2
nvidia-a100-40gb-community 6xJakjtNhCSRQJf5Lk79E846w4gyvs83cWz8Xd2cKnmH
nvidia-4090-community Dcwz62TisNbWuto6KJM2EGYGVKnHbdZGVGmgLASzsXy8
nvidia-3070-community 5DTW69bSjrGvNWWnGco3xi5EZTpE9o8NSPFzbw71HByp
silent-ridge-4090 C8JnyH6qhid3EaovSwb8JTkwAGP5n6GGqkktrazuKDqC
ember-drift-4090 31P9d5ahEY9iSmZuXJ2xwJsbRztFK5AUCdkvgziUM3vn
nvidia-4080 77wdaAuYVxBW5u2QiqddkAzoBZ5cuKxH9ZCbx5HfFUb2
nvidia-a4000 7fnuvPYzfd961iRDPRgMSKLrUf1QjTGnn7viu3P12Zuc
nvidia-3080-community 741d2jZmNreNVyrLCgGkvVGx1Wx3FjumXXPefd8MX83J
nvidia-a5000-community HBxyYe4gTzuutWL991vKL6isqwhGqApELAfoRiZgW1Sw
nvidia-4080-community HanragNudL4S4zFtpLQv85dn6QbdzCm7SNEWEb9sRp17
nvidia-4060-community 2NTfTR64rEH8avzNsxExeNKSXNZfRHTg1JZKmyqbR8LL
nvidia-a40-community 8kGjraXnXirSQcgjxTbFBK7QTBVz9fm9ufSRVr3DqBTV
nvidia-a100-40gb F3aGGSMb73XHbJbDXVbcXo7iYM9fyevvAZGQfwgrnWtB
nvidia-3090-community 985pQEVPn7SL5os3Z2iNwBoX4f9Bva334dENweXWyt9t
nvidia-3060-community 62bAk2ppEL2HpotfPZsscSq4CGEfY6VEqD5dQQuTo7JC
nvidia-3080 7RepDm4Xt9k6qV5oiSHvi8oBoty4Q2tfBGnCYjFLj6vA
nvidia-a6000 EjryZ6XEthz3z7nnLfjXBYafyn7VyHgChfbfM47LfAao
nvidia-pro6000-community 3tB46gYRURjyhmdQkTBqjhfT7rR2h6qFCPC2jtHwuorA
nvidia-4090 97G9NnvBDQ2WpKu6fasoMsAKmfj63C9rhysJnkeWodAf
nvidia-a100-80gb GLJHzqRN9fKGBsvsFzmGnaQGknUtLN1dqaFR8n3YdM22
nvidia-6000-ada 6eMivCx49anWFYwNgg8KNJQfSJYB5nBdif8CK6z52dem
nvidia-h100 Crop49jpc7prcgAcS82WbWyGHwbN5GgDym3uFbxxCTZg
nvidia-a6000-community 8XT6GbHuEVEdxatFsTYsKKeFB6jAGcJPrezA5fF1p6fq
frost-cascade-4090 FNchga9tXmcQU1DXCWapysjMCgUioiY6vQAb38Ts612K
nvidia-4070-community Bk5E3zN6xkxZS2nCQa3oTN6zjYmzFbXTVtnowUzH71zu
nvidia-a5000 4uBye3vJ1FAYukDdrvqQ36MZZZxqW3o8utWu8fyomRuN
nvidia-4070 EzuHhkrhmV98HWzREsgLenKj2iHdJgrKmzfL8psP8Aso
nvidia-6000-ada-community 5ZfPkACuAZgZVF1cobN4CeJdoXn2ze3azwtSv5ah9otV
nvidia-h100-community D9Pv7LthkwSYVJo5iGUPsAiosGwARj7eHTntuWFR1MK2
nvidia-pro6000 Ekro9NTNqLbnMkN7x7y2rY9AeTkazcHj2PPaTxT1Cogz
nvidia-5070-community HnCwNsk1FTREgmp3BQ1A9WBE9UqzCkfEfqPv9BybYA2y"""
rows=[]
for line in markets.splitlines():
    slug,addr=line.split()
    rows.append((slug,pda([b58d(addr),mint],jobs)[0]))
with open('data/market_vaults.csv','w') as f:
    f.write('market,market_address,vault_owner\n')
    for (slug,v),line in zip(rows,markets.splitlines()):
        f.write(f'{slug},{line.split()[1]},{v}\n')
vals=",\n  ".join(f"('{v}', '{s}')" for s,v in rows)
print(len(rows))

