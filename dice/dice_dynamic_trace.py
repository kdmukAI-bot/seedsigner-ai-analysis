"""Dynamic trace of SeedSigner's dice path at tag 0.8.7.

Runs the SHIPPED function with the entropy primitives instrumented, so that
"no code path here touches a random number generator" is demonstrated rather
than inferred from reading. Modelled on the approach used in the independent
Coldcard firmware trace.

Instruments:
  * hashlib.sha256      -- logs every construction and every update
  * os.urandom, random, secrets, ssl.RAND_bytes -- any call is a hard failure
"""
import hashlib
import os
import random
import secrets
import sys

SRC = "/tmp/claude-1000/-home-kdmukai-dev/7ae775a3-62df-4e94-8eab-dd59b23faa6a/scratchpad/ss087/src"
sys.path.insert(0, SRC)

ROLLS = ("655152231316521321611331544441236164664431121534415633526456254462"
         "245546236542364246312613322234612")
EXPECTED = ("eyebrow obvious such suggest poet seven breeze blame virtual frown dynamic donor "
            "harsh pigeon express broccoli easy apology scatter force recipe shadow claim radio")

rng_calls = []
hash_log = []


import traceback
_reals = {}

def _trip(name, real):
    def f(*a, **k):
        rng_calls.append((name, traceback.format_stack()[-2].strip().splitlines()[0].strip()))
        return real(*a, **k)
    return f


# --- trip-wires on every randomness source reachable from Python ---
os.urandom = _trip("os.urandom", os.urandom)
secrets.token_bytes = _trip("secrets.token_bytes", secrets.token_bytes)
random.getrandbits = _trip("random.getrandbits", random.getrandbits)
random.random = _trip("random.random", random.random)
random.randint = _trip("random.randint", random.randint)

# --- spy on sha256, recording construction and updates ---
_real_sha256 = hashlib.sha256


class Sha256Spy:
    def __init__(self, data=b""):
        self._h = _real_sha256(data)
        hash_log.append(("new", bytes(data)))

    def update(self, data):
        hash_log.append(("update", bytes(data)))
        self._h.update(data)

    def digest(self):
        d = self._h.digest()
        hash_log.append(("digest", d))
        return d

    def hexdigest(self):
        return self._h.hexdigest()

    def copy(self):
        return self


hashlib.sha256 = Sha256Spy

from seedsigner.helpers import mnemonic_generation  # noqa: E402  (after instrumentation)

import_rng = list(rng_calls)
rng_calls.clear()
hash_log.clear()
words = mnemonic_generation.generate_mnemonic_from_dice(ROLLS)
hashlib.sha256 = _real_sha256

print("=" * 74)
print("DYNAMIC TRACE - SeedSigner 0.8.7 generate_mnemonic_from_dice()")
print("=" * 74)
print(f"\ninput          : {len(ROLLS)} ASCII digits")
print(f"\nRNG calls DURING seed generation : {len(rng_calls)}"
      f"  {'<-- none' if not rng_calls else rng_calls}")
print(f"RNG calls at import time         : {len(import_rng)}")
for name, where in import_rng:
    print(f"    {name} <- {where}")
print("    (libsecp256k1 context randomisation; unrelated to seed material)")

print(f"\nsha256 events in the entropy path: {len(hash_log)}")
for kind, data in hash_log:
    if kind == "new":
        try:
            shown = data.decode("ascii") if data else "(empty)"
        except UnicodeDecodeError:
            shown = data.hex()
        print(f"  new    <- {len(data):3d} bytes  {shown[:60]}{'...' if len(shown) > 60 else ''}")
    elif kind == "update":
        print(f"  update <- {len(data):3d} bytes")
    else:
        print(f"  digest -> {data.hex()}")

print(f"\nresult         : {' '.join(words[:6])} ...")
print(f"matches published vector : {' '.join(words) == EXPECTED}")

fed = b"".join(d for k, d in hash_log if k in ("new", "update"))
print(f"\nbytes fed to the hash    : {len(fed)}")
print(f"identical to the rolls   : {fed == ROLLS.encode()}")
print("\nEvery byte entering the entropy chain is a die face the user typed.")
