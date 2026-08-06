"""Independent validation of SeedSigner's dice-roll -> mnemonic implementation.

Cross-checks the algorithm three ways that share no code:
  A. A from-scratch BIP-39 implementation written directly from the spec
  B. python-mnemonic (Trezor's reference implementation)
  C. embit 0.8.0 (the library SeedSigner actually ships)

against the two test vectors published in SeedSigner's own docs/dice_verification.md,
and validates implementation A against the official BIP-39 test vectors so that the
"independent" implementation is itself known-good.

Run with the venv that has `mnemonic` and `embit==0.8.0` installed.
"""
import hashlib
import json
import unicodedata
import urllib.request

# ---------------------------------------------------------------- test vectors
# Published in SeedSigner's docs/dice_verification.md (tag 0.8.7).
VEC_99 = (
    "655152231316521321611331544441236164664431121534415633526456254462245546236542364246312613322234612",
    "eyebrow obvious such suggest poet seven breeze blame virtual frown dynamic donor "
    "harsh pigeon express broccoli easy apology scatter force recipe shadow claim radio",
)
VEC_50 = (
    "65515223131652132161133154444123616466443112153441",
    "hole luggage safe present express tragic orbit shed switch metal identify path",
)
VEC_50_FINGERPRINT = "8d9cced8"


# --------------------------------------------------- A: from-scratch BIP-39
def bip39_from_entropy_scratch(entropy: bytes, wordlist: list) -> str:
    """BIP-39 entropy -> mnemonic, implemented directly from the spec.

    Spec: append the first ENT/32 bits of SHA256(entropy) as checksum, split the
    result into 11-bit groups, and index the wordlist with each group.
    """
    ent_bits = len(entropy) * 8
    checksum_bits = ent_bits // 32
    digest = hashlib.sha256(entropy).digest()

    bits = "".join(f"{b:08b}" for b in entropy)
    bits += "".join(f"{b:08b}" for b in digest)[:checksum_bits]

    words = [wordlist[int(bits[i:i + 11], 2)] for i in range(0, len(bits), 11)]
    return " ".join(words)


def seedsigner_dice_to_entropy(rolls: str, num_words: int) -> bytes:
    """SeedSigner's transformation, transcribed from helpers/mnemonic_generation.py.

        entropy_bytes = hashlib.sha256(roll_data.encode()).digest()
        if 12-word: entropy_bytes = entropy_bytes[:16]

    Note it hashes the ASCII DIGITS of the rolls, not a base-6 or binary reduction.
    """
    entropy = hashlib.sha256(rolls.encode()).digest()
    return entropy[:16] if num_words == 12 else entropy


print("=" * 78)
print("SEEDSIGNER DICE -> MNEMONIC : INDEPENDENT CROSS-VALIDATION")
print("=" * 78)

# ------------------------------------------------------------------ wordlists
from mnemonic import Mnemonic          # B: Trezor reference
from embit import bip39 as embit_bip39  # C: what SeedSigner ships

trezor = Mnemonic("english")
trezor_wordlist = list(trezor.wordlist)
embit_wordlist = list(embit_bip39.WORDLIST)

print("\n[1] Wordlist agreement")
print(f"    trezor words={len(trezor_wordlist)}  embit words={len(embit_wordlist)}")
same_wordlist = trezor_wordlist == embit_wordlist
print(f"    identical: {same_wordlist}")
wl_hash = hashlib.sha256("\n".join(trezor_wordlist).encode()).hexdigest()
print(f"    sha256(wordlist, newline-joined) = {wl_hash}")

# ------------------------------------ validate impl A against official vectors
print("\n[2] Implementation A vs official BIP-39 test vectors (Trezor's vectors.json)")
try:
    url = "https://raw.githubusercontent.com/trezor/python-mnemonic/master/vectors.json"
    with urllib.request.urlopen(url, timeout=20) as r:
        vectors = json.load(r)["english"]
    ok = fail = 0
    for entropy_hex, expected_mnemonic, *_rest in vectors:
        got = bip39_from_entropy_scratch(bytes.fromhex(entropy_hex), trezor_wordlist)
        if got == expected_mnemonic:
            ok += 1
        else:
            fail += 1
            print(f"    MISMATCH on {entropy_hex}")
    print(f"    {ok} passed, {fail} failed  (official vectors: entropy -> mnemonic)")
except Exception as e:
    print(f"    could not fetch official vectors ({e!r}); skipping this check")

# --------------------------------------------- the published SeedSigner vectors
print("\n[3] SeedSigner's published dice vectors, three independent implementations")
for label, (rolls, expected) in (("99 rolls / 24 words", VEC_99), ("50 rolls / 12 words", VEC_50)):
    num_words = len(expected.split())
    entropy = seedsigner_dice_to_entropy(rolls, num_words)

    a = bip39_from_entropy_scratch(entropy, trezor_wordlist)
    b = trezor.to_mnemonic(entropy)
    c = embit_bip39.mnemonic_from_bytes(entropy)

    print(f"\n    {label}   ({len(rolls)} rolls -> {len(entropy)} entropy bytes)")
    print(f"      sha256(rolls) = {hashlib.sha256(rolls.encode()).hexdigest()}")
    print(f"      entropy used  = {entropy.hex()}")
    print(f"      A from-scratch  == published : {a == expected}")
    print(f"      B trezor ref    == published : {b == expected}")
    print(f"      C embit (ships) == published : {c == expected}")
    print(f"      all three agree              : {a == b == c}")
    if a != expected:
        print(f"      GOT      : {a}")
        print(f"      EXPECTED : {expected}")

# ------------------------------------------------- fingerprint cross-check
print("\n[4] Master fingerprint cross-check (50-roll vector)")
try:
    from embit import bip32
    seed = embit_bip39.mnemonic_to_seed(
        unicodedata.normalize("NFKD", VEC_50[1]), password=""
    )
    root = bip32.HDKey.from_seed(seed)
    fp = root.my_fingerprint.hex()
    print(f"    derived fingerprint = {fp}")
    print(f"    published           = {VEC_50_FINGERPRINT}")
    print(f"    match               : {fp == VEC_50_FINGERPRINT}")
except Exception as e:
    print(f"    could not derive ({e!r})")

# ---------------------------------------- confirm the 6->0 remap is NOT applied
print("\n[5] Confirming the documented incompatibility with 'dice' (base-6) mode")
remapped = VEC_50[0].replace("6", "0")
alt = bip39_from_entropy_scratch(
    hashlib.sha256(remapped.encode()).digest()[:16], trezor_wordlist
)
print(f"    rolls with 6->0 remap produce a DIFFERENT mnemonic: {alt != VEC_50[1]}")
print("    (this is why the docs say to use Hex mode, not Dice mode, on iancoleman.io)")
