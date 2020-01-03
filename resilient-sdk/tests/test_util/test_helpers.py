#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) Copyright IBM Corp. 2010, 2019. All Rights Reserved.

import os
import stat
import re
import pytest
import jinja2
import sys
from resilient import SimpleClient
from resilient_sdk.util.sdk_exception import SDKException
from resilient_sdk.util import helpers
from tests.shared_mock_data import mock_data, mock_paths


def test_get_resilient_client(fx_mk_temp_dir, fx_mk_app_config):
    res_client = helpers.get_resilient_client(path_config_file=fx_mk_app_config)
    assert isinstance(res_client, SimpleClient)


def test_setup_jinja_env():
    jinja_env = helpers.setup_jinja_env(mock_paths.TEST_TEMP_DIR)
    assert isinstance(jinja_env, jinja2.Environment)
    assert jinja_env.loader.package_path == mock_paths.TEST_TEMP_DIR


def test_read_write_file(fx_mk_temp_dir):
    temp_file = os.path.join(mock_paths.TEST_TEMP_DIR, "mock_file.txt")
    helpers.write_file(temp_file, mock_data.mock_file_contents)
    assert os.path.isfile(temp_file)

    file_lines = helpers.read_file(temp_file)
    assert mock_data.mock_file_contents in file_lines


def test_rename_file(fx_mk_temp_dir):
    temp_file = os.path.join(mock_paths.TEST_TEMP_DIR, "mock_file.txt")
    helpers.write_file(temp_file, mock_data.mock_file_contents)

    helpers.rename_file(temp_file, "new_file_name.txt")
    path_renamed_file = os.path.join(mock_paths.TEST_TEMP_DIR, "new_file_name.txt")

    assert os.path.isfile(path_renamed_file) is True


def test_is_valid_package_name():
    assert helpers.is_valid_package_name("fn_mock_integration") is True
    assert helpers.is_valid_package_name("fnmockintegration") is True
    assert helpers.is_valid_package_name("get") is False
    assert helpers.is_valid_package_name("$%&(#)@*$") is False
    assert helpers.is_valid_package_name("fn-mock-integration") is False
    assert helpers.is_valid_package_name("fn-ځ ڂ ڃ ڄ څ-integration") is False


def test_has_permissions(fx_mk_temp_dir):
    temp_permissions_file = os.path.join(mock_paths.TEST_TEMP_DIR, "mock_permissions.txt")
    helpers.write_file(temp_permissions_file, mock_data.mock_file_contents)

    # Set permissions to Read only
    os.chmod(temp_permissions_file, stat.S_IRUSR)

    with pytest.raises(SDKException, match=r"User does not have WRITE permissions"):
        helpers.has_permissions(os.W_OK, temp_permissions_file)

    # Set permissions to Write only
    os.chmod(temp_permissions_file, stat.S_IWUSR)

    with pytest.raises(SDKException, match=r"User does not have READ permissions"):
        helpers.has_permissions(os.R_OK, temp_permissions_file)


def test_validate_file_paths(fx_mk_temp_dir):
    non_exist_file = "/non_exits/path/non_exist_file.txt"
    with pytest.raises(SDKException, match=r"Could not find file: " + non_exist_file):
        helpers.validate_file_paths(None, non_exist_file)

    exists_file = os.path.join(mock_paths.TEST_TEMP_DIR, "mock_existing_file.txt")
    helpers.write_file(exists_file, mock_data.mock_file_contents)

    helpers.validate_file_paths(None, exists_file)


def test_validate_dir_paths(fx_mk_temp_dir):
    non_exist_dir = "/non_exits/path/"
    with pytest.raises(SDKException, match=r"Could not find directory: " + non_exist_dir):
        helpers.validate_dir_paths(None, non_exist_dir)

    exists_dir = mock_paths.TEST_TEMP_DIR

    helpers.validate_dir_paths(None, exists_dir)


def test_get_obj_from_list(fx_mock_res_client):
    org_export = helpers.get_latest_org_export(fx_mock_res_client)
    export_data = helpers.get_from_export(org_export,
                                          functions=["mock_function_one", "mock_function_two"])

    all_functions = export_data.get("functions")
    got_functions = helpers.get_obj_from_list("export_key", all_functions)

    assert isinstance(got_functions, dict)
    assert "mock_function_one" in got_functions
    assert "mock_function_two" in got_functions

    # Test lambda condition
    got_functions = helpers.get_obj_from_list("export_key", all_functions, lambda o: True if o.get("export_key") == "mock_function_one" else False)
    assert "mock_function_one" in got_functions
    assert "mock_function_two" not in got_functions


def test_get_object_api_names(fx_mock_res_client):
    org_export = helpers.get_latest_org_export(fx_mock_res_client)
    export_data = helpers.get_from_export(org_export,
                                          functions=["mock_function_one", "mock_function_two"])

    func_api_names = helpers.get_object_api_names("x_api_name", export_data.get("functions"))

    assert all(elem in ["mock_function_one", "mock_function_two"] for elem in func_api_names) is True


def test_get_res_obj(fx_mock_res_client):
    org_export = helpers.get_latest_org_export(fx_mock_res_client)

    artifacts_wanted = ["mock_artifact_2", "mock_artifact_type_one"]
    artifacts = helpers.get_res_obj("incident_artifact_types", "programmatic_name", "Custom Artifact", artifacts_wanted, org_export)

    assert all(elem.get("x_api_name") in artifacts_wanted for elem in artifacts) is True


def test_get_res_obj_exception(fx_mock_res_client):
    org_export = helpers.get_latest_org_export(fx_mock_res_client)

    functions_wanted = ["mock_function_one", "fn_does_not_exist"]

    with pytest.raises(SDKException, match=r"Mock Display Name: 'fn_does_not_exist' not found in this export"):
        helpers.get_res_obj("functions", "export_key", "Mock Display Name", functions_wanted, org_export)


def test_get_message_destination_from_export(fx_mock_res_client):
    # TODO: Add test for all resilient objects...
    org_export = helpers.get_latest_org_export(fx_mock_res_client)

    export_data = helpers.get_from_export(org_export,
                                          message_destinations=["fn_main_mock_integration"])

    assert export_data.get("message_destinations")[0].get("name") == "fn_main_mock_integration"

    assert all(elem.get("name") in ("mock_function_one", "mock_function_two") for elem in export_data.get("functions")) is True


def test_minify_export(fx_mock_res_client):
    org_export = helpers.get_latest_org_export(fx_mock_res_client)

    minifed_export = helpers.minify_export(org_export, functions=["mock_function_one"])
    minified_functions = minifed_export.get("functions")
    minified_fields = minifed_export.get("fields")
    minified_incident_types = minifed_export.get("incident_types")

    # Test it minified given function
    assert len(minified_functions) == 1
    assert minified_functions[0].get("export_key") == "mock_function_one"

    # Test it set a non-mentioned object to 'empty'
    assert minifed_export.get("phases") == []

    # Test it added the internal field
    assert len(minified_fields) == 1
    assert minified_fields[0].get("export_key") == "incident/internal_customizations_field"
    assert minified_fields[0].get("uuid") == "bfeec2d4-3770-11e8-ad39-4a0004044aa1"

    # Test it added the default incident type
    assert len(minified_incident_types) == 1
    assert minified_incident_types[0].get("export_key") == "Customization Packages (internal)"
    assert minified_incident_types[0].get("uuid") == "bfeec2d4-3770-11e8-ad39-4a0004044aa0"


def test_minify_export_default_keys_to_keep(fx_mock_res_client):
    org_export = helpers.get_latest_org_export(fx_mock_res_client)

    minifed_export = helpers.minify_export(org_export)

    assert "export_date" in minifed_export
    assert "export_format_version" in minifed_export
    assert "id" in minifed_export
    assert "server_version" in minifed_export


def test_load_by_module():
    path_python_file = os.path.join(mock_paths.SHARED_MOCK_DATA_DIR, "mock_data.py")
    module_name = "mock_data"
    mock_data_module = helpers.load_py_module(path_python_file, module_name)

    assert mock_data_module.mock_loading_this_module == "yes you did!"


def test_rename_to_bak_file(fx_mk_temp_dir):
    temp_file = os.path.join(mock_paths.TEST_TEMP_DIR, "mock_file.txt")
    helpers.write_file(temp_file, mock_data.mock_file_contents)

    helpers.rename_to_bak_file(temp_file)

    files_in_dir = os.listdir(mock_paths.TEST_TEMP_DIR)
    regex = re.compile(r'^mock_file\.txt-\d+-\d+-\d+\d+-\d+:\d+:\d+\.bak$')
    matched_file_name = list(filter(regex.match, files_in_dir))[0]

    assert regex.match(matched_file_name)


def test_rename_to_bak_file_if_file_not_exist(fx_mk_temp_dir):
    temp_file = os.path.join(mock_paths.TEST_TEMP_DIR, "mock_file.txt")
    path_to_backup = helpers.rename_to_bak_file(temp_file)
    assert temp_file == path_to_backup


def test_generate_anchor():
    anchor = helpers.generate_anchor("D מ ן נ ס עata Ta$%^ble Utils: Delete_Row")
    assert anchor == "d-----ata-table-utils-delete-row"


def test_get_workflow_functions():
    # TODO: taken from docgen
    pass


def test_get_main_cmd(monkeypatch):
    mock_args = ["resilient-sdk", "codegen", "-p", "fn_mock_package"]
    monkeypatch.setattr(sys, "argv", mock_args)
    main_cmd = helpers.get_main_cmd()
    assert main_cmd == "codegen"


def test_get_timestamp():
    now = helpers.get_timestamp()
    assert re.match(r"\d\d\d\d-\d\d-\d\d-\d\d:\d\d:\d\d", now)
