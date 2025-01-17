#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) Copyright IBM Corp. 2010, 2020. All Rights Reserved.

import pytest
from resilient_sdk.util import package_file_helpers, sdk_validate_configs
from resilient_sdk.util.sdk_exception import SDKException


def test_name_lambda():

    func = sdk_validate_configs.setup_py_attributes.get("name", {}).get("fail_func", None)
    
    assert func is not None
    assert not func("test_name")
    assert not func("name_with_n0mb3rs")
    assert func("test_name_with invalid characters")

def test_display_name_lambda():

    func = sdk_validate_configs.setup_py_attributes.get("display_name", {}).get("fail_func", None)
    
    assert func is not None
    assert not func("This is My Display Name")
    assert func("<<default display name>>")

def test_license_lambda():

    func = sdk_validate_configs.setup_py_attributes.get("license", {}).get("fail_func", None)
    
    assert func is not None
    assert not func("MIT")
    assert func("<<default license>>")

def test_author_lambda():

    func = sdk_validate_configs.setup_py_attributes.get("author", {}).get("fail_func", None)
    
    assert func is not None
    assert not func("IBM")
    assert func("<<default author>>")

def test_author_email_lambda():

    func = sdk_validate_configs.setup_py_attributes.get("author_email", {}).get("fail_func", None)
    
    assert func is not None
    assert not func("ibm@ibm.com")
    assert not func("<<default email>>")
    assert func("example@example.com")

def test_description_lambda():

    func = sdk_validate_configs.setup_py_attributes.get("description", {}).get("fail_func", None)
    
    assert func is not None
    assert not func("My Custom Function is well described")
    assert func("Resilient Circuits Components for fn_test")
    assert func("Resilient Circuits Components")

def test_long_description_lambda():

    func = sdk_validate_configs.setup_py_attributes.get("long_description", {}).get("fail_func", None)
    
    assert func is not None
    assert not func("My Custom Function is well described. And the description is long.")
    assert func("Resilient Circuits Components for fn_test")
    assert func("Resilient Circuits Components")

def test_install_requires_lambda():

    func = sdk_validate_configs.setup_py_attributes.get("install_requires", {}).get("fail_func", None)
    
    assert func is not None
    assert not func(['resilient_circuits>=30.0.0', 'boto3'])
    assert not func(['resilient-circuits>=30.0.0', 'fn-utilities'])
    assert func(["'only-this-package'"])

def test_python_requires_lambda():

    func = sdk_validate_configs.setup_py_attributes.get("python_requires", {}).get("fail_func", None)
    
    assert func is not None
    assert not func(">=3.6")
    assert func(">=2.0")
    assert func(">=0.0")
    with pytest.raises(SDKException):
        func("<2")
    with pytest.raises(SDKException):
        func("<=2.7")

def test_entry_points_lambda():

    func = sdk_validate_configs.setup_py_attributes.get("entry_points", {}).get("fail_func", None)
    
    assert func is not None
    assert not func(package_file_helpers.SUPPORTED_EP)
    assert func(["only_one_entry_point"])
