"""
Created on 19 avr. 2018

@author: vauge
"""
from src.compare_XML_ONVIF_tests import *


class Test:
    def test_construct_steps_empty(self):
        assert len(construct_steps([])) == 0

    def test_construct_steps_right_count(self):
        step_nodes = etree.parse('test_files\\steps.xml').findall('StepResult')
        steps = construct_steps(step_nodes)

        assert len(steps) == 4

    def test_construct_steps_right_names(self):
        step_nodes = etree.parse('test_files\\steps.xml').findall('StepResult')
        steps = construct_steps(step_nodes)

        for i in range(len(step_nodes)):
            assert steps[i].name == step_nodes[i].find('StepName').text

    def test_construct_steps_right_results(self):
        step_nodes = etree.parse('test_files\\steps.xml').findall('StepResult')
        steps = construct_steps(step_nodes)

        for i in range(len(step_nodes)):
            assert steps[i].result == step_nodes[i].find('Status').text

    def test_construct_tests_empty(self):
        assert len(construct_tests([])) == 0

    def test_construct_tests_right_count(self):
        result_nodes = etree.parse('test_files\\results.xml').findall('TestResult')
        results = construct_tests(result_nodes)

        assert len(results) == 3

    #     def test_construct_tests_right_time(self):
    #         result_nodes = etree.parse('test_files\\results.xml').findall('TestResult')
    #         results = construct_tests(result_nodes)
    #
    #         for i in range(len(result_nodes)):
    #             assert results[result_nodes[i].find('TestInfo').find('Name').text].time == 0

    def test_construct_tests_right_requirement_level(self):
        result_nodes = etree.parse('test_files\\results.xml').findall('TestResult')
        results = construct_tests(result_nodes)

        for i in range(len(result_nodes)):
            assert results[result_nodes[i].find('TestInfo').find('Name').text].requirement_level == \
                   result_nodes[i].find('TestInfo').find('RequirementLevel').text

    def test_construct_tests_right_result(self):
        result_nodes = etree.parse('test_files\\results.xml').findall('TestResult')
        results = construct_tests(result_nodes)

        for i in range(len(result_nodes)):
            assert results[result_nodes[i].find('TestInfo').find('Name').text].result == \
                   result_nodes[i].find('Log').find('TestStatus').text

    def test_construct_tests_right_step(self):
        pass
