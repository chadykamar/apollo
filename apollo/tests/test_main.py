import subprocess

import os

import pytest


@pytest.fixture(scope="function")
def change_test_dir(request):
    os.chdir(request.fspath.dirname)
    yield
    os.chdir(request.config.invocation_dir)


def test_repl(change_test_dir):

    process = subprocess.Popen(
        ["python", "../main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    process.wait()

    assert process.stdout.read().decode("utf-8") == "apollo> "

    process.communicate(input="hello")

    assert process.stdout


def test_main_correct(change_test_dir):

    process = subprocess.Popen(
        ["python", "../main.py", "apollo_files/hello.apo"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert process.wait() == 0


def test_main_incorrect_args(change_test_dir):

    process = subprocess.Popen(
        ["python", "../main.py", "apollo_files/hello.apo", "incorrect", "args"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert process.wait() == 2


def test_main_file_not_found(change_test_dir):

    process = subprocess.Popen(
        ["python", "../main.py", "hello.apo"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert process.wait() == 2

    assert process.stderr.read().decode("utf-8") == "file hello.apo was not found\n"
