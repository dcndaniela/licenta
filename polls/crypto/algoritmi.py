from random import randint
import hashlib
import sympy as sympy

def getRandom_p():
    v = [1000003, 1000033, 1000037, 1002241]
    i= randint(0, len(v)-1)
    return v[i]

def getRandomGenerator_g(p,q):
    start=randint(int(p/4), int(p/2))
    g=-1
    for g in range(start,p-1):
        if pow(g,q,p)== 1:
            break
    return g

def generateEG_p_q_g():
    p=getRandom_p()
    q=int((p-1)/2)
    g=getRandomGenerator_g(p,q)
    # print('p=',p,'q=',q,'g=',g)
    return p, q, g

def generateEG_pk_sk(p,q,g):
    sk = randint(1, q - 1)
    pk = pow(g, sk, p)
    return pk, sk

def generateEG_alpha_beta_randomness(p,q,g,sk,pk,m): #m este mesajul in clar (plaintext)
    randomness = randint(1, q - 1)  # randomness
    alpha = pow(g, randomness, p)
    beta = (pow(g, m, p) * pow(pk, randomness, p)) % p
    return  alpha, beta, randomness

#verific ca sk s-a generat corect pentru pk   # pag 31/45 din IACR
def ZKProofIACR_verify_sk(p,q,g,sk,pk,sk_trustee,pk_trustee):
    sk1 = sk_trustee
    pk1 = pk_trustee
    challenge = randint(1,q-1)
    pk2 = pk1*pow(pk,challenge,p) %p
    sk2 = (sk1+challenge*sk) %q
    return(pow(g,sk2,p) == pk2)

# din Helios V4
def ChaumPederson_proof_that_alpha_beta_encodes_m(p, q, g, pk, m, alpha, beta, randomness):
    w = randint(1, q - 1)
    A = pow(g, w, p)
    B = pow(pk, w, p)
    challenge = randint(1, q - 1)
    response = w + challenge * randomness
    verify_alpha=(A * pow(alpha, challenge, p)) % p == pow(g, response, p)
    beta_over_m = (sympy.mod_inverse(pow(g, m, p), p) * beta) % p
    verify_beta= pow(pk, response, p) == ((B * pow(beta_over_m, challenge, p)) % p)
    return verify_alpha and verify_beta

def ChaumPederson_correct_decryption(p, q, g, alpha, beta, pk, sk, pk_trustee, sk_trustee):
    r = sk_trustee
    v = pk_trustee
    u = pow(alpha, r, p)
    challenge = int(hashlib.sha256((str(pk) + str(alpha) + str(beta) + str(u) + str(v)).encode())
                    .hexdigest(), 16)
    s = (r + challenge * sk) % q
    decryption_factor = pow(alpha, sk, p)
    verif1 = pow(alpha, sk, p) == u * pow(decryption_factor, challenge, p) % p
    verif2 = pow(g, sk, p) == v * pow(pk, challenge, p)
    return verif1 == verif2



def main():
    generateEG_p_q_g()


if __name__ == "__main__":
    main()

