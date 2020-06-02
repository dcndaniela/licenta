
import urllib, re, datetime, string

from django.conf import settings

import random, logging




def random_string(length=20, alphabet=None):
    random.seed()
    ALPHABET = alphabet or 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    r_string = ''
    for i in range(length):
        r_string += random.choice(ALPHABET)

    return r_string