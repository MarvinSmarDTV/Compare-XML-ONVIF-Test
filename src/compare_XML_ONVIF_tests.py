"""
Created on 18 avr. 2018

@author: vauge
"""
import os
import xml.etree.ElementTree as etree
import xmlschema
import sys


class MalformedResultsFile(Exception):
    pass


class Test:
    """
    Class that represent a test with it's name, requirement level,
    result, time and steps details
    """

    def __init__(self, requirement_level, result, time, steps):
        self.requirement_level = requirement_level
        self.result = result
        self.time = time
        self.steps = steps


class Step:
    """
    Class that represent a step with it's name and result
    """

    def __init__(self, name, result):
        self.name = name
        self.result = result


def construct_steps(step_nodes):
    """
    Return an array of Step object given an array of "StepResult" nodes
    """
    steps = []

    # Run through all StepResult nodes
    for sn in step_nodes:
        name = sn.find('StepName').text
        result = sn.find('Status').text

        steps.append(Step(name, result))

    return steps


def construct_tests(result_nodes):
    """
    Return a dictionary of Test object given an array of "TestResult" nodes
    """
    results = {}

    # Run through all TestResult nodes
    for rn in result_nodes:
        name = rn.find('TestInfo').find('Name').text
        requirement_level = rn.find('TestInfo').find('RequirementLevel').text
        result = rn.find('Log').find('TestStatus').text
        step_nodes = rn.find('Log').find('Steps').findall('StepResult')

        results[name] = Test(requirement_level, result, 0, construct_steps(step_nodes))

    return results


def construct_results(file):
    """
    Return a dictionary of Test object given an XML file path
    """
    # Validate XML file with XML Schema
    my_schema = xmlschema.XMLSchema('ONVIF_Device_Test_Tool.xsd')
    if not my_schema.is_valid(file):
        raise MalformedResultsFile('')

    # Open and parse XML file
    tree = etree.parse(file)

    root_node = tree.getroot()
    result_nodes = root_node.find('Results').findall('TestResult')

    return construct_tests(result_nodes)


def analyse_results(results_set):
    """
    Print some stats about a results dictionary
    """
    name = results_set[0]
    results = results_set[1]

    # Counters
    total_tests = len(results)
    total_mandatory_tests = 0
    passed_tests = 0
    failed_mandatory_tests = 0

    for test in results.values():
        # Update counters
        if test.result == 'Passed':
            passed_tests += 1

        if test.requirement_level == 'Must':
            total_mandatory_tests += 1
            if test.result == 'Failed':
                failed_mandatory_tests += 1

    print('==={}==='.format(name))
    print('Percentage of passed tests: ' + str(passed_tests / total_tests * 100) + '%')
    print('Percentage of failed mandatory tests: ' + str(failed_mandatory_tests / total_mandatory_tests * 100) + '%\n')


def compare_steps(steps1, steps2):
    """
    Compare 2 steps array
    """
    if len(steps1) != len(steps2):
        return
    for i in range(len(steps1)):
        if steps1[i].result != steps2[i].result:
            print(
                '>> Step {} "{}" is "{}" in results 1 but "{}" in results 2'.format(i, steps1[i].name, steps1[i].result,
                                                                                    steps2[i].result))


def print_diff(diff, name1, name2):
    """
    Pretty print an array of differences between tests
    :param diff: Dictionary of tuples containing differences
    :param name1: Name of file 1
    :param name2: Name of file 2
    :return: None
    """
    max_name_length = len(max(diff.keys(), key=len))
    
    # array header
    print('{} {} {}'.format(''.join([' ' for x in range(max_name_length)]), name1, name2))
    
    for name in diff.keys():
        offset = ''.join([' ' for x in range(max_name_length - len(name))])
        offset2 = ''.join([' ' for x in range(len(name1) - len(diff[name][0]))])
        
        print('{name}{offset} {result1}{offset2} {result2}'.format(name=name, offset=offset, result1=diff[name][0], offset2=offset2, result2=diff[name][1]))


def compare_results(results_set1, results_set2):
    """
    Compare 2 results dictionary
    """
    name1 = results_set1[0]
    name2 = results_set2[0]
    results1 = results_set1[1]
    results2 = results_set2[1]
    diff = {}

    # Look for test result different in file 1 and 2
    for name in results1:
        if name not in results2:
            continue

        if results1[name].result != results2[name].result:
            diff[name] = (results1[name].result, results2[name].result, results1[name].requirement_level)
            # compare_steps(results1[name].steps, results2[name].steps)

    print_diff(diff, name1, name2)

    # Test done in file 2 but not in file 1
    for name in results2:
        if name not in results1:
            print('> Test "{}" is in {} but not in {}'.format(name, name2, name1))

    # Test done in file 1 but not in file 2
    for name in results1:
        if name not in results2:
            print('> Test "{}" is in {} but not in {}'.format(name, name1, name2))


def usage():
    print('Usage: {} <file 1> [<file 2>]'.format(sys.argv[0]))
    sys.exit(1)


def main():
    """ main """
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()

    # If there are 2 files compare them
    if len(sys.argv) == 3:
        if not os.path.exists(sys.argv[1]) or not os.path.exists(sys.argv[2]):
            usage()

        name1 = os.path.basename(sys.argv[1])
        name2 = os.path.basename(sys.argv[2])

        results1 = construct_results(sys.argv[1])
        results2 = construct_results(sys.argv[2])

        analyse_results((name1, results1))
        analyse_results((name2, results2))

        compare_results((name1, results1), (name2, results2))
    else:
        # Else print some stats about the only file
        if not os.path.exists(sys.argv[1]):
            usage()

        name = os.path.basename(sys.argv[1])
        results = construct_results(sys.argv[1])
        analyse_results((name, results))


if __name__ == '__main__':
    main()
