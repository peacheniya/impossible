class ECPoint:
    gmpy2 = None
    import gmpy2
    import random
    
    class InvError(Exception):
        def __init__(self, *pargs):
            self.value = pargs
    
    @classmethod
    def Int(cls, x):
        return int(x) if cls.gmpy2 is None else cls.gmpy2.mpz(x)
    
    @classmethod
    def std_point(cls, t):
        if t == 'secp256k1':
            # https://en.bitcoin.it/wiki/Secp256k1
            # https://www.secg.org/sec2-v2.pdf
            p = 0xFFFFFFFF_FFFFFFFF_FFFFFFFF_FFFFFFFF_FFFFFFFF_FFFFFFFF_FFFFFFFE_FFFFFC2F
            a = 0
            b = 7
            x = 0x79BE667E_F9DCBBAC_55A06295_CE870B07_029BFCDB_2DCE28D9_59F2815B_16F81798
            y = 0x483ADA77_26A3C465_5DA4FBFC_0E1108A8_FD17B448_A6855419_9C47D08F_FB10D4B8
            q = 0xFFFFFFFF_FFFFFFFF_FFFFFFFF_FFFFFFFE_BAAEDCE6_AF48A03B_BFD25E8C_D0364141

        return ECPoint(a, b, p, x, y, q = q)
    
    def __init__(self, A, B, N, x, y, *, q = 0, prepare = True):
        if prepare:
            N = self.Int(N)
            A, B, x, y, q = [self.Int(e) % N for e in [A, B, x, y, q]]
            assert (4 * A ** 3 + 27 * B ** 2) % N != 0
            assert (y ** 2 - x ** 3 - A * x - B) % N == 0, (hex(N), hex((y ** 2 - x ** 3 - A * x) % N))
            assert N % 4 == 3
            assert y == pow(x ** 3 + A * x + B, (N + 1) // 4, N)
        self.A, self.B, self.N, self.x, self.y, self.q = A, B, N, x, y, q
    
    def __add__(self, other):
        A, B, N = self.A, self.B, self.N
        Px, Py, Qx, Qy = self.x, self.y, other.x, other.y
        if Px == Qx and Py == Qy:
            s = ((Px * Px * 3 + A) * self.inv(Py * 2, N)) % N
        else:
            s = ((Py - Qy) * self.inv(Px - Qx, N)) % N
        x = (s * s - Px - Qx) % N
        y = (s * (Px - x) - Py) % N
        return ECPoint(A, B, N, x, y, prepare = False)
    
    def __rmul__(self, other):
        assert other >= 1
        if other == 1:
            return self
        other = self.Int(other - 1)
        r = self
        while True:
            if other & 1:
                r = r + self
                if other == 1:
                    return r
            other >>= 1
            self = self + self
    
    @classmethod
    def inv(cls, a, n):
        a %= n
        if cls.gmpy2 is None:
            try:
                return pow(a, -1, n)
            except ValueError:
                import math
                raise cls.InvError(math.gcd(a, n), a, n)
        else:
            g, s, t = cls.gmpy2.gcdext(a, n)
            if g != 1:
                raise cls.InvError(g, a, n)
            return s % n

    def __repr__(self):
        return str(dict(x = self.x, y = self.y, A = self.A, B = self.B, N = self.N, q = self.q))

    def __eq__(self, other):
        for i, (a, b) in enumerate([(self.x, other.x), (self.y, other.y), (self.A, other.A),
                (self.B, other.B), (self.N, other.N), (self.q, other.q)]):
            if a != b:
                return False
        return True
        
def get_pub(priv_key):
    bp = ECPoint.std_point('secp256k1')
    pub = priv_key * bp
    return pub.x, pub.y

def main():
    import hashlib
    # priv_key = int(hashlib.sha3_256(b"Led Zeppelin - No Quarter").hexdigest(), 16)
    priv_key = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    # priv_key = 0xc0b279f18074de51d075b152c8ce78b7bddb284e8cfde19896162abec0a0acce
    print('priv key :', hex(priv_key))
    pubx, puby = get_pub(priv_key)
    print('pub key x:', hex(pubx))
    print('pub key y:', hex(puby))

main()


