import hashlib, math
WORDS = open("bip39_english.txt").read().split()
assert len(WORDS) == 2048

def bip39_encode(entropy):
    checksum_len = len(entropy) * 8 // 32
    digest = hashlib.sha256(entropy).digest()
    bits = "".join(f"{b:08b}" for b in entropy)
    bits += "".join(f"{b:08b}" for b in digest)[:checksum_len]
    assert len(bits) % 11 == 0
    return " ".join(WORDS[int(bits[i:i+11], 2)] for i in range(0, len(bits), 11))

OFFICIAL = [
 ("00000000000000000000000000000000","abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"),
 ("7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f","legal winner thank year wave sausage worth useful legal winner thank yellow"),
 ("80808080808080808080808080808080","letter advice cage absurd amount doctor acoustic avoid letter advice cage above"),
 ("ffffffffffffffffffffffffffffffff","zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo wrong"),
 ("ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff","zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo zoo vote"),
]
for hexent, expect in OFFICIAL:
    got = bip39_encode(bytes.fromhex(hexent))
    assert got == expect, f"SELF-TEST FAILED {hexent}\n got {got}"
print(f"BIP-39 self-test: {len(OFFICIAL)}/{len(OFFICIAL)} official vectors reproduced\n")

def reference(rolls, words):
    e = hashlib.sha256(rolls.encode()).digest()
    return bip39_encode(e[:16] if words == 12 else e)

def bowser(rolls):
    "lnbits/hardware-wallet: exactly 100 ASCII rolls, full 32-byte digest, 24 words"
    assert len(rolls) == 100 and all(c in "123456" for c in rolls)
    return bip39_encode(hashlib.sha256(rolls.encode()).digest())

def keystone(rolls, words):
    e = hashlib.sha256(rolls.replace("6","0").encode()).digest()
    return bip39_encode(e[:16] if words == 12 else e)

V99 = "655152231316521321611331544441236164664431121534415633526456254462245546236542364246312613322234612"
V50 = "65515223131652132161133154444123616466443112153441"
assert len(V99) == 99 and len(V50) == 50
DOC_24 = "eyebrow obvious such suggest poet seven breeze blame virtual frown dynamic donor harsh pigeon express broccoli easy apology scatter force recipe shadow claim radio"
DOC_12 = "hole luggage safe present express tragic orbit shed switch metal identify path"

r24, r12 = reference(V99,24), reference(V50,12)
print("Document's published test vectors, recomputed from scratch:")
print(f"  99 rolls -> 24 words : {'MATCH' if r24==DOC_24 else 'MISMATCH'}")
print(f"  50 rolls -> 12 words : {'MATCH' if r12==DOC_12 else 'MISMATCH'}")

k24 = keystone(V99,24)
print(f"\nSame rolls under Keystone's 6->0 construction:\n  {k24}")
print(f"  differs from reference: {k24 != r24}")
print(f"  words in common: {sum(1 for a,b in zip(k24.split(),r24.split()) if a==b)}/24")
print(f"  digits rewritten by Keystone: {V99.count('6')} of 99")
p50, p99 = (5/6)**50, (5/6)**99
print(f"\nTwo constructions coincide only if no 6 is rolled:")
print(f"  50 rolls: 1 in {1/p50:,.0f}")
print(f"  99 rolls: 1 in {1/p99:,.0f}")

print("\nBitBox02 paper-table mapping, checked against the wordlist:")
def bb(d1,d2,d3,d4,d5,coin):
    idx = (d1-1)*512+(d2-1)*128+(d3-1)*32+(d4-1)*8+(d5-1)*2+coin
    return idx, WORDS[idx]
for p in [(1,1,1,1,1,0),(1,1,1,1,1,1),(2,1,1,1,1,0),(4,4,4,4,4,1)]:
    idx,w = bb(*p)
    print(f"  dice {p[:5]} coin {p[5]} -> index {idx:4d} -> {w}")
print("  5 dice x 2 bits + 1 coin bit = 11 bits per word; 23 words = 253 bits")

print("\nBowser (LNbits) hashes the same way but demands a 100th roll:")
V100 = V99 + "4"
b24 = bowser(V100)
print(f"  reference, first 99 : {r24}")
print(f"  Bowser, all 100     : {b24}")
print(f"  differs from reference: {b24 != r24}")
print(f"  words in common: {sum(1 for a,b in zip(b24.split(), r24.split()) if a==b)}/24")
print(f"  truncating Bowser's 100 rolls to 99 recovers Bowser's seed: "
      f"{reference(V100[:99], 24) == b24}")
print(f"  input entropy: 99 rolls {99*math.log2(6):.3f} bits, "
      f"100 rolls {100*math.log2(6):.3f} bits, against a 256-bit digest")
