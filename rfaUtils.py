'''
Created on Oct 19, 2016

@author: sashaalexander
@author: team 9
'''
from datetime import datetime
import os
import sys
import mysql.connector
import requests


def getLog(testName, logDir):
    """
    Creates logDir directory, if it doesn't exist,
    creates or opens a log file in 'logs' directory.
    """
    # assign a current working directory + '/logs' to log_dir variable (platform independent)
    log_dir = os.path.join(os.getcwd(), logDir)
    # or --> script directory: log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    # or --> user directory: log_dir = os.path.join(os.path.expanduser("~"), "logs")

    try:
        # if logs directory(!) doesn't exist, create it
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
            # open log file with prefix and timestamp (platform independent) in Append mode
        log = open(os.path.join(log_dir, testName + "_" + getCurTime("%Y%m%d_%H-%M-%S") + ".log"), "a")
        return log
    except (OSError, IOError):
        # return -1 in case of exception
        return -1


def qaPrint(log, message):
    """
    Prints 'timestamp + message' to console and writes it to the log file
    """
    # current date and time as string + message. example: [Oct 25 01:52:33.000001] TC1 - Passed
    log_message = getCurTime("[%b %d %H:%M:%S.%f]") + " " + message
    # prints log_message
    print log_message
    # writes message to a log file
    log.write(log_message + "\n")


def getCurTime(date_time_format):
    """
    Returns current date_time as a string formatted according to date_time_format
    """
    date_time = datetime.now().strftime(date_time_format)
    return date_time


def getLocalEnv(propertiesFileName):
    try:
        properties = open(propertiesFileName, "r")
        props = {}
        for line in properties:
            line = line.strip()
            # skip line without "="
            if "=" not in line: continue
            # skip comments
            if line.startswith("#"): continue
            k, v = line.split("=", 1)
            props[k] = v
        if not properties.closed: properties.close()
        return props
    except Exception as e:
        print e
        if not properties.closed: properties.close()
        return -1


def getTestCases(testRunId, log):
    TEST_CASE_KEYS = ('rest_URL', 'HTTP_method', 'HTTP_RC_desired', 'param_list')
    testCases = {}
    try:
        testCasesFile = open(str(testRunId) + '.txt')
        # loop through lines in file
        for line in testCasesFile:
            line = line.strip()
            # skip empty line
            if line == '': continue
            # skip comments
            if line.startswith("#"): continue
            # convert last element to a list
            tc = line.split("|")
            tc[-1] = tc[-1].split(',')
            if tc[0] not in testCases:
                # fill dict with keys from TEST_CASE_KEYS and slice of list , skipping 1st element - tcid
                testCases[tc[0]] = dict(zip(TEST_CASE_KEYS, tc[1:]))
            else:
                qaPrint(log, "[INFO]Duplicated tcid {}, skipping line".format(tc[0]))
        if not testCasesFile.closed: testCasesFile.close()
        return testCases
    except Exception as ex:
        print ex
        return -1


def usage():
    print ('[ERROR]Invalid parameters. Proper usage: rfaRunner.py --testrun=<testRunId>')


def closeLog(log):
    # close the log file if it open
    if not log.closed:
        qaPrint(log, '[INFO]Test suite ends')
        log.close()


def getArguments(args):
    arguments = {}
    if len(args) < 2:
        sys.exit(usage())
    try:
        arguments['testName'] = args[0].split('/')[-1].replace('.py', '')
        for i in range(1, len(args)):
            arg = args[i].split('=')
            if arg[0].lower() == '--testrun':
                arguments['trid'] = int(arg[1])
                if (arguments['trid'] not in range(1, 10001)):
                    usage()
                    sys.exit("[ERROR]Invalid parameter, value should be [0-10000]")
        return arguments
    except Exception:
        sys.exit(usage())


def getDbConnection(url, username, user_password):
    try:
        cnx = mysql.connector.connect(user=username, password=user_password,
                                      host=url,
                                      database='bugs')
    except Exception as e:
        print e
        cnx = -1
    return cnx


def getDbCursor(cnx):
    try:
        cursor = cnx.cursor()
    except Exception as e:
        print e
        cursor = -1
    return cursor


def queryDb():
    pass


def buildURL(list_of_strings):
    url = ""
    if len(list_of_strings) > 0:
        url = list_of_strings[0].strip("/")

    for i in range(1, len(list_of_strings)):
        st = list_of_strings[i]
        if st == "":
            continue
        url = url + "/" + st.strip("/")
    url = url.strip("/")
    return url


def getHttpResponse(url, http_method, parameters):
    response = -1
    try:
        if http_method == 'POST':
            response = requests.post(url, auth=(parameters['username'], parameters['password']))
            return response
        if http_method == 'GET':
            response = requests.get(url, auth=(parameters['username'], parameters['password']))
            return response
        if http_method == 'HEAD':
            response = requests.head(url, auth=(parameters['username'], parameters['password']))
            return response
        if http_method == 'DELETE':
            response = requests.delete(url, auth=(parameters['username'], parameters['password']))
            return response
        if http_method == 'OPTIONS':
            response = requests.options(url, auth=(parameters['username'], parameters['password']))
            return response
    except Exception as e:
        print e
        return response


def getHttpResponseCode(response, indicator):
    if indicator == 'string':
        return str(response.status_code)
    if indicator == 'int':
        return response.status_code


def checkEnv():
    return True

