'''
Created on 19 avr. 2018

@author: vauge
'''
from src.compare_XML_ONVIF_tests import *

class Test:
    def test_construct_steps_empty(self):
        assert len(construct_steps([])) == 0
    
    def test_construct_steps_same_number(self):
        step_nodes = etree.parse('test_files\\steps.xml').findall('StepResult')
        steps = construct_steps(step_nodes)
        
        assert len(steps) == 4
    
    def test_construct_steps_right_names(self):
        step_nodes = etree.parse('test_files\\steps.xml').findall('StepResult')
        steps = construct_steps(step_nodes)
        
        for i in range(len(steps)):
            assert steps[i].name == step_nodes[i].find('StepName').text
    
    def test_construct_steps_right_results(self):
        step_nodes = etree.parse('test_files\\steps.xml').findall('StepResult')
        steps = construct_steps(step_nodes)
        
        for i in range(len(steps)):
            assert steps[i].result == step_nodes[i].find('Status').text
    
    