from random import randint
import math

# p = 16328632084933010002384055033805457329601614771185955389739167309086214800406465799038583634953752941675645562182498120750264980492381375579367675648771293800310370964745767014243638518442553823973482995267304044326777047662957480269391322789378384619428596446446984694306187644767462460965622580087564339212631775817895958409016676398975671266179637898557687317076177218843233150695157881061257053019133078545928983562221396313169622475509818442661047018436264806901023966236718367204710755935899013750306107738002364137917426595737403871114187750804346564731250609196846638183903982387884578266136503697493474682071
# q = 61329566248342901292543872769978950870633559608669337131139375508370458778917
# g = 14887492224963187634282421537186040801304008017743492304481737382571933937568724473847106029915040150784031882206090286938661464458896494215273989547889201144857352611058572236578734319505128042602372864570426550855201448111746579871811249114781674309062693442442368697449970648232621880001709535143047913661432883287150003429802392229361583608686643243349727791976247247948618930423866180410558458272606627111270040091203073580238905303994472202930783207472394578498507764703191288249547659899997131166130259700604433891232298182348403175947450284433411265966789131024573629546048637848902243503970966798589660808533

import hashlib
from decimal import Decimal

#p = 283
q = 47
p=283
g = 60


def ElGamalWikipedia():
    x = randint(1, q - 1)  # secret key
    h = pow(g, x, q)  # public key=h
    # criptare:
    m = 17
    y = randint(1, q - 1)
    s = pow(h, y, q)  # shared secret
    c1 = pow(g, y, q)  # aka alpha
    c2 = m * s % q  # aka beta
    # decriptare:
    s = pow(c1, x, q)
    s_inverse = pow(c1, q - x, q)
    m = c2 * s_inverse % q
    print(m)
    # return m

    # def decrypt2(a, b,sk):
    #     ai = pow(a, sk * (q - 2), q)
    #     gm = b * ai % q
    #     m = 0
    #     while pow(g, m,q) != gm:
    #         m += 1
    #     return m

q=1009
g=3
a=10
b=13
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

#def ElGamal

def ZKproofTrustee(alpha,beta,voter_id):
    g0 = 5  # nr random din grup
    x = 6  # fie x= Hash(password='abc') =6
    x=int(hashlib.sha1('abc'.encode()).hexdigest(), 16) % (10 ** 1)
    # x este secret key
    Y = pow(g0, x)  # Y=15625(aka este public key)
    r = 400  # generat random
    a = 3  # generat radom
    T1 = pow(g0, r)
    c_entire = hashlib.sha1((str(alpha)+str(beta)+str(voter_id)+str(Y) + str(T1) + str(a)).encode()).hexdigest()
    c = int(hashlib.sha1((str(alpha)+str(beta)+str(voter_id)+str(Y) + str(T1) + str(a)).encode()).hexdigest(), 16) % (10 ** 2)
    print('c=',c)
    z = r - int(c) * x
    T2 = int(pow(Y, c) * pow(g0, z))
    c2_entire = hashlib.sha1((str(alpha)+str(beta)+str(voter_id)+str(Y) + str(T2) + str(a)).encode()).hexdigest()
    c2=int(hashlib.sha1((str(alpha)+str(beta)+str(voter_id)+str(Y) + str(T2) + str(a)).encode()).hexdigest(), 16) % (10 ** 2)
    print('t1=', T1)
    print('verific c1 si c2:',c == c2)
    print('verific c1_entire si c2_entire :',c_entire==c2_entire)
    return (c==c2 and c_entire ==c2_entire)


def verify_alpha_and_beta(alpha,beta,r,y,m):
    print('verif alpha + beta \n')
    print(pow(g,r,p)==alpha,'\n')
    #print(pow(y,r,p)*m % p == beta)
    return((pow(g,r,p)==alpha) and ((pow(y,r,p)*m % p) == beta))

def main():
    # x,h=generate_keys()
    # m=7
    # c1,c2=encrypt(h,m)
    # mesaj=decrypt(c1,c2,x)
    # print(mesaj)


    #ZKproofTrustee(1,2,3)
    ElGamalWikipedia()


if __name__ == "__main__":
    main()

