from random import randint
import math

# p = 16328632084933010002384055033805457329601614771185955389739167309086214800406465799038583634953752941675645562182498120750264980492381375579367675648771293800310370964745767014243638518442553823973482995267304044326777047662957480269391322789378384619428596446446984694306187644767462460965622580087564339212631775817895958409016676398975671266179637898557687317076177218843233150695157881061257053019133078545928983562221396313169622475509818442661047018436264806901023966236718367204710755935899013750306107738002364137917426595737403871114187750804346564731250609196846638183903982387884578266136503697493474682071
# q = 61329566248342901292543872769978950870633559608669337131139375508370458778917
# g = 14887492224963187634282421537186040801304008017743492304481737382571933937568724473847106029915040150784031882206090286938661464458896494215273989547889201144857352611058572236578734319505128042602372864570426550855201448111746579871811249114781674309062693442442368697449970648232621880001709535143047913661432883287150003429802392229361583608686643243349727791976247247948618930423866180410558458272606627111270040091203073580238905303994472202930783207472394578498507764703191288249547659899997131166130259700604433891232298182348403175947450284433411265966789131024573629546048637848902243503970966798589660808533


p = 283
q = 47
g = 60

# a=x, b=y, c=z
def pow(x, y, z):
    ans = 1
    while y > 0:
        if y % 2 == 1:
            ans = (ans * x) % z
        x = (x * x) % z
        y = math.floor(y / 2)
    return ans


def customHash(values):
    h = 0
    for i in range(0, len(values)):
        h = (h + math.pow(10, i) * values[i] % q) % q
    return h


def validVoteProof(pk, v, a, b, r):
    if v == 0:
        c1 = randint(0, q - 1)
        r0 = randint(0, q - 1)
        r1 = randint(0, q - 1)

        a1 = pow(g, r1, p) * pow(a, c1 * (p - 2), p) % p
        b1 = pow(pk, r1, p) * pow(b * pow(g, p - 2, p) % p, c1 * (p - 2), p) % p

        a0 = pow(g, r0, p)
        b0 = pow(pk, r0, p)

        c = customHash([pk, a, b, a0, b0, a1, b1])
        c0 = (q + (c1 - c) % q) % q

        r0 = (r0 + (c0 * r) % q) % q
        return [a0, a1, b0, b1, c0, c1, r0, r1]
    if v == 1:
        c0 = randint(0, q - 1)
        r0 = randint(0, q - 1)
        r1 = randint(0, q - 1)

        a0 = pow(g, r0, p) * pow(a, c0 * (p - 2), p) % p
        b0 = pow(pk, r0, p) * pow(b, c0 * (p - 2), p) % p

        a1 = pow(g, r1, p)
        b1 = pow(pk, r1, p)

        c = customHash([pk, a, b, a0, b0, a1, b1])
        c1 = (q + (c0 - c) % q) % q
        r1 = (r1 + (c1 * r) % q) % q
        return [a0, a1, b0, b1, c0, c1, r0, r1]
    return [0, 0, 0, 0, 0, 0, 0, 0]


def generate_keys():
    sk = randint(1, q - 1)#secret key
    pk = pow(g, sk, p) #public key
    print('sk in eg.py=',sk)
    # print('\n')
    # print(pk)
    return pk, sk


def encrypt(pk, v):
    r = randint(1, q - 1)
    a = pow(g, r, p)
    b = pow(g, v, p) * pow(pk, r, p) % p
    proof = validVoteProof(pk, v, a, b, r)
    print('proof=',proof)
    return a, b, r  #, proof


def decrypt(sk, a, b):
    ai = pow(a, sk * (p - 2), p)
    gm = b * ai % p
    m = 0
    while pow(g, m, p) != gm:
        m += 1
    return m


def verifyDecryption(pk, a, b, proof):
    u, v, s, d = proof
    c = customHash([pk, a, b, u, v])
    return ((pow(a, s, p) == u * pow(d, c, p) % p) and (pow(g, s, p) == v * pow(pk, c, p) % p))


def verify_vote(pk, cipher, proof):
    a, b = cipher
    a0, a1, b0, b1, c0, c1, r0, r1 = proof

    s1 = pow(g, r0, p) == a0 * pow(a, c0, p) % p
    s2 = pow(g, r1, p) == a1 * pow(a, c1, p) % p
    s3 = pow(pk, r0, p) == b0 * pow(b, c0, p) % p
    s4 = pow(pk, r1, p) == b1 * pow(b * pow(g, p - 2, p) % p, c1, p) % p
    #
    # s5 = (c0 + c1) % q == custom_hash([pk, a, b, a0, b0, a1, b1])
    return s1 and s2 and s3 and s4


# def correct_decryption_proof(pk, sk, a, b):
#     r = randint(0, q - 1)
#     u = pow(a, r, p)
#     v = pow(g, r, p)
#     c = custom_hash([pk, a, b, u, v])
#     s = (r + (c * sk) % q) % q
#     d = pow(a, sk, p)
#     return u, v, s, d
#

def add(ciphers):
    a = 1
    b = 1
    for (ai, bi) in ciphers:
        a = (a * ai) % p
        b = (b * bi) % p
    return a, b


def is_prime(n):
    """
    Assumes that n is a positive natural number
    """
    # We know 1 is not a prime number
    if n == 1:
        return False

    i = 2
    # This will loop from 2 to int(sqrt(x))
    while i * i <= n:
        # Check if i divides x without leaving a remainder
        if n % i == 0:
            # This means that n has a factor in between 2 and sqrt(n)
            # So it is not a prime number
            return False
        i += 1
    # If we did not find any factor in the above loop,
    # then n is a prime number
    return True



# print(number.getRandomNumber(n_bits, cls.RAND.get_bytes) % max)


# a,b,proof= encrypt(pk,vote)













