"""
Created on 18 avr. 2018

@author: vauge
"""
import os
import xml.etree.ElementTree as etree
import xmlschema
import sys
from openpyxl import Workbook


class MalformedResultsFile(Exception):
    pass


class Test:
    """
    Class that represent a test with it's name, requirement level,
    result, time and steps details
    """

    def __init__(self, requirement_level, result, steps):
        self.requirement_level = requirement_level
        self.result = result
        self.steps = steps


class Step:
    """
    Class that represent a step with it's name and result
    """

    def __init__(self, name, result, message):
        self.name = name
        self.result = result
        self.message = message


def construct_steps(step_nodes):
    """
    Return an array of Step object given an array of "StepResult" nodes
    :param step_nodes: Array of Node object representing StepResult XML nodes
    :return: Array of Step object
    """
    steps = []

    # Run through all StepResult nodes
    for sn in step_nodes:
        name = sn.find('StepName').text
        result = sn.find('Status').text
        message = sn.find('Message').text

        steps.append(Step(name, result, message))

    return steps


def construct_tests(result_nodes):
    """
    Return a dictionary of Test object given an array of "TestResult" nodes
    :param result_nodes: Array of Node object representing TestResult XML nodes
    :return: Dictionary of Test object
    """
    results = {}

    # Run through all TestResult nodes
    for rn in result_nodes:
        name = rn.find('TestInfo').find('Name').text
        requirement_level = rn.find('TestInfo').find('RequirementLevel').text
        result = rn.find('Log').find('TestStatus').text
        step_nodes = rn.find('Log').find('Steps').findall('StepResult')

        results[name] = Test(requirement_level, result, construct_steps(step_nodes))

    return results


def construct_results(file):
    """
    Return a dictionary of Test object given an XML file path
    :param file: result file path
    :return: Dictionary of Test object
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
    :param results_set: Tuple containing the name of result file and the dictionary of tests
    :return: None
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


def compare_steps(name, requirement_level, steps_set1, steps_set2):
    """
    Compare 2 steps array and pretty print steps list
    :param name: Name of the parent test
    :param requirement_level: Requirement level of the parent test
    :param steps_set1: Tuple containing the name of the first result file and the associated array of Step object
    :param steps_set2: Tuple containing the name of the second result file and the associated array of Step object
    :return: None
    """
    name1 = steps_set1[0]
    name2 = steps_set2[0]
    steps1 = steps_set1[1]
    steps2 = steps_set2[1]
    # maximum number of test between steps1 and steps2
    max_step_number = max([len(steps1), len(steps2)])
    # maximum length between steps names and result file name one
    column1 = [s.name for s in steps1]
    column1.append(name1)
    max_name_length = len(max(column1, key=len))

    print('\nTest: {} is {}\n'.format(name, 'mandatory' if requirement_level == 'Must' else 'optional'))

    offset = ''.join(' ' for x in range(max_name_length - len(name1)))
    print('{name1}{offset} {name2}'.format(name1=name1, offset=offset, name2=name2))
    for i in range(max_step_number):
        # Length of current step name before coloring
        step_name_length = len(steps1[i].name if i < len(steps1) else '')

        # error message of failed steps
        error_msg = ''

        if 'NOCOLOR' in os.environ:
            step_name1 = steps1[i].name if i < len(steps1) else ''
            step_name2 = steps2[i].name if i < len(steps2) else ''

            # error message of failed steps
            error_msg += steps1[i].message if i < len(steps1) and steps1[i].result == "Failed" else ''
            error_msg += steps2[i].message if i < len(steps2) and steps2[i].result == "Failed" else ''
        else:
            # coloring of step name 1
            if i < len(steps1):
                if steps1[i].result == "Passed":
                    step_name1 = '\x1b[32;m{}\x1b[0m'.format(steps1[i].name)
                else:
                    error_msg += steps1[i].message
                    step_name1 = '\x1b[31;m{}\x1b[0m'.format(steps1[i].name)
            else:
                step_name1 = ''

            # coloring of step name 2
            if i < len(steps2):
                if steps2[i].result == "Passed":
                    step_name2 = '\x1b[32;m{}\x1b[0m'.format(steps2[i].name)
                else:
                    error_msg += steps2[i].message
                    step_name2 = '\x1b[31;m{}\x1b[0m'.format(steps2[i].name)
            else:
                step_name2 = ''

        offset = ''.join(' ' for x in range(max_name_length - step_name_length))
        print('{step_name1}{offset} {step_name2}'.format(step_name1=step_name1, offset=offset, step_name2=step_name2))

        if error_msg != '':
            if 'NOCOLOR' in os.environ:
                print('{}'.format(error_msg))
            else:
                print('\x1b[31;m{}\x1b[0m'.format(error_msg))


def compare_results(results_set1, results_set2):
    """
    Compare 2 results dictionary and interact with user to inspect steps
    :param results_set1: Tuple containing the name of the first result file and the associated dictionary of Test object
    :param results_set2: Tuple containing the name of the second result file and the associated dictionary of Test
    object
    :return: None
    """
    name1 = results_set1[0]
    name2 = results_set2[0]
    results1 = results_set1[1]
    results2 = results_set2[1]
    diff = {}
    wb = Workbook()
    ws = wb.active
    ws.title = 'Test differences'

    ws['B1'] = name1
    ws['C1'] = name2

    # Look for test result different in file 1 and 2
    i = 0
    for name in results1:
        if name not in results2:
            continue

        if results1[name].result != results2[name].result:
            ws['A' + str(2 + i)] = name
            ws['B' + str(2 + i)] = results1[name].result
            ws['C' + str(2 + i)] = results2[name].result
            # diff[name] = (results1[name].result, results2[name].result, results1[name].requirement_level)

        i += 1

    # Test done in file 2 but not in file 1
    for name in results2:
        if name not in results1:
            print('> Test "{}" is in {} but not in {}'.format(name, name2, name1))

    # Test done in file 1 but not in file 2
    for name in results1:
        if name not in results2:
            print('> Test "{}" is in {} but not in {}'.format(name, name1, name2))

    for inspect in range(len(diff)):
        name = list(diff)[inspect]
        requirement_level = results1[name].requirement_level
        steps1 = results1[name].steps
        steps2 = results2[name].steps

        compare_steps(name, requirement_level, (name1, steps1), (name2, steps2))

    wb.save('output.xlsx')


def usage():
    print('Usage: {} <file 1> [<file 2>]'.format(sys.argv[0]))
    sys.exit(1)


def main():
    """ main """
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        usage()

    # If there are 2 files compare them
    if len(sys.argv) == 3:
        if not os.path.exists(sys.argv[1]):
            sys.stderr.write("{} doesn't exist".format(sys.argv[1]))
            usage()

        if not os.path.exists(sys.argv[2]):
            sys.stderr.write("{} doesn't exist".format(sys.argv[2]))
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
            sys.stderr.write("{} doesn't exist".format(sys.argv[1]))
            usage()

        name = os.path.basename(sys.argv[1])
        results = construct_results(sys.argv[1])
        analyse_results((name, results))


if __name__ == '__main__':
    main()
