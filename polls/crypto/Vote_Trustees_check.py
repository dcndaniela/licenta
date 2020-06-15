from django.contrib import messages
from django.shortcuts import redirect
from polls.crypto import algoritmi


# Helios cripteaza corect votul care este verificat de Trustee1 si Trustee2

#Helios

def test(request):
    messages.error(request, 'TEST!!Something went wrong! Please contact us on voote5@voote5.com!',
                        extra_tags = 'alert alert-danger alert-dismissible fade show')
    return redirect('polls:index')



#Trustee1

def Trustee_validate_vote(p, q, g, sk_vote, pk_vote, sk_trustee,pk_trustee,alpha_vote,beta_vote,randomness_vote,m):
    #verifica daca sk generata de Helios este corecta

    check1= algoritmi.ZKProofIACR_verify_sk(p, q, g, sk_vote, pk_vote, sk_trustee, pk_trustee)

    check2= algoritmi.ChaumPedersonHeliosV4_proof_that_alpha_beta_encodes_m(p, q, g, pk_vote, m, alpha_vote, beta_vote,
                                                                            randomness_vote)

    check3= algoritmi.ChaumPederson_correct_decryption(p, q, g, alpha_vote, beta_vote, pk_vote, sk_vote, pk_trustee, sk_trustee)

    return check1 and check2 and check3



#Trustee2