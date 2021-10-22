#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) Copyright IBM Corp. 2021. All Rights Reserved.

import re
from resilient_sdk.util.sdk_validate_issue import SDKValidateIssue
from resilient_sdk.util import sdk_helpers, constants, sdk_validate_helpers
from resilient_sdk.util import package_file_helpers as package_helpers

# formatted strings follow array of values: [attr, attr_value, <OPTIONAL: fail_msg_lambda_supplement>]
setup_py_attributes = {
    "name": {
        "parse_func": package_helpers.parse_setup_py,
        "fail_func": lambda x: re.findall(r"[^a-z_]+", str(x)),
        "fail_msg": "setup.py attribute '{0}' is has invalid character(s)",
        "missing_msg": "setup.py file is missing attribute/or missing value for attribute '{0}'",
        "solution": "Make sure that '{0}' is all lowercase and does not include and special characters besides underscores",
        "severity": SDKValidateIssue.SEVERITY_LEVEL_CRITICAL
    },
    "display_name": {
        "parse_func": package_helpers.parse_setup_py,
        "fail_func": lambda x: re.findall(r"^<<|>>$", str(x)),
        "fail_msg": "setup.py attribute '{0}' appears to still be the default value '{1}'", 
        "missing_msg": "setup.py file is missing attribute/or missing value for attribute '{0}'",
        "solution": "Please set '{0}' to an appropriate value. This value will be displayed when the integration is installed",
        "severity": SDKValidateIssue.SEVERITY_LEVEL_WARN
    },
    "license": {
        "parse_func": package_helpers.parse_setup_py,
        "fail_func": lambda x: re.findall(r"^<<|>>$", str(x)), # TODO: what are the GPL's?
        "fail_msg": "setup.py attribute '{0}' appears to still be the default value '{1}'", 
        "missing_msg": "setup.py file is missing attribute/or missing value for attribute '{0}'",
        "solution": "Please set '{0}' to an appropriate value. More info TODO: HERE", # TODO: documentation link 
        "severity": SDKValidateIssue.SEVERITY_LEVEL_CRITICAL
    },
    "author": {
        "parse_func": package_helpers.parse_setup_py,
        "fail_func": lambda x: re.findall(r"^<<|>>$", str(x)),
        "fail_msg": "setup.py attribute '{0}' appears to still be the default value '{1}'", 
        "missing_msg": "setup.py file is missing attribute/or missing value for attribute '{0}'",
        "solution": "Please set '{0}' to the name of the author",
        "severity": SDKValidateIssue.SEVERITY_LEVEL_CRITICAL
    },
    "author_email": {
        "parse_func": package_helpers.parse_setup_py,
        "fail_func": lambda x: re.findall(r"@example\.com", str(x)),
        "fail_msg": "setup.py attribute '{0}' appears to still be the default value '{1}'", 
        "missing_msg": "setup.py file is missing attribute/or missing value for attribute '{0}'",
        "solution": "Please set '{0}' to the author's contact email",
        "severity": SDKValidateIssue.SEVERITY_LEVEL_CRITICAL
    },
    "description": {
        "parse_func": package_helpers.parse_setup_py,
        "fail_func": lambda x: re.findall(r"^(Resilient Circuits Components).+", str(x)),
        "fail_msg": "setup.py attribute '{0}' appears to still be the default value '{1:29.29}...'", 
        "missing_msg": "setup.py file is missing attribute/or missing value for attribute '{0}'",
        "solution": "Please make sure that you write your own '{0}'. This will be displayed when the integration is installed",
        "severity": SDKValidateIssue.SEVERITY_LEVEL_WARN
    },
    "long_description": {
        "parse_func": package_helpers.parse_setup_py,
        "fail_func": lambda x: re.findall(r"^(Resilient Circuits Components).+", str(x)),
        "fail_msg": "setup.py attribute '{0}' appears to still be the default value '{1:29.29}...'", 
        "missing_msg": "setup.py file is missing attribute/or missing value for attribute '{0}'",
        "solution": "Please make sure that you write your own '{0}'. This will be displayed when the integration is installed",
        "severity": SDKValidateIssue.SEVERITY_LEVEL_WARN
    },
    "install_requires": {
        "parse_func": package_helpers.parse_setup_py,
        "fail_func": lambda x: False 
            if package_helpers.get_dependency_from_install_requires(x, "resilient_circuits") is not None 
            else False if package_helpers.get_dependency_from_install_requires(x, "resilient-circuits") is not None
            else True,
        "fail_msg": "'resilient_circuits' must be included as a dependency in '{0}'",
        "missing_msg": "'resilient_circuits' must be included as a dependency in '{0}'",
        "solution": "Please include 'resilient_circuits>={0}' as a requirement in '{1}'".format(
            constants.RESILIENT_LIBRARIES_VERSION, "{0}"
        ),
        "severity": SDKValidateIssue.SEVERITY_LEVEL_CRITICAL
    },
    "python_requires": {
        "parse_func": package_helpers.parse_setup_py,
        "fail_func": lambda x: package_helpers.get_required_python_version(x) < sdk_helpers.MIN_SUPPORTED_PY_VERSION,
        "fail_msg": "'{0}' version '{2[0]}.{2[1]}' is not officially supported",
        "fail_msg_lambda_supplement": lambda x: package_helpers.get_required_python_version(x),
        "missing_msg": "'python_requires' is a recommended attribute",
        "solution": "Suggested value is 'python_requires>={0}.{1}'".format(
            sdk_helpers.MIN_SUPPORTED_PY_VERSION[0],
            sdk_helpers.MIN_SUPPORTED_PY_VERSION[1]
        ),
        "severity": SDKValidateIssue.SEVERITY_LEVEL_WARN
    },
    "entry_points": {
        "parse_func": package_helpers.parse_setup_py,
        "fail_func": lambda x: False if not any([ep not in x for ep in package_helpers.SUPPORTED_EP]) else True,
        "fail_msg": "'{0}' is missing {2} which is one of the required entry points", 
        "fail_msg_lambda_supplement": lambda x: [ep for ep in package_helpers.SUPPORTED_EP if ep not in x],
        "missing_msg": "'{0}' is missing",
        "solution": "Please make sure that all of the following values for '{0}' are implemented: " + str(package_helpers.SUPPORTED_EP),
        "severity": SDKValidateIssue.SEVERITY_LEVEL_CRITICAL
    }
}


# NOTE: selftest_attributes needs to be a list as the order of these checks MATTERS
selftest_attributes = [
    { # check 1: verify that resilient-circuits is installed in python env
        "func": sdk_validate_helpers.selftest_validate_resilient_circuits_installed,

        "fail_name": "'{0}' version is too low".format(constants.CIRCUITS_PACKAGE_NAME),
        "fail_msg": "'{0}=={1}' is not supported".format(constants.CIRCUITS_PACKAGE_NAME, "{0}"),
        "fail_solution": "Upgrade '{0}' by running 'pip install '{0}>={1}''".format(constants.CIRCUITS_PACKAGE_NAME, constants.RESILIENT_LIBRARIES_VERSION),

        "missing_name": "'{0}' not found".format(constants.CIRCUITS_PACKAGE_NAME),
        "missing_msg": "'{0}' is not installed in your python environment".format(constants.CIRCUITS_PACKAGE_NAME),
        "missing_solution": "Please install '{0}' by running 'pip install '{0}''".format(constants.CIRCUITS_PACKAGE_NAME),

        "severity": SDKValidateIssue.SEVERITY_LEVEL_CRITICAL,
        
        "pass_name": "'{0}' found in env".format(constants.CIRCUITS_PACKAGE_NAME),
        "pass_msg": "'{0}' was found in the python environment with the minimum version installed".format(constants.CIRCUITS_PACKAGE_NAME)
    },
    { # check 2: check that the given package is acutally installed in the env
        "func": sdk_validate_helpers.selftest_validate_package_installed,

        "fail_name": "'{0}' not found",
        "fail_msg": "'{0}' is not installed in your python environment",
        "solution": "Please install '{0}' by running 'pip install {1}'",
        "severity": SDKValidateIssue.SEVERITY_LEVEL_CRITICAL,
        
        "pass_name": "'{0}' found in env",
        "pass_msg": "'{0}' is correctly installed in your python environment",
    },
    { # check 3: validate that the selftest file exists
        "func": sdk_validate_helpers.selftest_validate_selftestpy_file_exists,

        "fail_name": "selftest.py not found",
        "fail_msg": "selftest.py is a required file",
        "solution": "Please run codegen --reload and implement the templated selftest function",
        "severity": SDKValidateIssue.SEVERITY_LEVEL_CRITICAL,
        
        "pass_name": "selftest.py found",
        "pass_msg": "selftest.py file found at path '{0}'",
    },
    { # check 4: execute selftest and check how it went
        "func": sdk_validate_helpers.selftest_run_selftestpy,

        # if selftest returncode == 1
        "fail_name": "selftest.py failed",
        "fail_msg": "selftest.py failed  for {0}. Details: {1}",
        "fail_solution": "Please check your configuration values and make sure selftest.py is properly implemented",
        "fail_severity": SDKValidateIssue.SEVERITY_LEVEL_CRITICAL,

        # if 'unimplemented' is the return value from selftest
        "missing_name": "selftest.py not implemented",
        "missing_msg": "selftest.py not implemented for {0}",
        "missing_severity": SDKValidateIssue.SEVERITY_LEVEL_CRITICAL,
        "missing_solution": "selftest.py is a recommended check that should be implemented. More info <TODO: LINK>", # TODO: documentation link

        # if a returncode > 1 comes from running selftest.py
        "error_name": "selftest.py failed",
        "error_msg": "While running selftest.py, 'resilient-circuits' failed to connect to server. Details: {0}",
        "error_severity": SDKValidateIssue.SEVERITY_LEVEL_CRITICAL,

        # if selftest.py succeeds (i.e. returncode == 0)
        "pass_name": "selftest.py success",
        "pass_msg": "selftest.py successfully ran for '{0}'",
    }
]
