from random import randint
import math
import hashlib
import sympy as sympy


# def ElGamalWikipedia():
#     q=283
#     x = randint(1, q - 1)  # secret key
#     h = pow(g, x, q)  # public key=h
#     # criptare:
#     m = 17
#     y = randint(1, q - 1)#randomness
#     s = pow(h, y, q)  # shared secret
#     c1 = pow(g, y, q)  # aka alpha
#     c2 = m * s % q  # aka beta
#
#     # decriptare:
#     s = pow(c1, x, q)
#     s_inverse = pow(c1, q - x, q)
#     s2 = sympy.mod_inverse(s, q)
#     print('c1=', c1, '\n', 'c2=', c2, '\n', s_inverse,'\n')
#     # m = c2 * s_inverse % q
#     m = c2 * s2 % q
#     print(m)
#     # return m
#
#     # def decrypt2(a, b,sk):
#     #     ai = pow(a, sk * (q - 2), q)
#     #     gm = b * ai % q
#     #     m = 0
#     #     while pow(g, m,q) != gm:
#     #         m += 1
#     #     return m
#


# def ZKProofIACR():
# #verific ca sk s-a generat corect pt pk
#     p=283
#     q=141
#     g=60
#     sk = randint(1, q - 1)  # secret key
#     pk = pow(g, sk, p)  # public key=h
#     # criptare:
#     m = 17
#     y = randint(1, q - 1)#randomness
#     s = pow(pk, y, q)  # shared secret
#     c1 = pow(g, y, p)  # aka alpha
#     #c2 = m * s % p  # aka beta
#
#     sk1 = randint(1, q - 1)  # secret key
#     pk1 = pow(g, sk1, p)  # public key=h
#     c=randint(1,q-1)
#     pk2=pk1*pow(pk,c,p) %p
#     sk2= (sk1+c*sk) %q
#     print('pow(g,sk2,p)=',pow(g,sk2,p))
#     print('pk2=',pk2)
#    # print(pow(g,sk2,p)==pk2)
#
# #verific daca c1 si c2 au fost generate corect:
#     #print(pow(g,sk2,p)==(pk1*pow(pk,c1,p))%p)
#
# def ZKProofHeliosV4(p,q,g):
# #din Helios v4
#     # p = 283
#     # q = 141
#     # g = 60
#     sk = randint(1, q - 1)  # secret key
#     pk = pow(g, sk, p)  # public key=h
#     # criptare:
#     m = 17
#     y = randint(1, q - 1)#randomness
#     c1 = pow(g, y, p)  # aka alpha
#     c2=(pow(g,m,p)*pow(pk,y,p)) %p
#
#     w= randint(1,q-1)
#     A=pow(g,w,p)
#     B=pow(pk,w,p)
#     challange=randint(1,q-1)
#     response=w+challange*y
#     print('verif alpha=',(A*pow(c1,challange,p))%p==pow(g,response,p) )
#     invers_g_m=sympy.mod_inverse(pow(g,m,p), p)
#     beta_over_m=(sympy.mod_inverse(pow(g,m,p), p)*c2) %p
#     print('st1=',pow(pk,response,p),'\n','dr1=',(B* pow(beta_over_m,challange,p))%p)
#     print('st2=',pow(pk,response,p),'\n','dr2=',(B*pow(int(c2*invers_g_m),challange,p))%p)
#
#     print('verif beta over m=',pow(pk,response,p)==(B* pow(beta_over_m,challange,p))%p)
#     print('verif beta=', (B*pow(int(c2*invers_g_m),challange,p))%p==pow(pk,response,p))
#
#
#ChaumPederson ZKProof
#
# def generate_keys():
#     r = randint(1, q - 9)#secret key
#     h = pow(g, x, q) #public key=h
#     # print(sk)
#     # print('\n')
#     # print(pk)
#     return x, h
#
# def encrypt(h, m):
#     y = randint(1, q - 1)
#     s=pow(h,y,q)#shared secret
#     c1=pow(g,y,q)
#     c2= m*s % q
#     return c1,c2
#
# def ZKproofTrustee(alpha,beta,voter_id):
#     g0 = 5  # nr random din grup
#     x = 6  # fie x= Hash(password='abc') =6
#     x=int(hashlib.sha1('abc'.encode()).hexdigest(), 16) % (10 ** 1)
#     # x este secret key
#     Y = pow(g0, x)  # Y=15625(aka este public key)
#     r = 400  # generat random
#     a = 3  # generat radom
#     T1 = pow(g0, r)
#     c_entire = hashlib.sha1((str(alpha)+str(beta)+str(voter_id)+str(Y) + str(T1) + str(a)).encode()).hexdigest()
#     c = int(hashlib.sha1((str(alpha)+str(beta)+str(voter_id)+str(Y) + str(T1) + str(a)).encode()).hexdigest(), 16) % (10 ** 2)
#     print('c=',c)
#     z = r - int(c) * x
#     T2 = int(pow(Y, c) * pow(g0, z))
#     c2_entire = hashlib.sha1((str(alpha)+str(beta)+str(voter_id)+str(Y) + str(T2) + str(a)).encode()).hexdigest()
#     c2=int(hashlib.sha1((str(alpha)+str(beta)+str(voter_id)+str(Y) + str(T2) + str(a)).encode()).hexdigest(), 16) % (10 ** 2)
#     print('t1=', T1)
#     print('verific c1 si c2:',c == c2)
#     print('verific c1_entire si c2_entire :',c_entire==c2_entire)
#     return (c==c2 and c_entire ==c2_entire)
#
#
# def verify_alpha_and_beta(alpha,beta,r,y,m):
#     print('verif alpha + beta \n')
#     print(pow(g,r,p)==alpha,'\n')
#     #print(pow(y,r,p)*m % p == beta)
#     return((pow(g,r,p)==alpha) and ((pow(y,r,p)*m % p) == beta))


def generateEG_p_q_g():
    possibleP=[10007,10009,10037]
    i=randint(0,len(possibleP)-1)
    p=possibleP[i]
    q=int((p-1)/2)
    for g in range(101,p): #pornesc de la 101 pt ca vreau ca g sa fie nu foarte mic
        if pow(g,q,p)==1:
            #print('g=', g)
            break
    print('g=',g)
    return p,q,g


def generateEG_pk_sk(p,q,g):
    sk = randint(1, q - 1)  # secret key
    pk = pow(g, sk, p)  # public key=h
    return pk,sk


def generateEG_alpha_beta_randomness(p,q,g,sk,pk,m): #m este mesajul in clar (plaintext)
    randomness = randint(1, q - 1)  # randomness
    alpha = pow(g, randomness, p)
    beta = (pow(g, m, p) * pow(pk, randomness, p)) % p
    return  alpha,beta,randomness


def ZKProofIACR_verify_sk(p,q,g,sk,pk):
#verific ca sk s-a generat corect pentru pk
    sk1 = randint(1, q - 1)  # secret key
    pk1 = pow(g, sk1, p)  # public key=h
    challange=randint(1,q-1)
    pk2=pk1*pow(pk,challange,p) %p
    sk2= (sk1+challange*sk) %q
    #print('pow(g,sk2,p)=',pow(g,sk2,p))
    #print('pk2=',pk2)
    return(pow(g,sk2,p)==pk2)


def ZKProofHeliosV4_verify_alpha_beta(p,q,g,pk,m,alpha,beta,randomness):
    w = randint(1, q - 1)
    A = pow(g, w, p)
    B = pow(pk, w, p)
    challange = randint(1, q - 1)
    response = w + challange * randomness
    verify_alpha=(A * pow(alpha, challange, p)) % p == pow(g, response, p)
    beta_over_m = (sympy.mod_inverse(pow(g, m, p), p) * beta) % p
    verify_beta= pow(pk, response, p) == ((B * pow(beta_over_m, challange, p)) % p)
    #print('verif alpha=', (A * pow(alpha, challange, p)) % p == pow(g, response, p))
    #print('st1=', pow(pk, response, p), '\n', 'dr1=', (B * pow(beta_over_m, challange, p)) % p)
    #print('verif beta over m=', pow(pk, response, p) == (B * pow(beta_over_m, challange, p)) % p)
    return ( verify_alpha and verify_beta)


def ChaumPederson_correct_decryption(p,q,g,alpha,beta,pk,sk):

    r=randint(1,q-1)
    u= pow(alpha,r,p)
    v=pow(g,r,p)
    challange =int(hashlib.sha256((str(pk)+str(alpha)+str(beta)+str(u)+str(v)).encode()).hexdigest(),16)
    print('challange=',challange)
    s= (r+challange*sk) %q
    decryption_factor=pow(alpha,sk,p)
    verif1=pow(alpha,sk,p)==u*pow(decryption_factor,challange,p) %p
    verif2= pow(g,sk,p)== v* pow(pk,challange,p)
    print(verif1==verif2)








def main():
    p,q,g=generateEG_p_q_g()
    pk,sk=generateEG_pk_sk(p,q,g)
    m=5
    if(ZKProofIACR_verify_sk(p,q,g,sk,pk)):
        alpha, beta, randomness = generateEG_alpha_beta_randomness(p, q, g, sk, pk, m)
        if ZKProofHeliosV4_verify_alpha_beta(p,q,g,pk,m,alpha,beta,randomness) :
            print('corect')
            ChaumPederson_correct_decryption(p, q, g, alpha, beta, pk, sk)
        else:
            print('incorect')
    else:
        print('incorect')



if __name__ == "__main__":
    main()

