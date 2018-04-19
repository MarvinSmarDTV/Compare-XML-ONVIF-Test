'''
Created on 18 avr. 2018

@author: vauge
'''
import xml.etree.ElementTree as etree

class Test:
    '''
    Class that represent a test with it's name, requirement level,
    result, time and steps details
    '''
    def __init__(self, requierment_level, result, time, steps):
        self.requierment_level = requierment_level
        self.result = result
        self.time = time
        self.steps = steps

class Step:
    '''
    Class that represent a step with it's name and result
    '''
    def __init__(self, name, result):
        self.name = name
        self.result = result

def construct_steps(steps_node):
    '''
    Return an array of Step object given the "Steps" XML node
    '''
    steps = []
    total_steps = len(steps_node)
    
    # Run through all StepResult nodes
    for i in range(total_steps):
        name = steps_node[i][1].text
        result = steps_node[i][-1].text
        
        steps.append(Step(name, result))
    
    return steps

def construct_tests(results_node):
    '''
    Return a dictionary of Test object given the "Results" XML node
    '''
    results = {}
    
    # Run through all TestResult nodes
    for i in range(len(results_node)):
        name = results_node[i][0][1].text
        requierment_level = results_node[i][0][5].text
        result = results_node[i][1][1].text
        steps_node = results_node[i][1][0]
        
        results[name] = Test(requierment_level, result, 0, construct_steps(steps_node))
        
    return results

def construct_results(file):
    '''
    Return a dictionary of Test object given an XML file path
    '''
    # Open and parse XML file
    tree = etree.parse(file)
    
    root_node = tree.getroot()
    results_node = root_node[3]

    return construct_tests(results_node)

def analyse_results(results):
    '''
    Print some stats about a results dictionary
    '''
    # Counters
    total_tests = len(results)
    total_mandatory_tests = 0
    passed_tests = 0
    failed_mandatory_tests = 0
    
    for test in results.values():
        # Update counters
        if test.result == 'Passed':
            passed_tests += 1
         
        if test.requierment_level == 'Must':
            total_mandatory_tests += 1
            if test.result == 'Failed':
                failed_mandatory_tests += 1
    
    print('Percentage of passed tests: ' + str(passed_tests / total_tests * 100) + '%')
    print('Percentage of failed mandatory tests: ' + str(failed_mandatory_tests / total_mandatory_tests * 100) + '%')

def compare_results(results1, results2):
    '''
    Compare 2 results dictionary
    '''
    for name in results1:
        if name not in results2:
            print('> Test "{}" is in results 1 but not in results 2'.format(name))
            continue
        
        if results1[name].result != results2[name].result:
            print('> Test "{}" is "{}" in results 1 but "{}" in results 2'.format(name, results1[name].result, results2[name].result))
            print('  This test is {}'.format('mandatory' if results1.requierment_level == 'Must' else 'optional'))

''' main '''

results1 = construct_results('A:\\ONVIF tests\\tests_dahua.xml')
#results2 = construct_results('A:\\ONVIF tests\\tests_hikvision.xml')

analyse_results(results1)
#analyse_results(results2)

compare_results(results1, results1)
