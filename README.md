# Compare-XML-ONVIF-Test

*Python 3.6.5*

## Requirements

- pytest >= 3.5.0
- xmlschema >= 0.9.29
- openpyxl >= 2.5.3

```sh
pip install xmlschema
pip install openpyxl
pip install pytest
```

## Description

This tool is for compare two XML files generated by the ONVIF Device Test Tool 17.12.

## Usage

```
python compare_XML_ONVIF_tests.py <file 1> [<file 2>]
```
File 2 is optionnal.

If there is only one file, the program will output some stats about results on stdout.

If two files are given, the program will compare them and output results in an Excel file named with the name of the two input files.

The program look for tests failed in one file but passed in the other. When found, it creates a new sheet named with the row number from the main sheet. In this new sheet, the program print all steps done and append the error message if the step is failed.
