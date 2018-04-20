'''
Created on 19 avr. 2018

@author: vauge
'''
from src.compare_XML_ONVIF_tests import *

class Test:
    def test_construct_steps_empty(self):
        assert len(construct_steps([])) == 0
    
    def test_construct_steps(self):
        pass
    