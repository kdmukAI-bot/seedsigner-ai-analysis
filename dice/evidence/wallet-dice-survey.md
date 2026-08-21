# Survey: Dice-Roll Entropy Implementations Across Bitcoin Wallets

**Date:** 2026-08-03, substantially revised 2026-08-04, extended 2026-08-11
**Method:** All findings below are read directly from public source code fetched from GitHub (`raw.githubusercontent.com` + GitHub code search). No claims are taken from documentation or marketing except where explicitly labeled. Each repo is pinned to the HEAD commit fetched on the survey date; line numbers refer to those commits.

> **Revision note (2026-08-04).** The original section 8 of this survey concluded that BitBox02,
> Jade, Passport and several other devices had "no dice-roll entropy feature." **That conclusion was
> wrong for at least three of them, and the error was methodological.** The survey tested for
> dice arithmetic in firmware, found none, and stopped. It did not check vendor documentation, where
> BitBox and Blockstream both publish first-party dice procedures with printed lookup tables.
>
> Two further gaps: **Keystone was never examined at all** and turns out to be a shipping hardware
> wallet with an on-device dice path that is *not* interoperable with the reference, and
> **AirGap Vault** implements the reference recipe alongside a mode misleadingly named after
> Coldcard.
>
> Sections 1 to 7 were re-checked and stand. Section 8 is replaced by sections 8 to 11 below, which
> use a four-way taxonomy instead of a yes/no test.

> **Extension note (2026-08-11).** The published document moved from a four-way class taxonomy to a
> per-method chart, because several implementations occupy more than one class at once and a single
> letter could not say so. Nothing in sections 1 to 12 was overturned. What this pass added:
>
> 1. **Kern** was classified from source but never written up. Section 13 does that, at tag `0.0.15`.
> 2. **The final-word affordance is far more common than class (c) implied.** All four devices that
>    implement the reference construction, SeedSigner, Coldcard, Krux and Kern, also restrict the
>    last word of a typed-in phrase to checksum-valid choices. Verified from source in each case,
>    section 14. The paper-table method therefore works on devices whose vendors never mention it,
>    which is why the chart separates *completes a hand-built phrase* from *vendor publishes a dice
>    worksheet*.
> 3. **SeedSigner's coin-flip path and Calc Final Word tool** were not covered before. Section 14.
> 4. **Jade's dice guide has been retrieved**, so the rolls-per-word scheme is no longer unverified.
>    Section 15, and the "Not fully verified" entry is retired.
> 5. **Sparrow and Specter DIY move out of the class (d) summary row**, where they were still listed
>    despite sections 11 and 12 placing them elsewhere.

> **Extension note (2026-08-18).** Two additions, one of which corrects a claim that had gone stale
> between survey and publication. Nothing in sections 1 to 16 was overturned.
>
> 1. **Bowser** (`lnbits/hardware-wallet`) was never examined, and the class (d) listing in
>    section 12 was stale. It implements the reference construction exactly and requires **100
>    rolls rather than 99**, which is the only thing separating it from SeedSigner and is enough to
>    break interoperability. Section 17. It is **not charted on the published page**, which covers
>    the established implementations; this survey records the reading regardless.
> 2. **Passport Prime is no longer class (d).** KeyOS `v1.3.1` (2026-08-07) added a final-word
>    affordance that did not exist at `v1.3.0`, the commit this survey pinned. Section 18. The
>    section 11 note and the summary table are corrected accordingly. Prime and Core reach the same
>    behavior by separate codebases, so the published page carries them as one entry citing both
>    sources; the differences below are recorded here rather than there, because none of them
>    changes what a reader does.

## Taxonomy used from the revision onward

| Class | Meaning |
|---|---|
| **(a)** | Device/tool hashes the raw ASCII rolls: the reference recipe. Interoperable. |
| **(b)** | Device/tool does dice arithmetic, but a different construction. Not interoperable. |
| **(c)** | Device does no dice arithmetic; the user maps rolls to words from a printed table. The device's contribution is computing the checksum-valid final word. |
| **(d)** | No dice affordance at all. Typing in an externally computed phrase does not count, since nearly every wallet accepts that. |

**Reference construction (SeedSigner):** concatenate the ASCII digit characters `'1'`–`'6'` of exactly 50 (12 words) or 99 (24 words) D6 rolls with no delimiter; compute a single SHA-256 over that byte string; truncate the digest to the first 16 bytes for 12 words (full 32 bytes for 24); feed to `embit.bip39.mnemonic_from_bytes()`.

## Pinned commits

| Repo | Branch @ commit |
|---|---|
| `SeedSigner/seedsigner` | `dev` @ `1fb2956322ea978428a6a96b955baa93e965c877` |
| `Coldcard/firmware` | `master` @ `c849c4e04a978335937a0fd0c96e76f5bd70bbb6` |
| `selfcustody/krux` | `main` @ `7ea3f95eff1eafa5c159f951425ee537df2a08c2` |
| `iancoleman/bip39` | `master` @ `de71c22328b24e0848bbe1bd12ac8974ca83b5b8` |
| `BitcoinQnA/seedtool` | `main` @ `dac9c8880d45fef4f5c5fceda5ec6fc899ea386a` |
| `BlueWallet/BlueWallet` | `master` @ `635cfc2c1517c61695b1ceea07eb147455a9494f` |
| `BlockchainCommons/seedtool-cli` | `master` @ `b79d02fb6d936921dd36c08c3994bfd155ee7288` |
| `Blockstream/Jade` | `master` @ `cfce08ced9f58ed0244e516f1d7f0c61a82889ee` |
| `Foundation-Devices/passport2` | `main` @ `2ac5658394b9a924dfb5201b0e5bae36acedccf9` |
| `Foundation-Devices/passport-firmware` | `main` @ `e985d0a0a2097715147091186f35e4aac393f5e0` |
| `BitBoxSwiss/bitbox02-firmware` | `master` @ `833236c81e831b8aa95271dda2c0301ca609817a` |
| `cryptoadvance/specter-diy` | `master` @ `eb8397d2b53bfe43cec0571f8efa235aa352d8ec` |
| `trezor/trezor-firmware` | `main` @ `8c04a8fbdfe950e5913ceb3fe4a7c94add191bca` |
| `spesmilo/electrum` | `master` @ `b1aa52d701eb826d3c68ae9c03737cc05163c0e2` |
| `sparrowwallet/sparrow` | `master` @ `1a00e2ef3a4601c2b1bac869e577487a176a9792` |
| `nunchuk-io/libnunchuk` | `main` @ `f5d0acc091b517a77c8c9aa51c2d389361eec9eb` |
| `wizardsardine/liana` | `master` @ `6ef57fb6212f8b7874dc985962b39fee853e4126` |
| `SatoshiPortal/bullbitcoin-mobile` | `main` @ `33a1ff1e94fe4d45069690953aa8a5bf21350f1b` |

### Added in the 2026-08-04 revision, pinned to release tags where available

| Repo | Tag @ commit |
|---|---|
| `KeystoneHQ/keystone3-firmware` | `3.0.2` @ `c224a7f5164cce07bf13885d7664afd99bed11a0` |
| `KeystoneHQ/Keystone-cold-app` | @ `34e638fa57aed6a54051f9fe065d501c3e129581` |
| `BitBoxSwiss/bitbox02-firmware` | `firmware/v9.26.4` @ `6c18aa9cebcc457c3c5cd2c36ce58268a16bede5` |
| `Blockstream/Jade` | `1.0.40` @ `bbab28775a73e1f19339808affa8370e006205d6` |
| `Foundation-Devices/passport2` | `v2.3.11` @ `2ac5658394b9a924dfb5201b0e5bae36acedccf9` |
| `Foundation-Devices/KeyOS` | @ `425c9791007146d46355478b3ec321f2321ab226` |
| `airgap-it/airgap-vault` | @ `aa50b7f0371ed2e681f358d22b546c7c000e05b7` |
| `BlockchainCommons/GordianSeedTool-iOS` | `releases/universal/1.6` @ `ec0a86f256e6761ce0511453ecb5f9ab6686c8f5` |
| `trezor/trezor-firmware` | `core/v2.12.4` @ `30be4e8c9488eeab68f994af23b3d9c9b7334266` |
| `trezor/trezor-firmware` | `legacy/v1.14.1` @ `725c0c01879329900f08fc453d8fd0fcb4d86090` |
| `keepkey/keepkey-firmware` | `v7.14.1` @ `5482e7366a36e81336074f53a9defb6cff45ed72` |
| `OneKeyHQ/firmware` | `touch` @ `e99ba63809cd175d86649c9a3bfe75f4ff7952c2` |
| `LedgerHQ/ledger-secure-sdk` | @ `c2816ab60ebfdd8b6d03203ad310aa4c53ecb727` |
| `BlueWallet/BlueWallet` | `8.0.1` @ `0a53056a636370073a58d6cdd6de5c0728e5926a` |
| `sparrowwallet/sparrow` | `2.5.3` @ `0dce4783ef463c9985fd4ff814280209545bebc3` |
| `wizardsardine/liana` | `v15.0` @ `4684d5cb0c75471ae40f43dffc78333ac74afb38` |
| `bitcoin/bitcoin` | `v31.1` @ `9be056a8a72b624dae9623b2f7bded92c2a21c91` |
| `WalletWasabi/WalletWasabi` | @ `27e6e7c860461cd98df4123e8c06e0d159382d63` |
| `Blockstream/green_qt` | @ `5aaf284ba54ad04221ed0935243f5a16d189bb0d` |
| `cryptoadvance/specter-diy` | `v1.10.4` @ `fa7d46d72ccc4fe3912d74ceb99358f13c3609ea` |

### Added in the 2026-08-18 extension

| Repo | Tag @ commit |
|---|---|
| `lnbits/hardware-wallet` | `v0.8.1` @ `06ee5374dc211e518f8775002756432de3d8a712` |
| `Foundation-Devices/KeyOS` | `v1.3.1` @ `de966a11e88d28f116b52509679c19eb33591711` |

---

## 1. SeedSigner (reference)

`src/seedsigner/helpers/mnemonic_generation.py` (dev @ `1fb2956`), lines 17-18 and 64-81:

```python
DICE__NUM_ROLLS__12WORD = 50
DICE__NUM_ROLLS__24WORD = 99
...
def generate_mnemonic_from_dice(roll_data: str, wordlist_language_code: str = SettingsConstants.WORDLIST_LANGUAGE__ENGLISH) -> list[str]:
    """
        Takes a string of 50 or 99 dice rolls and returns a 12- or 24-word mnemonic.

        Uses the iancoleman.io/bip39 and bitcoiner.guide/seed "Base 10" or "Hex" mode approach:
        * dice rolls are treated as string data.
        * hashed via SHA256.

        Important note: This method is NOT compatible with iancoleman's "Dice" mode.
    """
    entropy_bytes = hashlib.sha256(roll_data.encode()).digest()

    if len(roll_data) == DICE__NUM_ROLLS__12WORD:
        # 12-word mnemonic; only use 128bits / 16 bytes
        entropy_bytes = entropy_bytes[:16]

    # Return as a list
    return bip39.mnemonic_from_bytes(entropy_bytes, wordlist=Seed.get_wordlist(wordlist_language_code)).split()
```

- Input: ASCII digits `'1'`–`'6'`, no remap, no delimiter. Exactly 50 or 99 rolls (UI enforces exact counts). D6 only.
- Single SHA-256 over the whole string; first-16-bytes truncation for 12 words.
- No statistical quality guard on the rolls.
- Its own docstring already flags the iancoleman "Dice"-mode incompatibility.

---

## 2. Coldcard (`Coldcard/firmware`) — HAS DICE — byte-identical to SeedSigner

`shared/seed.py` (master @ `c849c4e`).

**Hashing** — incremental SHA-256 over the ASCII keypresses, seeded with the prior seed (empty for a pure dice seed). Lines 380-424 (excerpted):

```python
async def add_dice_rolls(count, seed, judge_them, nwords=None, enforce=False):
    ...
    # None is for papaer wallet private key - as it is 32 bytes of entropy we need 99 D6
    if nwords in (24, None):
        threshold = 99
        sec_bit = 256
    else:
        threshold = 50
        sec_bit = 128

    counter = {}
    md = sha256(seed)
    ...
        if ch in '123456':
            count += 1
            counter[ch] = counter.get(ch, 0) + 1  # mimics defaultdict
            ...
            md.update(ch)
```

`new_from_dice` (lines 471-484) starts with `seed = b''`, so `md = sha256(b'')` then `md.update(ch)` per keypress — mathematically identical to `sha256(whole_roll_string)`. Truncation for 12 words happens in `approve_word_list` (lines 657-660):

```python
    if nwords == 12:
        seed = seed[0:16]

    words = bip39.b2a_words(seed).split(' ')
```

**Roll-count policy:** threshold 50 (12w) / 99 (24w). In the new-seed flow (`enforce=True`) too-few rolls forces "add more or exit"; in the ephemeral-seed flow the user may confirm past the warning (lines 434-449).

**Historical defect, now fixed (added 2026-08-11).** Roll-count enforcement and the distribution
check both arrive in commit `2bbe27fa52e940bfef2a0a42b290c23e2d93b6db` (2023-01-20), *"add dice
rolls distribution check and enforce it in case of main seed generation, enforce number of dice
rolls for main seed generation"*. Before it, `add_dice_rolls` had no `nwords`/`enforce` parameters
and the count was advisory in every flow:

```python
        elif ch == 'y':
            if count < 99 and judge_them:
                if not count:
                    return 0, seed
                ok = await ux_confirm('''You only provided %d dice rolls, ...''' % count)
                if not ok: continue
```

The only refusal is `if not count` (zero rolls), so **a single roll could be confirmed into a
seed**. Verified present in the original dice commit `7878c4815` (2019-07-03), so the
window runs from the feature's introduction to January 2023, roughly three and a half years.

**And enforcement is path-specific even after the fix.** `enforce=True` is passed only on the
main seed-generation flow; the ephemeral-seed flow still shows the warning and lets the user
confirm past it. Independent corroboration: Crypto Guide, *"Cracking Unsafe Bitcoin Wallets +
Coldcard Mk4 Warning (Insecure Dice Based Seeds & Private Keys)"*, 2023-10-31,
`https://youtu.be/oj_W3xOlt6U?t=328` (channel `@CryptoGuide`, 598 s). Its description states the
video searches the chain for wallets "likely created using low numbers of dicerolls", reports funds
lost, and demos "how this can still happen with Coldcard Mk4, even running the latest firmware";
chapter markers include "03:51 Ongoing risk for low numbers of dice rolls" and "05:15 Coldcard Mk4
Issues & Warning". **Sourcing note:** title, channel, upload date, description and chapter list were
read from the video page metadata. The demonstration itself was not verified here, because YouTube's
caption endpoint returns empty without a token, so the on-screen claims are attributed rather than
checked. This
parallels Keystone's missing 24-word gate (section 8) and is the same class of defect.

**Bias guard** (lines 451-455):

```python
            if judge_them:
                bad_dist = any((v / count) > 0.30 for _, v in counter.items())
                if bad_dist:
                    bad_dist_msg = ("Distribution of dice rolls is not random. "
                                    "Some numbers occurred more than 30% of the time.")
```

With `enforce=True` a bad distribution aborts outright; otherwise the user may confirm past it.

**Extra mode:** from the TRNG-generated word list screen, "Press (4) to add some dice rolls into the mix" (lines 662, 677-682) — reruns `add_dice_rolls(0, seed, False)` with the 32-byte TRNG seed as the initial hash state, i.e. `sha256(trng_seed ∥ rolls)`. This mixed mode has no SeedSigner counterpart.

**Host verification script** `docs/rolls.py` (public domain, in the same repo) reproduces the construction in ~20 lines: `h = sha256(input().strip().encode()).digest()`, warns if input length < 99 (`2.585 * len` bits), warns on the empty-string hash `e3b0c442...`, and prints the 24 words.

**Verdict: EQUIVALENT.** Same rolls → same seed as SeedSigner (both 12w and 24w), verified from source. Incremental `md.update()` vs. one-shot hash is a non-difference. Coldcard additionally has the >30% face-frequency guard and the mix-with-TRNG mode, which SeedSigner lacks.

---

## 3. Krux (`selfcustody/krux`) — HAS DICE (D6 + D20) — D6 byte-identical to SeedSigner

`src/krux/pages/new_mnemonic/dice_rolls.py` (main @ `7ea3f95`).

**Constants** (lines 42-47):

```python
D6_12W_MIN_ROLLS = 50
D6_24W_MIN_ROLLS = 99
D20_12W_MIN_ROLLS = 30
D20_24W_MIN_ROLLS = 60
MIN_ENTROPY_12W = 128
MIN_ENTROPY_24W = 256
```

**Roll string** (lines 308-309): rolls are stored as strings (`D6_STATES = [str(i + 1) for i in range(6)]`, face values 1-6 as typed — no remap) and joined:

```python
            entropy = (
                "".join(self.rolls) if self.num_sides < 10 else "-".join(self.rolls)
            )
```

So D6 → `"31452..."` (no delimiter, identical to SeedSigner); D20 → `"3-17-20-..."` (dash-delimited, faces 1-20 as decimal text).

**Hash + truncation** (lines 335-348):

```python
            import hashlib
            import binascii

            entropy_bytes = entropy.encode()
            entropy_hash = binascii.hexlify(
                hashlib.sha256(entropy_bytes).digest()
            ).decode()
            ...  # displays "SHA256 of rolls:" on screen
            num_bytes = 32 if len_mnemonic == 24 else 16
            return hashlib.sha256(entropy_bytes).digest()[:num_bytes]
```

**Mnemonic conversion** — `src/krux/pages/login.py` lines 105-116:

```python
    def new_key_from_dice(self, d_20=False):
        """Create a new key from dice rolls"""
        from .new_mnemonic.dice_rolls import DiceEntropy
        dice_entropy = DiceEntropy(self.ctx, d_20)
        captured_entropy = dice_entropy.new_key()
        if captured_entropy is not None:
            from embit.bip39 import mnemonic_from_bytes
            words = mnemonic_from_bytes(captured_entropy).split()
```

Same `embit` call SeedSigner uses.

**Quality guards** (stronger than Coldcard's, warn-and-proceed):
- Shannon-entropy progress bar: computed over the face-frequency distribution, must reach 128/256 bits minus a 2-bit tolerance or the user gets a "Poor entropy!" warning with "Proceed anyway?" (lines 83-93, 288-306).
- Pattern detection: Shannon entropy of successive roll *derivatives* (differences), flags arithmetic progressions like "123456123456..." with "Pattern detected!" + "Proceed anyway?" (lines 95-125).
- "Stats for Nerds" screen shows the roll distribution bar graph and Shannon entropy (lines 127-173).

**Roll counts:** minimums 50/99 (D6) and 30/60 (D20); the user may keep rolling beyond the minimum (loop only exits on Go).

**Verdict: D6 EQUIVALENT** — with exactly 50 or 99 rolls, Krux D6 produces byte-identical entropy and the same mnemonic as SeedSigner. (Krux permits >min rolls; SeedSigner requires exactly 50/99, so only the exact-count case is comparable.) **D20 has no SeedSigner counterpart** (dash-delimited multi-digit faces).

---

## 4. iancoleman.io/bip39 (`iancoleman/bip39`) — HAS DICE — NOT equivalent

`src/js/entropy.js` and `src/js/index.js` (master @ `de71c22`).

**Dice mode remaps 6→0.** `entropy.js` lines 183-202:

```javascript
    this.fromString = function(rawEntropyStr, baseStr) {
        var base = getBase(rawEntropyStr, baseStr);
        // Convert dice to base6 entropy (ie 1-6 to 0-5)
        // This is done by changing all 6s to 0s
        if (base.str == "dice") {
            var newEvents = [];
            for (var i=0; i<base.events.length; i++) {
                var c = base.events[i];
                if ("12345".indexOf(c) > -1) {
                    newEvents[i] = base.events[i];
                }
                else {
                    newEvents[i] = "0";
                }
            }
            base.str = "base 6 (dice)";
```

The remapped events then feed **two different paths** depending on the "Mnemonic Length" dropdown (`src/index.html` lines 117-124 — default is `<option value="raw" selected>Use Raw Entropy (3 words per 32 bits)</option>`):

**(a) Default "raw" mode — no hashing at all.** Each remapped digit maps to a variable-length bit string (`entropy.js` lines 43-50):

```javascript
    "base 6 (dice)": {
        "0": "00", // equivalent to 0 in base 6
        "1": "01",
        "2": "10",
        "3": "11",
        "4": "0",
        "5": "1",
    },
```

The concatenated bits are used directly as BIP39 entropy; `index.js` lines 1919-1922 keep the **last** multiple-of-32-bits (`var start = bits.length - bitsToUse; var binaryStr = bits.substring(start);`) and word count varies with rolls.

**(b) Fixed 12/24-word mode — SHA-256 of the remapped digit string.** `index.js` lines 1892-1906:

```javascript
        // Use entropy hash if not using raw entropy
        var bits = entropy.binaryStr;
        var mnemonicLength = DOM.entropyMnemonicLength.val();
        if (mnemonicLength != "raw") {
            // Get bits by hashing entropy with SHA256
            var hash = sjcl.hash.sha256.hash(entropy.cleanStr);
            ...
            var numberOfBits = 32 * mnemonicLength / 3;
            bits = bits.substring(0, numberOfBits);
```

Here `entropy.cleanStr` is the events joined **after** the 6→0 remap. So even the hashed mode's SHA-256 preimage differs from SeedSigner's whenever the rolls contain a 6 — with 50 random rolls that is a >99.98% probability (1 − (5/6)^50). Truncation direction (first 128 bits for 12 words) matches SeedSigner.

**Hex mode** (what SeedSigner's docs use for verification): hex characters map directly to their 4-bit nibbles (`entropy.js` lines 69-86); in the default raw mode the pasted digest bytes become the BIP39 entropy with **no further hashing**, so pasting SeedSigner's displayed SHA-256 digest (or its first 32 hex chars for 12 words) reproduces SeedSigner's mnemonic. In non-raw mode the hex *string* would be SHA-256-hashed again — a verifier must use raw mode (the default).

**Roll counts / guards:** no minimum enforced; non-raw mode shows "The mnemonic will appear more secure than it really is" when supplied bits < needed (lines 1907-1913) but still generates. No distribution guard (zxcvbn-style feedback only in the entropy stats display).

**Verdict: NOT equivalent** in dice mode (either sub-mode): default raw mode is an unhashed variable-length bit encoding, and the hashed mode's preimage has 6s remapped to 0s. Hex-raw mode is the correct external verification path for SeedSigner digests.

---

## 5. bitcoiner.guide/seed — Seed Tool (`BitcoinQnA/seedtool`) — HAS DICE — hashed mode byte-identical to SeedSigner

README confirms the online instance is https://bitcoiner.guide/seed. Derived from iancoleman ("Based on Ian Coleman's bip39 tool", `src/www/js/lib/entropy.js` header) **but the dice handling differs in the critical detail: no 6→0 remap.**

`src/www/js/lib/entropy.js` (main @ `dac9c88`) defines the dice bit map directly on faces 1-6 (lines 75-82):

```javascript
    dice: {
      1: '00', // equivalent to 0 in base 6
      2: '01',
      3: '10',
      4: '11',
      5: '0',
      6: '1',
    },
```

and `fromString` performs **no remap step**; `cleanStr = base.events.join('')` (line 308) is the raw filtered `'1'`–`'6'` string exactly as typed.

**Hashed mode** (Mnemonic Length = 12/24 words; **default is 12 words**, `src/www/dev.html` lines 452-459): `src/www/js/dom.js` lines 2449-2509:

```javascript
const hash = async (text, algo = 'SHA-256') => {
  const msgUint8 = new TextEncoder().encode(text);
  const hashBuffer = await crypto.subtle.digest(algo, msgUint8);
  ...
};
...
  // Use biased bits to allow 99 dice roll
  const bits = Math.ceil(entropy.base.bitsPerEvent * entropy.base.events.length);
  ...
  // Refuse to make a seed with insufficient entropy
  if ((mnemonicLength / 3) * 32 > bits) {
    DOM.entropyWeakEntropyOverrideWarning.classList.remove('hidden');
    return;
  }
  ...
  // Get bits by hashing entropy with SHA256
  let hex = await hash(entropy.cleanStr);
  ...
  const end = (mnemonicLength * 8) / 3;
  const hexedBin = hex.slice(0, end);
  const phrase = window.bip39.entropyToMnemonic(hexedBin);
```

That is: SHA-256 over the UTF-8 bytes of the raw roll string, first 32 hex chars (16 bytes) for 12 words / 64 (32 bytes) for 24 — **the same construction as SeedSigner**. The `Math.ceil(log2(6)·n)` biased-bit gate makes the minimums exactly 50 rolls (⌈129.2⌉=130 ≥ 128) for 12 words and 99 rolls (⌈255.9⌉=256 ≥ 256) for 24 — matching SeedSigner's counts. Insufficient rolls are *refused*, not just warned; a separate "Unbiased entropy is too low" warning appears when the debiased bit count is below target.

**Raw mode** (selectable): unhashed variable-length bits per the table above, first 256 bits, multiple-of-32 required (lines 2526-2545). Note its bit table (face k → the encoding of k−1... i.e. 1→'00' ... 6→'1') differs from iancoleman's post-remap table (6→'00', 1→'01', ...), so even the two tools' *raw* dice modes disagree with each other.

**Verdict: EQUIVALENT in its default hashed mode** (12- or 24-word Mnemonic Length, dice input): same rolls → same mnemonic as SeedSigner. Seed Tool accepts ≥50/≥99 rolls while SeedSigner requires exactly 50/99, so the comparison applies at the exact counts. Raw mode is NOT equivalent. No face-frequency guard.

---

## 6. BlueWallet (`BlueWallet/BlueWallet`) — HAS DICE (coin, D6, D20) — NOT equivalent

`screen/wallets/ProvideEntropy.tsx` (master @ `635cfc2`). No hashing anywhere: rolls are **bit-packed** into a big integer.

Faces are pushed **0-indexed** (line 201: `onPress={() => push(getEntropy(i, sides))}` while displaying face `i + 1`), so face k contributes value k−1. `getEntropy` (lines 103-125) implements a variable-length debiasing encoding: for D6, values 0-3 → 2 bits, values 4-5 → 1 bit; for D20, values 0-15 → 4 bits, 16-19 → 2 bits; coin → 1 bit. The reducer (lines 63-78) left-shifts the accumulator and adds each value, capping at 128 bits (12 words) or 256 bits (24 words); a final roll that overflows the cap is right-shifted to fit (lines 71-74).

On save (lines 292-324), the packed bits are cut to whole bytes (`convertToBuffer`, lines 128-152) and — critically — **any shortfall is filled with system RNG** after a confirmation dialog:

```typescript
            if (remaining > 0) {
              const random = await randomBytes(remaining);
              buf = concatUint8Arrays([buf, random], bufLength);
            }
```

The resulting 16/32 bytes go through `bip39.entropyToMnemonic` (`class/wallets/abstract-hd-electrum-wallet.ts` lines 173-178).

**Roll counts:** no minimum — with average ~1.66 bits/roll (D6), filling 256 bits takes ~154 rolls; fewer rolls means RNG-completed entropy (disclosed in the dialog: "X bytes generated, Y remaining"). No distribution guard.

**Verdict: NOT equivalent.** Unhashed bit-packing with 0-indexed faces, possible RNG fill, and cap-overflow truncation — same physical rolls cannot reproduce a SeedSigner seed. (Curiosity: its D6 value→bits table coincides with BitcoinQnA Seed Tool's raw-mode table, but the packing/fill semantics differ.)

---

## 7. Gordian seedtool-cli (`BlockchainCommons/seedtool-cli`) — HAS DICE — same construction as SeedSigner

Not a wallet, but a Bitcoin-ecosystem (Blockchain Commons) seed tool with a `--in dice` format. `src/format-dice.cpp` (master @ `b79d02f`), entire input path:

```cpp
void FormatDice::process_input(Params* p) {
    auto input = p->get_one_argument();

    #if 0
    auto entropy = digits_to_data(input, 1, 6);
    p->seed = deterministic_random(entropy, p->count);
    #else
    // Compatibility with https://iancoleman.io/bip39/
    digits_to_data(input, 1, 6); // syntax check only
    p->seed = sha256_deterministic_random(input, p->count);
    #endif
}
```

`src/random.cpp` lines 56-69: `sha256_deterministic_random(string, n)` = SHA-256 over the raw ASCII string, then `take(seed, n)` (first n bytes; throws if n > 32). `digits_to_data(input, 1, 6)` (`src/utils.cpp` lines 103-113) rejects any character outside `'1'`–`'6'` (so `'0'` is invalid — dice faces are kept as-is, **no 6→0 remap**). Default `count` is 16 bytes (`src/params.cpp` lines 27-37); BIP39 output requires 16/32 for 12/24 words.

**Verdict: same construction as SeedSigner** — `SHA256(ascii_rolls)[:16]` or `[:32]` — despite the comment claiming iancoleman compatibility. Because iancoleman remaps 6→0 before hashing and seedtool-cli does not, the two agree **only** for roll strings containing no 6s; for any string with a 6, seedtool-cli actually matches SeedSigner/Coldcard, not iancoleman. No roll-count minimum or distribution guard in the dice path.

---

## 8. Keystone (`KeystoneHQ/keystone3-firmware`) — HAS DICE, class (b) — the 6→0 remap in hardware

Not examined in the original survey. Pinned to tag `3.0.2` = `c224a7f5164cce07bf13885d7664afd99bed11a0`.

`src/ui/gui_widgets/gui_dice_rolls_widgets.c`, `ConfirmHandler`, lines 329-339 (fetched and read directly):

```c
    for (size_t i = 0; i < rollsLen; i++) {
        char c = temp[i];
        if (c < '1' || c > '6') {
            ASSERT(false);
        }
        if (c == '6') {
            temp[i] = '0';
        }
    }
    uint8_t hash[32] = {0};
    sha256((struct sha256 *)hash, temp, rollsLen);
```

Truncation and BIP-39 encoding, `src/ui/gui_model/gui_model.c` lines 497-506:

```c
        if (mnemonicNum == 24 && SecretCacheGetDiceRollsLen() < 100) {
            ret = ERR_GENERAL_FAIL;
            break;
        }
        entropyLen = (mnemonicNum == 24) ? 32 : 16;
        hash = SecretCacheGetDiceRollHash();
        memcpy_s(entropy, sizeof(entropy), hash, entropyLen);
        SecretCacheSetEntropy(entropy, entropyLen);

        ret = bip39_mnemonic_from_bytes(NULL, entropy, entropyLen, &mnemonic);
```

So: `entropy = SHA256(remap6to0(rolls))[:16 or :32]`. Structurally the reference recipe, different alphabet.

- **Roll counts:** ≥50 for 12 words; **≥100 for 24 words**, hard-enforced (`ERR_GENERAL_FAIL`). Note this rejects the reference's 99. Keystone's own user documentation still says 99; the firmware demands 100.
- **Guard:** a "Lack of randomness" label appears if any face exceeds 30% of rolls, but `g_confirmValid` is set solely by the length test, so the warning is advisory and Confirm stays live.
- **Mixing:** none. Pure dice, no device RNG contribution, fully deterministic.
- **Provenance:** the legacy Android codebase states the intent outright. `KeystoneHQ/Keystone-cold-app` @ `34e638fa57aed6a54051f9fe065d501c3e129581`, `SetupVaultViewModel.java:396-405`: `//Use the same algorithm as https://iancoleman.io/bip39/` followed by `rolls.append(b % 6)`. Keystone deliberately targets iancoleman's Dice mode.
- **Historical defect, now fixed:** at tag `2.1.6` and earlier there was no roll-count gate on the 24-word path, so 50 rolls (~129 bits) could produce a phrase presented as 256-bit. Fixed in `2.5.0` (2026-06-29), changelog entry: "Improved Dice Roll Entropy Validation."
- Dice present since the first dice release, `1.2.6` (2024-01-10), verified at tag `ab278833c6144b031f63b912775832828b8ce87e`.

**Verdict: NOT equivalent.** Independently reproduced (see `verification` note at the end of this document): the reference's published 99-roll vector yields `eyebrow obvious such suggest…` under raw ASCII and `police guard reject concert…` under Keystone's remap, with **zero words in common**. The two agree only for roll strings containing no 6: P = (5/6)^50 ≈ 1 in 9,100 at 50 rolls, ≈ 1 in 69,000,000 at 99.

---

## 9. AirGap Vault (`airgap-it/airgap-vault`) — HAS DICE, class (a) *and* (b)

Not examined in the original survey. Pinned to `aa50b7f0371ed2e681f358d22b546c7c000e05b7`.

`src/app/services/dice-roll/dice-roll.service.ts`:

```ts
export enum DiceRollType {
  DEFAULT = 0, // Iancoleman, Cobo Vault
  COLDCARD = 1
}
...
async transformEntropy(diceEntropy: string, type: DiceRollType): Promise<string> {
    if (type === DiceRollType.COLDCARD) {
      return diceEntropy.replace(/6/g, '0')
    }
    return diceEntropy
}
...
const hash: Uint8Array = createHash('sha256').update(transformedEntropy).digest()
```

- **`DEFAULT` mode is the reference recipe**, bit-identical.
- **`COLDCARD` mode applies the 6→0 remap, which Coldcard does not do.** The label is wrong. A user selecting it because they own a Coldcard gets a seed their Coldcard cannot reproduce. Cross-checked against `Coldcard/firmware` `shared/seed.py`, which has no remap (see section 2).
- **Roll count:** 99 minimum, hard-gated; **24 words only**, no 50-roll/12-word path. Rolls beyond 99 are accepted, which takes the user off the canonical vector.
- **Guard:** rejects the empty-string hash explicitly; no face-frequency check.

## 10. Gordian Seed Tool for iOS (`BlockchainCommons/GordianSeedTool-iOS`) — HAS DICE, class (a), 12-word only

Listed as "not fully verified" in the original survey. Now verified at `ec0a86f256e6761ce0511453ecb5f9ab6686c8f5` (tag `releases/universal/1.6`), `SeedTool/Entropy/Tokens/DieToken.swift:84-91`:

```swift
extension DieToken: SeedProducer {
    static func seed(values: [DieToken]) -> Data {
        let string = Self.string(from: values)
        let data = string.utf8Data
        let digest = data.sha256()
        return digest[0..<16]
    }
}
```

Faces `1`-`6` only, bare ASCII digits, no remap or separator. **The `[0..<16]` truncation is unconditional, so there is no 24-word dice path**, and no roll count is enforced. The sibling `BitToken.swift:62-69` does the same over `'0'`/`'1'` for coin flips. `CardToken.swift:169-178` does **not** follow the recipe (it seeds a PRNG), and the app's own manual says card entropy is not iancoleman-compatible.

## 11. Devices that support dice by printed lookup table (class (c))

These do no dice arithmetic. The user maps rolls to words on paper; the device computes the checksum-valid final word, which is the step that is impractical by hand. **This is the category the original survey got wrong.**

### BitBox02 (`BitBoxSwiss/bitbox02-firmware`)

First-party documentation, fetched directly:
- `https://bitbox.swiss/bitbox02/BitBox_Diceware_HowTo.pdf` (sha256 `ecdf7d6054f45ae8e33bef091c1168f181a248fb512b680e6e3a97db09cae667`)
- `https://bitbox.swiss/bitbox02/BitBox_Diceware_LookupTable.pdf` (sha256 `9db3c8986b20737a3b76207a0fb325fec17fb3221aac32d2df470c2615e37535`, 4 pages, dated 2021-01-24, CC BY-SA 4.0)

Procedure, verbatim from the lookup table header: *"Roll your dice 5 times, repeating a specific roll if you get a 5 or 6. The 6th time roll a dice or flip a coin to get the recovery word."*

The table decodes to a plain positional encoding, independently verified against the canonical BIP-39 English wordlist:

```
word_index = (d1-1)*512 + (d2-1)*128 + (d3-1)*32 + (d4-1)*8 + (d5-1)*2 + coin
   di in {1,2,3,4} (D6 rerolled until <= 4);  coin = 0 or 1
```

Spot-checks reproduce: `(1,1,1,1,1)+0 → 0 → abandon`; `(1,1,1,1,1)+1 → 1 → ability`; `(2,1,1,1,1)+0 → 512 → divorce`; `(4,4,4,4,4)+1 → 2047 → zoo`. That is exactly 11 uniform bits per word. **No hashing anywhere.**

Device side, pinned to tag `firmware/v9.26.4` = `6c18aa9cebcc457c3c5cd2c36ce58268a16bede5`, `src/rust/bitbox02-rust/src/workflow/mnemonic.rs:293-308`:

```rust
    // For the last word, we can restrict to a subset of bip39 words that fulfil the
    // checksum requirement. This special case exists so that users can generate a seed
    // using only the device and no external software, allowing seed generation via dice
    // throws, for example.
```

`lastword_choices` (lines 111-166) enumerates candidates: 8 for 24 words, 128 for 12. The SHA-256 in that function is the BIP-39 checksum, **not** entropy derivation. Shipped in **v9.4.0** (2021-01-19), five days before the lookup table PDF was dated; unchanged through v9.26.4. Restore path (`hww/api/restore.rs:108-136`) stores the typed entropy unmodified; no host entropy is XORed in on that path.

**Entropy accounting:** 23 words × 11 bits = 253 bits from dice. The 24th word contributes 3 further seed bits **chosen by the human from an 8-item menu**, not by dice.

### Blockstream Jade (`Blockstream/Jade`)

First-party documentation, fetched: [Create a recovery phrase using dice](https://help.blockstream.com/blockstream-jade/add-more-security-functionality/create-a-recovery-phrase-using-dice) (updated 2026-05-11), which instructs the user to consult a downloadable **lookup table** and type 11 or 23 words into the device.

Source at tag `1.0.40` = `bbab28775a73e1f19339808affa8370e006205d6`, `main/process/mnemonic.c:572` (`valid_final_words()`) brute-forces the wordlist keeping every checksum-valid candidate; gated to Advanced mode and the final word only at line 658; line 674 asserts the candidate count exactly: `JADE_ASSERT(num_filter_words == (nwords == 12 ? 128 : 8));`.

Jade's own generator uses `get_random` (`main/keychain.c:281`), an RNG pool fed by AXP192 sensor reads, cycle counters and `esp_fill_random`. CompactSeedQR import is still present at `main/process/mnemonic.c:1060-1062`, which is a carry path for a seed made elsewhere, **not** dice support.

**Caveat:** the vendor's own dice guide attachment (`hc/article_attachments/21328564164505`) returns 404, so Jade's rolls-per-word scheme could not be read. UNVERIFIED whether it matches BitBox's.

### Foundation Passport (`Foundation-Devices/passport2`)

Documentation, fetched: [docs.foundation.xyz/passport/setup/](https://docs.foundation.xyz/passport/setup/) — *"From firmware version 2.3.0, Passport Core can now help advanced users generate their own seed by picking random words from the BIP39 list. After entering the first 11 or 23 words, Passport Core shows a Generate Final Word option."* The 2.3.0 release blog names dice explicitly, as a caution: *"…unless you are an advanced user that understands the risks with manual seed generation via dice rolls etc."*

**Important difference from Jade and BitBox02.** Passport's version is not a pure checksum calculator. At tag `v2.3.11` = `2ac5658394b9a924dfb5201b0e5bae36acedccf9`, `ports/stm32/boards/Passport/modules/predictive_utils.py:63-77`:

```python
# choose a random last word
index_bytes = bytearray(4)
common.noise.random_bytes(index_bytes, common.noise.ALL)
index = int.from_bytes(index_bytes, "little") % SEED_WORD_LIST_LENGTH
```

The device **picks** the final word using its own RNG rather than showing the valid options. So the residual entropy bits of the last word are the device's, not the user's.

Guard: `modules/utils.py:1554` `insufficient_randomness()` warns if any word repeats more than twice.

**Passport gen 1 never had Coldcard's dice flow.** At `v1.1.0` = `e985d0a0a2097715147091186f35e4aac393f5e0`, zero hits for `add_dice_rolls`/`dice_rolls`/`roll_dice`, and no dice commit anywhere in repo history. It was never present, not removed. **Passport Prime** runs a separate codebase (`Foundation-Devices/KeyOS`). At `v1.3.0` = `425c9791007146d46355478b3ec321f2321ab226`, the commit originally surveyed, it had zero dice hits and no final-word feature: class (d). **That is no longer current.** `v1.3.1` added one; see section 18. Prime still has no dice arithmetic, so it is class (c) on the same terms as Passport Core.

> A commit adding a "Custom Entropy" option under "Create Seed" exists
> (`1f1e3494eb6edfc0ff5697cef526dc06c7d07834`) but is **in zero tags and not an ancestor of HEAD**.
> It never shipped. Anyone grepping git history could easily mis-report this.

---

## 12. Wallets with NO dice-roll entropy feature (class (d))

> **Jade, Passport and BitBox02 have been moved to section 11.** They are class (c), not (d). The
> entries that stood here were the survey's central error.

- **Trezor** (`trezor-firmware` @ tag `core/v2.12.4` = `30be4e8c9488eeab68f994af23b3d9c9b7334266`): no dice entry in firmware. `core/src/apps/management/reset_device/__init__.py` L88/L103/L350-355 generate 32 bytes of internal RNG and SHA-256 them with host-supplied external entropy; `legacy/firmware/reset.c` (tag `legacy/v1.14.1`) is identical in structure. **The internal RNG is mixed in unconditionally**, so even a custom host tool injecting dice bytes yields `SHA256(device_RNG ‖ dice)`, never `SHA256(dice_ascii)`. Host entropy is always CSPRNG: `trezorlib` `device.py:324-325` → `secrets.token_bytes(32)`; Suite `verifyEntropy.ts:10-16` → `randomBytes`. Re-verified by full working-tree grep at every tag, all 20 CHANGELOGs, and all `core/translations/*.json` (a dice UI would need translation strings; there are none). Corroborating: firmware issue **#23 "diceware/cointoss initialization"** has been open since 2018-09-26 and unimplemented, and issue **#1293** carries a 2026-08-01 user comment describing the manual 11/23-word grind. Trezor's "Advanced recovery" is a blind-keypad *input* method for an existing seed, not advanced creation.
- **Ledger** (Nano S/S Plus/X, Stax, Flex): **firmware is closed source; this conclusion is documentation-sourced, not source-verified.** The public SDK cannot answer the question, and that itself is informative: `ledger-secure-sdk/include/os_seed.h` exposes only derivation from an already-onboarded seed, and there is no `os_perso_set_seed`/onboarding syscall in public code at all. First-party docs are consistent: [Donjon](https://donjon.ledger.com/threat-model/os-random-number-generation/) — *"a True Random Number Generator is used for seed generation"*; [Ledger Academy](https://www.ledger.com/academy/topics/security/what-is-the-entropy) — *"your entropy is generated by the True Random Number Generator… inside the device's Secure Element."* No host contribution, unlike Trezor. Zero dice hits across `app-bitcoin-new`, `ledger-secure-sdk` (the 5 hits are a fuzzer local variable), `app-recovery-check`, and `ledger-live`. Note `support.ledger.com` is now a JS-only SPA returning a content-free shell for every path, so support-article quotes come from Wayback captures.
- **KeepKey** (`keepkey/keepkey-firmware` @ tag `v7.14.1` = `5482e7366a36e81336074f53a9defb6cff45ed72`): a Trezor fork with the same formula, `lib/firmware/reset.c:86,139-143`. Zero `dice` hits in the whole tree and across all refs' commit messages; all **67** GitHub releases swept, no matches. One difference worth recording: `fsm_msgLoadDevice` is **not** debug-gated (`lib/firmware/fsm_msg_common.h:502-528`), so production firmware will accept an arbitrary host-supplied mnemonic, making the manual route easier than on Trezor.
- **OneKey** (`OneKeyHQ/firmware` @ `e99ba63809cd175d86649c9a3bfe75f4ff7952c2`): a Trezor fork that did **not** add a dice path; seed creation is the unmodified `reset_device` flow. Grep for `user_entropy|custom_entropy|manual_entropy|external_entropy` across all firmware source returns zero, as does a sweep of 5 non-default branches and all 9 CHANGELOGs. Its **"Use multiple sources of entropy"** advanced option is *two silicon RNGs* (MCU TRNG plus secure element), not user input. Two traps: OneKey's marketing describes its TRNG as *"a dice-rolling machine kept in a safe"*, and `bip39.onekey.so` is a **fork of iancoleman's tool** (per its `package.json` repository field) that does have dice input, but it is a web page, not the wallet.
- **Electrum** (`spesmilo/electrum` @ `b1aa52d`): no dice; `make_seed` (`electrum/mnemonic.py:201`) draws only from `secrets.randbelow`, and `extra_entropy` appears **zero** times in the tree. Electrum also cannot *generate* a BIP-39 seed at all, only import one. **Live caveat:** lead maintainer SomberNight wrote PR **#8839** *"mnemonic.make_seed: add 'extra_entropy' arg"* (2024-01-22, body explicitly contemplating dice), confirmed via API as `state: open, merged: false`, untouched since 2024-04-08. A custom-entropy option existed historically and was removed twice (`e0c38b31`, then `5e5134b7` around v3.1.2). If #8839 merges, Electrum becomes class (b), never (a), since the input would be XOR-mixed with OS randomness.
- **Sparrow** (`sparrowwallet/sparrow` @ tag `2.5.3` = `0dce4783ef463c9985fd4ff814280209545bebc3`): no dice. `MnemonicKeystoreEntryPane.generateNew():57-70` uses `SecureRandom.getInstanceStrong()` only. Maintainer craigraw declined the feature in [sparrow#1351](https://github.com/sparrowwallet/sparrow/issues/1351): *"I don't think adding such features to Sparrow would be a net positive - indeed the reverse."* Two near-misses to not mistake for dice: `CardImportPane.java:203-226` has a user-entropy text box, but it is **SHA-256d** and becomes the *chain code* for Tapsigner/Satochip/Keycard setup, producing no mnemonic; and **Border Wallets** (`MnemonicGridDialog`) is a memorability scheme whose grid shuffle comes from machine RNG. **Reclassified to (c)**: the reading above is about dice *arithmetic*, of which there is none, but the checksum-valid final-word autosuggest on the seed-entry path is the class (c) affordance. See the summary table.
- **Nunchuk** (`libnunchuk` @ `f5d0acc`): no dice. `SoftwareSigner::GenerateMnemonic` (`src/softwaresigner.cpp:67-69`) calls trezor-crypto's `mnemonic_generate`, verified at submodule SHA `b957dfbddb4222c5f9e573f3d4dc21fcbc6ff3a9` to be `random_buffer(data, 32)`. The public API has no entropy parameter. Same Tapsigner chain-code near-miss as Sparrow. **`nunchuk-io/nunchuk-ios` returns 404, so the iOS app is closed source**; that platform is inference from the shared core.
- **Liana** (`wizardsardine/liana` @ tag `v15.0` = `4684d5cb0c75471ae40f43dffc78333ac74afb38`): no dice. `liana/src/signer.rs:116-121` uses `random::random_bytes()` (RDRAND + `getrandom` + contextual data, SHA-256 mixed); no user-input path in library, CLI or GUI. Decisively, Wizardsardine's own [Coldcard RNG advisory](https://wizardsardine.com/blog/coldcard-rng-vulnerability/) (2026-08-01) tells users to *"generate a new seed with dice on the Coldcard(s)"*, framing dice as a Coldcard capability.
- **Bitcoin Core** (@ tag `v31.1` = `9be056a8a72b624dae9623b2f7bded92c2a21c91`): a *structural* no. `grep -rniI "bip39\|mnemonic"` over the whole repo returns **0** — Core does not implement BIP-39 in any form, so there is no seed for dice to feed. `sethdseed`, the last RPC accepting user-chosen key material, was removed with legacy wallets in v30.0.
- **Wasabi** (`WalletWasabi/WalletWasabi` @ `27e6e7c860461cd98df4123e8c06e0d159382d63`): no dice. `KeyManager.cs:205` uses NBitcoin's CSPRNG constructor. Two traps: Wasabi's docs *do* teach dice, but for the **Diceware passphrase**, not the seed; and Wasabi says "entropy" constantly in the coinjoin-privacy sense. Requested and never built: #3720 (closed 2023 with no PR) and **#14901, opened 2026-08-04** with no maintainer response.
- **Blockstream Green** (`green_qt` @ `5aaf284ba54ad04221ed0935243f5a16d189bb0d`): no dice, provable at the API level. GDK's public header declares `GDK_API int GA_generate_mnemonic(char** output);` — **output pointer only, no input parameter**, so no caller can supply entropy, and "entropy" appears zero times in `gdk.h`. Blockstream's dice article is for **Jade the device** (section 11), not the app.
- **Bull Bitcoin mobile** (`SatoshiPortal/bullbitcoin-mobile` @ `33a1ff1`): no dice feature found (hits are Italian localization — "dice" means "says" in Italian — and BIP85 tables).
- **Specter DIY** (`cryptoadvance/specter-diy` @ tag `v1.10.4` = `fa7d46d72ccc4fe3912d74ceb99358f13c3609ea`): no dice, and the documented feature is **coin flips**, not dice. `grep -c dice` over the entire tree is **0**; the product page says *"Added Entropy — Use coin-flips to introduce extra randomness to key generation."* The 11-bit toggle keypad (`src/gui/screens/mnemonic.py:93`, place-values 1…1024) lets a user set any word's bits by hand with checksum auto-fix (`helpers.py:27-30`). Three precision points: there is **no XOR anywhere in the mnemonic path** (the maintainer's "XOR" is arithmetic the user does on paper), the toggled bits become entropy **directly and unhashed**, and **untouched words remain TRNG output** with no accounting. Secondary sources claiming Specter DIY takes dice input on-device are conflating coin flips with dice. **Reclassified to (c)**: hand-set word bits with checksum auto-fix is the same affordance as class (c), reached with coin flips rather than a dice table, and the untouched-words-stay-TRNG behavior is why the published chart also marks it as blending in the device's own entropy.
- **Commercial hardware wallets, all class (d), none offering on-device dice or coin entropy:** Bitkey (`@cf16705`, no BIP-39 in the hardware path at all — 32 raw bytes into BIP-32), Cypherock X1 (`@5b11739`), Prokey (`@484d7b2` — note `firmware/reset.c:109-114` *is* a SHA-256→BIP-39 construction, but 32 bytes of device TRNG are unconditionally prepended), Satochip (`@8cbaa1d`, card never generates a seed), SecuX (`@3795a26`), SafePal (`@09ee73c`), ELLIPAL Joy (`@a672896`). Closed firmware, inferred from complete documented flows: Tangem, NGRAVE ZERO (its `zero-firmware` repo is an empty 60-byte placeholder), Ellipal Titan, D'CENT, Arculus (75-article help corpus, zero hits for dice/coin flip/entropy), Ballet (no BIP-39 at all).
- **Open DIY signers, all class (d):** Portal `@a084b3a`, ~~Bowser `@f0013ea`~~ (**superseded**: Bowser shipped a dice path by `v0.8.1`, see section 17), Frostsnap `@6030ccb`, catcard `@a8d52b0` (dice explicitly *planned*, `docs/ENTROPY.md:148`), keep-esp32 `@f195c74`.

**Caveat on negative findings.** These conclusions now rest on cloned working-tree greps, release-note sweeps and first-party documentation, not on GitHub code search alone. **The original survey's method was not sufficient**, and the specific failure modes are worth recording because they cut both ways:

- A case-insensitive grep for `dice` produces overwhelming **false positives**: "in**dice**s" dominates (Passport ~340 hits, Bitcoin Core 242, nunchuk-android 295, libnunchuk 139), plus BIP-39 English word #492 is literally `dice`, `codice`/`índice` fill Italian, Spanish and Portuguese localization files, and Spanish *"que dice"* means "which says". Also `\broll` matches "scroll" and `d6` matches hex strings.
- A word-boundary grep produces the **false negative that caused this revision**: vendors whose dice support is a published PDF plus a checksum-word feature leave no dice string in the firmware at all.

The only method that gets both right is reading the seed-creation path, the release notes, **and** the vendor's own documentation.

## 13. Kern (`odudex/Kern`) — HAS DICE, class (a)

Classified from source when the published document first listed it, but never written up here.
Verified at tag `0.0.15`, fetched 2026-08-11.

`main/pages/new_mnemonic/dice_rolls.c`:

```c
#define MIN_ROLLS_12_WORDS 50
#define MIN_ROLLS_24_WORDS 99
#define MAX_ROLLS 256
...
  if (dice_value >= '1' && dice_value <= '6' && rolls_count < MAX_ROLLS) {
...
  if (wally_sha256((const unsigned char *)rolls_string, rolls_count, hash,
...
  ret = bip39_mnemonic_from_bytes(NULL, hash, entropy_len, &mnemonic)
```

- Keypad offers faces `1`-`6` only (`"1","2","3","\n","4","5","6"`), stored as typed, no remap, no
  delimiter. D6 only; no D20 path, unlike Krux despite the shared author.
- `wally_sha256` over the roll string, then `entropy_len` of 16 or 32 bytes. Same construction as
  SeedSigner.
- **Roll counts are minimums, not exact counts**: `min_rolls = (word_count == 12) ? 50 : 99` and up
  to `MAX_ROLLS` 256. Rolling past the minimum leaves the published vectors, as with Krux.
- No statistical guard on the rolls.

**Verdict: EQUIVALENT** at exactly 50 or 99 rolls.

---

## 14. The final-word affordance outside class (c)

Section 11 treated "the device computes the checksum-valid final word" as the defining feature of
the paper-table class. That was too narrow. The same affordance is present on every class (a) device
surveyed, where it falls out of ordinary seed entry rather than being built for dice. The difference
that survives is **documentation**: BitBox02 and Blockstream Jade publish the lookup table the
method needs, and the others do not.

| Implementation | Where | What it does |
|---|---|---|
| **SeedSigner** | `views/tools_views.py` `ToolsCalcFinalWord*` @ `0.8.7` | A dedicated Calc Final Word tool. The user enters 11 or 23 words, then supplies the last word's spare bits (7 bits at 12 words, 3 at 24) one of three ways: `COIN_FLIPS`, `SELECT_WORD` (any BIP-39 word, whose index supplies the bits), or `ZEROS`. The device then replaces the trailing bits with the checksum. |
| **Coldcard** | `shared/seed.py` `WordNestMenu` L232-261 @ `3238f6fd` | On the last word of a typed-in phrase, offers only `bip39.a2b_words_guess(words)`, i.e. the 8 valid candidates at 24 words and 128 at 12. |
| **Krux** | `pages/mnemonic_editor.py` L266-273 @ `7ea3f95` | `Key.get_final_word_candidates(...)` constrains autocomplete to checksum-valid words when the last word of a new mnemonic is entered. |
| **Kern** | `pages/load_mnemonic/manual_input.c` + `new_mnemonic/new_mnemonic_menu.c` L92-94 @ `0.0.15` | `manual_input_page_create(..., checksum_filter_last_word)` is called with `true` from the **New Mnemonic → words** flow; the last word's candidate list is filtered to valid checksums. |

**SeedSigner also has a coin-flip generation path**, not previously recorded here.
`helpers/mnemonic_generation.py` L85-101 @ `0.8.7`: `generate_mnemonic_from_coin_flips` takes 128 or
256 characters of `'0'`/`'1'`, hashes the string with SHA-256 and truncates to 16 bytes at 128 flips.
That is the reference construction over a binary alphabet, matching iancoleman and Seed Tool's
"Binary" mode, and it is why the chart records coin as well as dice for SeedSigner.

**Scope of this finding.** It was checked on the signing devices, where a seed is generated and the
question matters. It was **not** established for the software tools and apps, and the published chart
marks those cells as not established rather than guessing.

---

## 15. Jade's dice guide, retrieved

The 2026-08-04 revision could not read Jade's rolls-per-word scheme because the attachment linked
from the help article returned 404. The guide is now served from a different host and was fetched on
2026-08-11:

- `https://storage.googleapis.com/dxp-production-assets/content/blockstream-jade/add-more-security-functionality/create-a-recovery-phrase-using-dice/JadeDiceRollsGuide.pdf`
- sha256 `5aa832156e75a5bc947b191deca243abd27350d85cd0587dc0c582079fcf64d6`, 17 pages, PDF creation
  date 2023-02-28.

Verbatim from page 1:

> 1) Acquire (2) 16-sided dice and (1) 8-sided dice.
> 2) Roll D1, D2, and D3 simultaneously - then use the lookup table to find the corresponding word
> that matches your results.
> 3) For example: if D1 rolls a "10", D2 rolls a "9", and D3 rolls an "8" - then your resulting word
> is ocean.
> 4) Repeat this process until you have either 11 or 23 words, then use the Calculate feature on
> Blockstream Jade to choose a valid final word.

The table decodes to `word_index = (D1-1)*128 + (D2-1)*8 + (D3-1)`, covering 16x16x8 = 2048 exactly,
so there is no rerolling and no coin flip. Independently checked against the canonical BIP-39 English
wordlist: the guide's own example (10, 9, 8) gives 1223 = `ocean`; (1,1,1) = 0 = `abandon`;
(1,5,1) = 32 = `advice`; (1,13,1) = 96 = `army`; (16,16,8) = 2047 = `zoo`.

**This is not BitBox02's scheme.** BitBox02 uses five rejection-sampled D6 plus a coin flip per
word; Jade uses two D16 and one D8 with no rejection step. A transcript from one is meaningless to
the other. Both arrive at 11 uniform bits per word.

---

## Not fully verified

- ~~**Jade's dice lookup table**~~ RESOLVED 2026-08-11: the guide was retrieved from its new host and read. See section 15. It does **not** match BitBox02's scheme.
- **Ledger's BOLOS onboarding code** is closed source and has never been published. The class (d) verdict there is documentation-sourced and cannot be source-verified by anyone outside Ledger.
- **Nunchuk iOS** (`nunchuk-io/nunchuk-ios`) returns 404; the iOS UI is closed source.
- **`BlockchainCommons/seedtool.info`** is a WASM build of seedtool-cli; its `docs/index.html` has zero dice occurrences, so all dice behavior lives inside `seedtool.wasm`, which was not disassembled.
- **Krux/Coldcard release-tag drift:** sections 2 and 3 quote default-branch HEADs, not release tags. A claim about a specific shipped firmware version should re-verify against that version's tag.
- **Repository provenance noise:** a search for dice-to-BIP-39 tools surfaced roughly 45 repositories created between 2026-08-01 and 2026-08-04 with zero stars, a burst consistent with low-quality or generated churn. None is cited here. In particular `jsgoyette/seed-from-rolls` implements the recipe correctly but was created hours before it was found, so it is evidence of nothing about ecosystem practice.

---

## Independent verification of the constructions

A from-scratch BIP-39 encoder (standard library only, no wallet code) was validated against 5 official BIP-39 test vectors, then used to check the claims above. Script: `dice/evidence/verify_constructions.py`. Results:

- The document's published vectors reproduce exactly: 50 rolls → `hole luggage safe present…`, 99 rolls → `eyebrow obvious such suggest…`.
- The same 99 rolls under Keystone's 6→0 remap give `police guard reject concert…`, with **0 of 24 words in common**. 17 of the 99 digits are rewritten.
- BitBox02's positional table decodes correctly against the canonical wordlist across its full range: index 0 → `abandon`, 2047 → `zoo`.

---

## Summary comparison

| Tool | Class | Construction | Same rolls → same seed as SeedSigner? |
|---|---|---|---|
| SeedSigner | (a) | SHA256(ASCII '1'-'6'), truncate 16B for 12w | (reference) |
| Coldcard | (a) | Incremental SHA256 over same ASCII chars; `seed[0:16]` for 12w | **YES** (byte-identical) |
| Krux | (a) | D6: identical string+SHA256+truncation, via embit; D20: dash-joined | **YES (D6)**; D20 n/a |
| Kern | (a) | `wally_sha256(ASCII rolls)`, 16/32 bytes; min 50/99, max 256 | **YES** (at exactly 50/99) |
| AirGap Vault, default mode | (a) | SHA256(raw ASCII rolls); 99 rolls, 24 words only | **YES** |
| Gordian Seed Tool (iOS) | (a) | SHA256(raw ASCII rolls)`[0:16]`, unconditional; 12 words only | **YES (12w)**; no 24w path |
| Gordian seedtool-cli | (a) | SHA256(raw ASCII rolls), first N bytes | **YES** (construction) |
| bitcoiner.guide Seed Tool | (a) | Hashed mode: SHA256(raw ASCII rolls), first 16/32B | **YES** (hashed mode); raw mode NO |
| **Bowser** (LNbits) | **(a) construction, (b) outcome** | `wally_sha256(ASCII rolls)`, full 32B; **exactly 100 rolls, 24 words only** | **NO** (roll count alone; the arithmetic is identical) |
| **Keystone** | **(b)** | **Remaps 6→0, then SHA256 + truncate. 100 rolls for 24w** | **NO** (0/24 words match) |
| AirGap Vault, "Coldcard" mode | (b) | Remaps 6→0, then SHA256. Misnamed; Coldcard does not do this | **NO** |
| iancoleman.io, Dice mode | (b) | Remaps 6→0; default sub-mode does not hash at all | **NO** (both sub-modes) |
| BlueWallet | (b) | Unhashed bit packing, 0-indexed faces, RNG fills shortfall | **NO**, and not reproducible twice |
| **BitBox02** | **(c)** | Paper table, 5 rejection-sampled dice + coin = 11 bits/word; device solves word 24 | **NO** (no hashing at all) |
| **Blockstream Jade** | **(c)** | Paper table; device shows checksum-valid final words | **NO** |
| **Foundation Passport** (Core and Prime) | **(c)** | Paper table; device *picks* the final word with its own RNG. Separate codebases, same behavior; per-product detail in §18 | **NO** |
| **Sparrow** | **(c)** | Autosuggests checksum-valid final words on the seed-entry path; Border Wallets grid, no dice screen | **NO** |
| **Specter DIY** | **(c)** | 11-bit keypad sets any word by hand from coin flips, checksum auto-fixed; untouched words stay TRNG | **NO** |
| Trezor, Ledger, KeepKey, OneKey, Electrum, Nunchuk, Liana, Wasabi, Green, Bitcoin Core, Bull Bitcoin, and the commercial and DIY devices listed in §12 | (d) | — | n/a |
- **The final-word affordance on the software tools and apps** (AirGap Vault, both Gordian tools, Seed Tool, iancoleman.io, BlueWallet, RooSoft/bitcoinlib) was not established. Section 14 checked the signing devices only.

## 16. Third-party dice worksheets (not published by any wallet vendor)

Surveyed 2026-08-15. **This is an open set**: anyone can publish a worksheet, so no count is
claimed and none should be. These are the ones found and checked, not the ones that exist.

Checked against the canonical BIP-39 English wordlist (2048 words, sha256 of the newline-terminated
list `2f5eed53a4727b4bf8880d8f3f199efc90e58503646d9ff8eff3a2ed3b24dbda`, read from
`embit/src/embit/wordlists/bip39.py`).

**Depth of check, stated per worksheet.** `dicebip39`, `taelfrinn`, SeedPicker and RudeFox were
verified **positionally**: every cell's index compared against the wordlist entry it claims.
`reardencode`'s four PDFs were verified for **construction math and wordlist membership** (token
scan plus outcome-count arithmetic), **not** positionally; their two-page print layout defeats
reliable text-order extraction, so a transposition inside a row would not have been caught.

### Pinned sources

| Worksheet | Ref | Artifact |
|---|---|---|
| `sarpulhu/dicebip39` | `main` @ `44cd94ae2393ce9b229f47cd4057b895be008e1c` (Unlicense) | `readme`, plain-text table |
| `reardencode/bip39_dice` | `master` @ `65c830db0e9ebde69509e379980618894a3cd239` (no license) | 4 PDFs, 2pp each |
| `taelfrinn/Bip39-diceware` | `master` @ `5320c9978fe89b5e068f6c0cafe45effe900e74c` (no license) | `coin_plus_d6_bip39.{md,html,pdf}`, 3pp |
| SeedPicker | `https://seedpicker.net/guide/SeedPicker_Lookup_Table.pdf` | 5pp, PDFium, created 2019-01-11 |
| RudeFox | `https://www.rudefox.io/custody/walkthrough/create-seed/lookup-tables.pdf` | 3pp, Acrobat Distiller, created 2020-09-25 |

PDF sha256, as retrieved 2026-08-15:

- reardencode 3d16 `909936c6be29e89bbb850a87ff8ffde5bec4e0038f98768e7c362d3920aae605`
- reardencode 4d8 `5651f7104d6f392f7c61d4fb5687999248b180246b97ebb0c7c7eee4b905f4ed`
- reardencode 1d8 4d4 `86106d28c1705f8023977f2f13a4f8faa98dbbabfda19244e6d8ff6509f242c1`
- reardencode 1coin 5d4 `d80d4dc5a8133551472d541723f62e28642a48722a4dd6b2b6ac0fad0641a7b8`
- taelfrinn `96bf7848fa6adcb0567d3d7fae6379925936b31ad6e5d502ec6834c05ebaf385`
- SeedPicker `f43a5bd810b06b6c736c6a16f3a473f30a81cabee0763fcf473722ee539c533e`
- RudeFox `f5bd56c15a2471413289b42e3ebc3da598dcd9c35a8e2ae681c3937283348c6d`

### Constructions, all VERIFIED against the wordlist

**`sarpulhu/dicebip39` — D6 only, parity + rejection.** One roll sets chart half (odd = top,
even = bottom); five further rolls are taken as 1-4, rerolling any 5 or 6. That is
2 x 4^5 = 2048 exactly. Verbatim: *"Keep rolling until odd/even,X,X,X,X,X is determined."*
All 2048 rows parsed; the enumeration matches parity x 4^5 in order, and the words are the
wordlist in exact order. **No errors found.**

Note the fetched summary of this repo reported *four* trailing rolls, which yields 512 and cannot
address 2048. The source says five. Read the table, not the description.

**`reardencode/bip39_dice` — power-of-2 dice.** Four printable tables. Exact-cover configurations:
1d8+2d16, 1d4+3d8, 1d8+4d4, 1coin+5d4, each 2048 outcomes = 11 bits. Reduced configurations:
3d16, 4d8, 6d4 each produce 4096 and drop the top bit; 4096 is a multiple of 2048, so the
reduction stays uniform. README states the design intent verbatim: *"the numeric value of the
words in the BIP39 wordlist correspond to the binary values produced by the dice."*

**`taelfrinn/Bip39-diceware` — 1 coin + 4d6 with an exact rejection boundary.** Heads addresses
words 1-1296 (all of 6^4); tails addresses 1297-2048, rejecting any tails roll above `4362`.
Verified: 1296 heads + 752 tails = 2048, and `4362` is exactly the 752nd of the 1296 ordered
4d6 combinations. Table is a bijection onto the wordlist (2048 distinct words, set-equal to the
wordlist); sorting heads-then-tails by roll value reproduces wordlist order. The raw file is a
multi-column print layout, so file order is not wordlist order. **No errors found.**
Last word: the README directs the user to try the block of 16 containing it, which is correct
for a 12-word phrase (7 entropy bits + 4 checksum bits in the final word).

**SeedPicker — the dice/word-picking hybrid.** Verbatim from page 1: *"Draw one ticket ➔ Roll the
six sided die ➔ lookup the word and write it on the seed form ➔ Repeat 23 times."* 342 tickets x 6
faces = 2052 cells; words occupy 2048 and the final four cells of ticket T342 read
*"Draw a new ticket!"*, which is rejection sampling down to 2048 exactly. This is the one surveyed
worksheet that combines physical drawing with dice.

**RudeFox — binary grid.** 128 rows (2^7) x 16 columns (2^4) = 2048, row label carries the high 7
bits (`0-000000-XXXX` form), column header the low 4. Grid structure verified. The dice-to-binary
step is documented in the site walkthrough rather than in the PDF, and was **not** verified.

### Finding: spreadsheet corruption in printed lookup tables

Three of the five worksheets ship at least one cell that is not the canonical wordlist entry, and
in every case the corruption is a spreadsheet artifact rather than a transcription slip.

| Worksheet | Bad cells | Canonical | Mechanism |
|---|---|---|---|
| `reardencode/bip39_dice` (all 4 PDFs) | `TRUE` | `true` | Boolean coercion |
| RudeFox | `TRUE`, `FALSE` | `true`, `false` | Boolean coercion |
| SeedPicker | `March`, `October` | `march`, `october` | Proper-noun autocapitalization |
| `sarpulhu/dicebip39` | none | — | Plain text, not a spreadsheet |
| `taelfrinn/Bip39-diceware` | none | — | — |

The mechanism is confirmed rather than inferred for reardencode: its README states the tables
*"were made using a Google Sheet"*. In each reardencode table the corrupted cell sits between
`truck` and `truly`, exactly where `true` belongs, and `false` is unaffected (`false` present,
`FALSE` absent) — consistent with a sheet that coerced one literal and not the other.

**Impact: none, and the earlier draft of this section overstated it.** The canonical wordlist is
lowercase, so `TRUE` is not a BIP-39 word at all. An implementation handed it rejects the phrase
rather than deriving a different seed — verified against `embit`, which raises
`ValueError: Word 'True' is not in the dictionary`. Hardware wallets take word entry through a
lowercase keyboard with autocomplete, so the user types `true` regardless of what the paper says.

The consequence is a tell, not a defect: a table carrying an uncorrected spreadsheet artifact was
never diffed against the wordlist. **The defect that would matter is a different one** — a cell
holding a real BIP-39 word that belongs at another index, which no implementation would question
and which would substitute silently. No table surveyed had one, subject to the depth-of-check note
above (reardencode's four were verified for membership and construction, not positionally).

### Also noted

- **reardencode's 6d4 link is broken.** The README links `./Dice%20Seed%20Words%20-%206d4.pdf`
  (404 at the pinned commit); the file is published as `Dice Seed Words - 1coin 5d4.pdf` (200).
- **reardencode advises testing your dice** and ships `chisq.py` for it, directly contrary to
  this analysis's §2/§4 position that testing cannot pay for itself. Recorded as a documented
  disagreement, not as an error.
- **SeedSigner history**, from reardencode's README: *"In SeedSigner < 0.5.1 you can use 11 or 23
  words, and the device generates a last word (this givs 121 or 253 bits of entropy instead of 128
  or 256)."* Not independently verified here.

### Out of scope: codex32 (BIP-93)

Mention-only. Verified from `bitcoin/bips` `bip-0093.mediawiki`: title *"codex32: Checksummed
SSSS-aware BIP32 seeds"*, authors Leon Olsson Curr and Pearlwort Sneed, and Andrew Poelstra.
Abstract verbatim: *"This document proposes a checksummed base32 format, "codex32", and a standard
for backing up and restoring the master seed of a BIP-0032 hierarchical deterministic wallet using
it."*

It is worksheet-driven and hand-computable, so a reader will reasonably expect it here, but its
output is a BIP-32 master seed rather than a BIP-39 phrase. The BIP carries a rationale section
titled **"Not BIP-0039 Entropy"** explaining that choice, which is the citation for excluding it.
Nothing in this document's method catalog applies to it, and it deserves its own treatment.

### Out of scope: alternate wordlists, and the risk they create for worksheets

Same disposition as codex32 — not analyzed here — but the risk belongs on the page, because every
worksheet in this section is **wordlist-specific** and nothing about a finished phrase says which
list produced it.

Measured 2026-08-15. BIP-39 and SLIP-39 lists read from `embit` @ `691cee340bc47b6b831d911991694a559bca13b9`
(`src/embit/wordlists/{bip39,slip39}.py`); Electrum files from `spesmilo/electrum` @
`a94e460b50bc5afc334ca0d6feead47d3b50539f`.

| Scheme | List size | Bits/word | Relationship to the BIP-39 English list |
|---|---|---|---|
| BIP-39 | 2048 | 11 | reference, sha256 `2f5eed53…3b24dbda` |
| SLIP-39 | 1024 | 10 | different list, sha256 `bcc45553…e601eec3`; 553 words shared |
| Electrum legacy ("old seed") | 1626 | — | different list, from a poetry frequency list |
| Electrum v2 | 2048 | 11 | **byte-identical**, same sha256 `2f5eed53…3b24dbda` |

**SLIP-39 overlaps enough to be mistaken for BIP-39, and agrees with it nowhere.** 553 of its 1024
words also appear in the BIP-39 list, 54% of the SLIP-39 list. **Not one of those 553 sits at the
same index in both lists** (`acid` is 15 in BIP-39 and 1 in SLIP-39; `acquire` 17 and 3; `actress`
22 and 6). A phrase built from shared words looks equally plausible in either system and decodes to
entirely different bits. Both lists have unique 4-letter prefixes, so prefix-based entry does not
disambiguate them either.

**Electrum legacy** uses 1626 words taken from *Wiktionary:Frequency_lists/Contemporary_poetry*
(`electrum/old_mnemonic.py`, `assert n == 1626`), beginning `like, just, love, know, never`. Visibly
not BIP-39, and the encoding is positional in a way BIP-39's is not.

**Electrum v2 is the case that cannot be spotted by eye.** Its `electrum/wordlist/english.txt` is
the BIP-39 English list byte for byte. Validation is not BIP-39's SHA-256 checksum but a version
prefix over an HMAC, from `electrum/mnemonic.py`:

```python
s = hmac_oneshot(b"Seed version", x.encode('utf8'), hashlib.sha512).hex()
return s.startswith(prefix)
```

The two systems are engineered to be mutually exclusive. Electrum's generator explicitly discards
any candidate that would also pass BIP-39, with the comment *"Make sure the mnemonic we generate is
not also a valid bip39 seed by accident"*:

```python
if bip39_is_checksum_valid(seed, wordlist=self.wordlist) == (True, True): continue
```

**Why this matters to a worksheet user.** The output of every table in this section is a BIP-39
phrase and nothing else. Twelve or 24 words drawn from a BIP-39 worksheet are not an Electrum v2
seed, will not validate as one, and if imported through a wallet's BIP-39 path will derive a
different wallet than Electrum's own seed logic would. The reverse also holds. The words carry no
marking, so the only record of which scheme was used is the user's own note of it.

### iancoleman.io: the weak-entropy warning is stale in Dice + fixed-length mode

Source-read 2026-08-16 at the pinned commit already used above,
`iancoleman/bip39` @ `de71c22328b24e0848bbe1bd12ac8974ca83b5b8`.

Following the §19 walkthrough (entropy type Dice, Mnemonic Length 24 Words) raises
*"The mnemonic will appear more secure than it really is"*, and the page rates the input as
sufficient for only 15 words. **The warning is a false positive in this state.** It should not be
re-filed as a defect in this document's steps.

Two different quantities are in play, from `src/js/index.js` L1893-L1913:

```js
var bits = entropy.binaryStr;
if (mnemonicLength != "raw") {
    var hash = sjcl.hash.sha256.hash(entropy.cleanStr);   // <- seed derives from cleanStr
    ...
    if (mnemonicLength / 3 * 32 > entropy.binaryStr.length) {   // <- warning tests binaryStr
        DOM.entropyWeakEntropyOverrideWarning.removeClass("hidden");
```

- `cleanStr` is the event string after the 6-to-0 rewrite (`src/js/entropy.js` L184-L201), which is
  exactly the §9 construction. This is what gets hashed, and it is what makes Dice + fixed length
  agree with Keystone.
- `binaryStr` is the variable-length packing from the `"base 6 (dice)"` table in `entropy.js` L43-L51:
  faces 1, 2, 3 and the rewritten 6 carry 2 bits, faces 4 and 5 carry 1 bit. That is the §10 method
  and it is what `raw` mode uses.

Computed for this document's published 99-roll vector: `binaryStr` is **167 bits** (1.687 bits per
roll). The threshold is `words/3*32`, so 12 words (128) and 15 words (160) pass, while 18 (192),
21 (224) and 24 (256) trip the warning. That reproduces the observed "15 words" rating exactly.

The rolls themselves carry 99 x log2(6) = **255.9 bits**, all of which reaches the seed through
`sha256(cleanStr)`. The warning compares the request against a conversion the code discarded one
line earlier, so it understates the entropy by the difference between the packing and the hash.

Hex mode raises no warning because `"hexadecimal"` maps every character to exactly 4 bits
(`entropy.js`), so the same 99 characters yield 396 bits and clear 256 outright.

---

## 17. Bowser (`lnbits/hardware-wallet`) — HAS DICE — reference construction at 100 rolls

Pinned to `v0.8.1` = `06ee5374dc211e518f8775002756432de3d8a712`. `wallet/723_cmd_create.ino` is
byte-identical at `main` HEAD `c8c7c694cc50d41452b909329c435674f16eb450`; only `README.md` differs
between the two, so the tag is a safe pin for this reading.

Bowser Wallet is an ESP32 signer built on generic dev boards, with no secure element. The dice path
is reached over an encrypted WebSerial session or from an air-gapped `commands.in.txt` on microSD.

`wallet/100_constants.ino:36`:

```c
const int DICE_ROLL_COUNT = 100;
```

`wallet/723_cmd_create.ino:32-51`:

```c
  char rolls[DICE_ROLL_COUNT];
  int rollCount = collectDiceRolls(rolls, DICE_ROLL_COUNT);
  if (rollCount != DICE_ROLL_COUNT) { /* ... refuse ... */ }

  uint8_t entropy[32];
  if (wally_sha256((uint8_t *)rolls, sizeof(rolls), entropy, sizeof(entropy)) != WALLY_OK) { ... }
  clearSensitiveBytes((uint8_t *)rolls, sizeof(rolls));

  String mnemonic = mnemonicFromBytes(entropy, sizeof(entropy));
```

`mnemonicFromBytes` (`wallet/410_bitcoin.ino:32-39`) calls
`bip39_mnemonic_from_bytes(NULL, entropy, 32, &mnemonic)`. The `NULL` wordlist resolves to English
in the vendored libwally (`libraries/libwally/vendor/src/bip39.c:125`, `w = w ? w : &en_words`).

**Construction, VERIFIED.** Concatenate the ASCII digits `'1'`–`'6'` of exactly 100 D6 rolls with no
delimiter and no remap; take one SHA-256 over the 100-byte buffer; use the **full 32-byte digest**
directly as BIP-39 entropy. 24 words only. There is no 12-word path and no 50-roll path.

**This is the SeedSigner construction with one more roll.** Every step matches the reference: same
ASCII encoding, same single hash, same untruncated digest for 24 words. The roll count is the entire
difference, and it is sufficient to break interoperability, because the hash input is a different
byte string:

```
Rolls  655152231316521321611331544441236164664431121534415633526456254462245546236542364246312613322234612 (+ "4")

SeedSigner, first 99 : eyebrow obvious such suggest poet seven breeze blame virtual frown dynamic
                       donor harsh pigeon express broccoli easy apology scatter force recipe shadow
                       claim radio
Bowser, all 100      : achieve absurd other chef buffalo picnic flower coil evolve style mistake
                       disorder grace include acquire inquiry plug library badge wall mom label
                       toddler equip
```

Truncating a Bowser transcript to its first 99 rolls does not recover the Bowser seed either; it
recovers the SeedSigner seed for that prefix. A Bowser dice transcript reproduces on Bowser alone.

**100 rolls is not a defect.** 100 × log2(6) = 258.496 bits against a 256-bit digest, so the dice
input saturates the seed. SeedSigner's and Coldcard's 99 gives 255.911, a shortfall of 0.089 bits
that is of no practical consequence. Bowser is not unusual in exceeding 256 bits: Keystone also
demands at least 100 for 24 words, and Coldcard allows up to `MAX_ROLLS` 256 above its 99 minimum.
What is unusual is that Bowser requires *exactly* 100, neither more nor fewer. Per pitfall
6, differing from the canonical construction is not a severity finding, and this one is a
reproducibility fact rather than a weakness. The vendor documents the count plainly in `README.md`,
which is the difference from Keystone, whose documentation still says 99 while its firmware requires
100.

**Guards: none beyond the count.** No face-distribution check, no Shannon score, no pattern
detector. The count is hard-gated: `collectDiceRolls` cannot return fewer than
`DICE_ROLL_COUNT` (`*` backspaces, `#` confirms only at 100/100), so the caller's
`rollCount != DICE_ROLL_COUNT` guard is defensive and unreachable.

**Handling.** The roll buffer is zeroized with `clearSensitiveBytes` immediately after hashing, as
are the entropy bytes after the mnemonic is built. Neither the rolls nor the seed words are written
to the microSD card; `commands.out.txt` receives only `/create 1`. Note that `commands.in.txt`
contains the wallet password in the air-gapped flow.

**No final-word affordance: this is NOT class (c).** `wallet/717_cmd_restore.ino:32-35` rejects any
phrase failing `bip39_mnemonic_validate`, so a user cannot enter 23 words and have the device
complete the 24th. Bowser is therefore the only device implementing the hashed construction that
will not finish a hand-built phrase.

**Availability caveat.** Dice entry requires a matrix keypad or a touchscreen
(`executeCreate` returns "Dice input unavailable" when `!BOARD.hasMatrixKeypad &&
!BOARD.hasTouchscreen`). The single-button Waveshare target has no dice path.

**Out of scope but noted:** a separate hardware-RNG path with health checks
(`wallet/rng_health.h`, `deriveHealthyHardwareEntropy()`) and a `/trng` command that draws a
100-bin histogram over 5,000 samples and reports a chi-squared statistic against the NIST
critical values for 99 degrees of freedom. That is RNG diagnostics, not dice, and was not verified.

---

## 18. Passport Prime gains a final-word affordance (KeyOS `v1.3.1`)

**This supersedes the class (d) placement in section 11.** The original reading was correct at the
commit it pinned and became wrong with a firmware release.

Verified at `v1.3.1` = `de966a11e88d28f116b52509679c19eb33591711` (2026-08-07),
`utils/seed-quiz/src/lib.rs:33-67`:

```rust
/// Suggest a checksum-valid final word for a 12- or 24-word entry.
///
/// A random filler word supplies the remaining entropy bits. `from_entropy`
/// recomputes the checksum, and retrying rejects the word already displayed so
/// the result always changes without touching the user's prefix words.
pub fn random_last_word<S: AsRef<str>>(words: &[S]) -> Option<String> {
    let (candidate_count, checksum_bits) = match prefix.len() {
        11 => (128, 4),
        23 => (8, 8),
        ...
```

**The crate did not exist at the previously pinned commit.** `git ls-tree -r v1.3.0` (`425c9791`)
returns no path under `utils/seed-quiz`, and no `random_last_word`/`final_word` symbol appears
anywhere in that tree. This is a new feature, not a missed read.

**It is wired in, not dead code.** `seed_quiz::init_seed_callbacks!(ui)` is invoked from
`os/gui-app-onboarding/src/main.rs:705` and `apps/gui-app-seed-vault/src/callbacks.rs:309`, and
`ui/ui/pages/seed-entry.slint:32` declares `callback suggest-last-word(words: [string]) -> string`
with Generate and Regenerate controls bound to it.

**Class (c), on the same terms as Passport Core.** The device picks one of the valid completions
with its own RNG rather than presenting them, so the last word's residual entropy bits are the
device's. Prime's implementation is the better of the two in one respect: the retry path computes
`random + usize::from(random >= current)` over `candidate_count - 1`, which excludes the word
currently shown, so regenerating always changes the result. Foundation's own maintainer notes that
Core's retry "may repeat a word rather than cycling through all eight"
([passport2#656](https://github.com/Foundation-Devices/passport2/issues/656), 2026-08-02).

**Still no dice arithmetic anywhere in the Foundation codebases.** Checked on 2026-08-18 across
`passport2` (every tag through `v2.4.0-beta-1`, `main`, and all 475 branch names), `KeyOS`
(`v1.3.1` = `main`, all branches), `passport-firmware`, plus org-wide code, commit, PR, and issue
search. The only entropy-related branch, `sft-7320-entropy-hardening` @ `273e24fe` (2026-08-01), is
RNG failure propagation and health checks. The `KeyOS-Releases` `1.4.0-beta1` notes (2026-08-16,
newer than any pushed source) describe entropy hardening as mixing the ATECC608 secure element in as
a third source, with no dice.

First-party statement on the question, from Foundation's Ken Carpenter in passport2#656
(2026-08-02): *"Side note: If we add direct support for dice rolls, this will not be an issue. We
are still discussing the best way we might offer this."*
