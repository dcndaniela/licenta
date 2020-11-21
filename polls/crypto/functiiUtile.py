from django.utils import timezone


def is_Admin_or_Staff(request):
    return request.user.is_staff or request.user.is_superuser

def verif_data_nasterii(cnp):
    if int(cnp[0]) == 0:
        return False
    if (int(cnp[3]) ==1 and int(cnp[4])>=0 and int(cnp[4])<3) or (int(cnp[3])==0 and int(cnp[4])>0):
        print('intra')
        if (int(cnp[5])==0 and int(cnp[6])==0):
            return False
        if (int(cnp[5])==3 and int(cnp[6])>1):
            return False
        if (int(cnp[5]) > 3):
            return False
        return True
    return False

def is_CNP_valid(cnp):
    print(len(cnp))
    if len(cnp)!= 13 :
        return False
    if verif_data_nasterii(cnp):
        print('ok')
        suma = 0
        nr = "279146358279"
        for i in range(0,12):
            suma = suma + int(cnp[i]) * int(nr[i])
        cif_control = suma % 11
        print("c_contr=",cif_control)
        if suma % 11 == 10:
            cif_control = 1
        if cif_control == int(cnp[12]):
            return True
        return False
    return False

def can_edit_Election(request,poll):
    #daca este owner + este Admin sau Staff + election NU a inceput => True
    if (request.user == poll.owner) and  is_Admin_or_Staff(request) and  poll.has_not_started \
        and timezone.now()<poll.start_date: #Nu se poate modifica daca s-a terminat de votat
        return True
    return False

def can_see_DetailView(request,poll):
    if not is_Admin_or_Staff(request) and not poll.isActive:
        return False
    return True


def main():
    # print('este valid:',is_CNP_valid("2990211385570"))
    print('este valid:', is_CNP_valid("2990211385562"))


if __name__ == "__main__":
    main()




