# PROVES Kit RP2040 v5b CircuitPython Flight Software and Ground Station

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![CI](https://github.com/proveskit/CircuitPython_RP2350_v5b/actions/workflows/ci.yaml/badge.svg)

This is the template repository for v5b PROVES Kit Flight Controller boards. Head to our [docs site](https://proveskit.github.io/pysquared/) to get started.

## Running power tests

To run the power tests run

> test_power()

it will print to console and also write to a file

> read_power_file()

to read it

to make the circuitpython a detachable drive again, run

> erase_boot_file()

and then reboot the flight computer then you can drag and drop the file or load more code

to get back to the boot detaching itself run

> put_back_boot_file

you can also erase the power file with

> erase_power_file()

otherwise the tests will append to each other
