
from django.utils import timezone

def get_user_type(request):#ce tip de user este conectat acum
    if request.user.is_superuser:
        return "Administrator"
    if request.user.is_staff:
        return "Stuff"
    return "User"

def is_Admin_or_Staff(request):
    return request.user.is_staff or request.user.is_superuser

def is_CNP_valid(cnp):
    if len(cnp)!=13 :
        return False
    suma=1
    nr="279146358279"
    for i in range(0,12):
        suma=suma+ int(cnp[i]) * int(nr[i])
    cif_control=suma%11
    if suma % 11 ==10:
        cif_control=1
    print ('suma=',suma, 'cif_control=',cif_control)
    if cif_control==int(cnp[12]):
        return True
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
    print('este valid:',is_CNP_valid("2990211385570"))


if __name__ == "__main__":
    main()




