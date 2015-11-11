#from django.test import TestCase
from build_util import *

def package():
    apks_build('false', 'false', 'develop', 'public_test', '792387725@qq.com')

if __name__=="__main__":
    package()
# Create your tests here.
