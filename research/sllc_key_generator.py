"""Systematic Low Leakage Coding, implemented and tested end to end.

Closes two of the three things W-INTL-110 listed as undone: whether the mask being
response bits changes the error-correction requirement, and whether the scheme composes
with a code this project actually has. Both were beliefs; this makes them tests.
"""
import hashlib, random, sys
sys.path.insert(0, __file__.rsplit('/',1)[0])
from math import comb

M, RED_POLY, T, K = 7, 0x09, 21, 29
N = (1 << M) - 1
MASK = N

def gf_mul(a, b):
    acc = 0
    for i in range(M):
        if (b >> i) & 1: acc ^= a
        a = ((a << 1) ^ RED_POLY) & MASK if (a >> (M-1)) & 1 else (a << 1) & MASK
    return acc
POW = [1]
for _ in range(N-1): POW.append(gf_mul(POW[-1], 2))

def minimal_poly(i):
    """Minimal polynomial of alpha^i over GF(2), as a bit-vector of coefficients."""
    roots, x = [], i
    while True:
        roots.append(x); x = (2*x) % N
        if x == i: break
    poly = [1]                     # coefficients, low order first, over GF(2^m)
    for r in roots:
        ar = POW[r]
        new = [0]*(len(poly)+1)
        for j, c in enumerate(poly):
            new[j]   ^= gf_mul(c, ar)
            new[j+1] ^= c
        poly = new
    assert all(c in (0,1) for c in poly), "minimal polynomial must be binary"
    return poly

def poly_mul_gf2(a, b):
    out = [0]*(len(a)+len(b)-1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i+j] ^= y
    return out

def generator():
    g = [1]
    seen = set()
    for i in range(1, 2*T+1):
        cs = set()
        x = i
        while x not in cs: cs.add(x); x = (2*x) % N
        if cs & seen: continue
        seen |= cs
        g = poly_mul_gf2(g, minimal_poly(i))
    while len(g) > 1 and g[-1] == 0: g.pop()
    return g

G = generator()
DEG = len(G) - 1

# The driver runs under a main guard. This file computed its whole demonstration on
# import - the thing W-INTL-169 recorded as making a module impossible to
# cross-check against - and was the last one in the tree still doing it. The
# tables above stay at module level: they are definitions, not a demonstration.
# W-INTL-218.
if __name__ == "__main__":
    print(f"BCH({N},{K},{T}): generator degree {DEG}, so k = {N-DEG}"
          + ("  OK" if N-DEG == K else f"  MISMATCH, expected {K}"))

    def systematic_parity(info):
        """Remainder of info(x)*x^(n-k) modulo g(x): the systematic redundancy."""
        reg = [0]*DEG
        for b in reversed(info):
            fb = b ^ reg[DEG-1]
            for j in range(DEG-1, 0, -1):
                reg[j] = reg[j-1] ^ (G[j] & fb)
            reg[0] = G[0] & fb
        return reg

    def syndromes(bits):
        out = []
        for j in range(1, 2*T+1):
            s = 0
            for i, b in enumerate(bits):
                if b: s ^= POW[(i*j) % N]
            out.append(s)
        return out

    def bm(syn):
        lam, bee, gamma, ell = [1]+[0]*T, [1]+[0]*T, 1, 0
        for r in range(2*T):
            d = 0
            for j in range(min(ell, T)+1):
                if r+1-j >= 1: d ^= gf_mul(lam[j], syn[r-j])
            new = [gf_mul(gamma, lam[i]) ^ (gf_mul(d, bee[i-1]) if i else 0) for i in range(T+1)]
            if d and 2*ell <= r: bee, gamma, ell = lam[:], d, r+1-ell
            else: bee = [0]+bee[:-1]
            lam = new
        return lam, ell

    def chien(lam, deg):
        pos = []
        for c in range(N):
            tot = 0
            for k in range(T+1):
                if lam[k]: tot ^= gf_mul(lam[k], POW[(k*c) % N])
            if tot == 0: pos.append((N-c) % N)
        return pos if len(pos) == deg else None

    # ── the check that the generator is right: a codeword must have zero syndromes ──
    rng = random.Random(5)
    info = [rng.randint(0,1) for _ in range(K)]
    cw = info + systematic_parity(info)
    assert len(cw) == N
    print(f"systematic codeword syndromes all zero: {not any(syndromes(cw))}")
    print(f"first k bits equal the information bits: {cw[:K] == info}")

    def sllc_enrol(response):
        """response is n bits. First k are the key part, the rest the mask."""
        info, mask = response[:K], response[K:]
        red = systematic_parity(info)
        hd = [a ^ b for a, b in zip(red, mask)]
        return hd

    def sllc_reconstruct(noisy, hd):
        info_n, mask_n = noisy[:K], noisy[K:]
        red_n = [a ^ b for a, b in zip(hd, mask_n)]
        word = info_n + red_n
        syn = syndromes(word)
        if not any(syn): return word[:K]
        lam, deg = bm(syn)
        if deg > T: return None
        pos = chien(lam, deg)
        if pos is None: return None
        for p in pos: word[p] ^= 1
        return word[:K]

    # ── the helper-data manipulation countermeasure ─────────────────────────────
    # W-INTL-116: the field's answer to helper-data manipulation is not to choose a code
    # that resists it, but to fold the helper data into the key - K = S xor f(W). Hiller's
    # implementation hashes the helper data with SPONGENT so that 88 key bits are affected
    # by each helper data bit, corrupting the key the moment the helper data is touched.
    #
    # This project had four loops of an open question about which construction is immune,
    # and the answer is that the question does not arise once this is present. It was
    # absent from every design here. Present now, and tested: the key must survive an
    # honest reconstruction and must not survive a manipulated helper data.

    def key_from(info_blocks, helper_blocks):
        """K = f(S) xor f(W): the secret and the helper data both folded in."""
        s_bytes = bytes(sum((b for b in info_blocks), []))
        w_bytes = bytes(sum((h for h in helper_blocks), []))
        ks = hashlib.sha256(s_bytes).digest()
        kw = hashlib.sha256(w_bytes).digest()
        return bytes(a ^ b for a, b in zip(ks, kw))


    BLOCKS = 5
    print(f"\nSLLC over {BLOCKS} blocks, {N*BLOCKS} raw response bits, "
          f"{K*BLOCKS} key bits before compression")
    print(f"{'ber':>6} {'trials':>7} {'recovered':>10} {'model':>11}")
    for ber, trials in ((0.00, 30), (0.02, 60), (0.04, 200), (0.08, 120)):
        ok = 0
        for _ in range(trials):
            blocks = [[rng.randint(0,1) for _ in range(N)] for _ in range(BLOCKS)]
            hds = [sllc_enrol(b) for b in blocks]
            key = hashlib.sha256(bytes(sum((b[:K] for b in blocks), []))).digest()
            good = True
            for b, hd in zip(blocks, hds):
                noisy = [x ^ (1 if rng.random() < ber else 0) for x in b]
                got = sllc_reconstruct(noisy, hd)
                if got is None or got != b[:K]: good = False; break
            if good: ok += 1
        per = sum(comb(N,i)*ber**i*(1-ber)**(N-i) for i in range(T+1, N+1)) if ber else 0.0
        model = 1-(1-per)**BLOCKS
        print(f"{ber:6.2f} {trials:7d} {ok}/{trials:<8} {model:11.2e}")


    # ── the countermeasure, tested ──────────────────────────────────────────────
    print("\nHelper-data manipulation countermeasure, K = f(S) xor f(W):")
    ok_honest = ok_tamper = 0
    TRIALS = 60
    for _ in range(TRIALS):
        blocks = [[rng.randint(0, 1) for _ in range(N)] for _ in range(BLOCKS)]
        hds = [sllc_enrol(b) for b in blocks]
        key = key_from([b[:K] for b in blocks], hds)

        # honest reconstruction at two percent noise
        rec, good = [], True
        for b, hd in zip(blocks, hds):
            noisy = [x ^ (1 if rng.random() < 0.02 else 0) for x in b]
            got = sllc_reconstruct(noisy, hd)
            if got is None:
                good = False
                break
            rec.append(got)
        if good and key_from(rec, hds) == key:
            ok_honest += 1

        # one helper-data bit flipped, everything else identical
        bad = [h[:] for h in hds]
        bad[0][rng.randrange(len(bad[0]))] ^= 1
        rec2, good2 = [], True
        for b, hd in zip(blocks, bad):
            got = sllc_reconstruct(b[:], hd)
            if got is None:
                good2 = False
                break
            rec2.append(got)
        if not good2 or key_from(rec2, bad) != key:
            ok_tamper += 1

    print(f"  honest reconstruction recovers the key      {ok_honest}/{TRIALS}")
    print(f"  one flipped helper-data bit changes the key {ok_tamper}/{TRIALS}")
    print("  the second line is the property the countermeasure exists for: a tampered")
    print("  helper data must not yield the enrolled key, whatever the decoder does with it")
