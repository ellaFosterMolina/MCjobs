""" Combines EFM all_congress dataset with 

"""
# icpsr code for merging
# expect 1-2% not match

import sys
if sys.version_info < (3, 6, 0):
    sys.exit("Relies on OrderedDict features in Python >= 3.6.0.")

import csv
import argparse


_all_congress = "allCongressDataPublish.csv"
_lep = "LEPData93to110Congresses.txt"


def _all_congress_key(row):
    return (row["congNum"], row["icpsr"])


def read_all_congress(source, key_method=_all_congress_key):
    with open(source) as s:
        reader = csv.DictReader(s)
        for_merging = {}
        for row in reader:
                for_merging[key_method(row)] = row
    return for_merging


def _lep_key(row):
    #print(row.keys())
    return (row["congress"], row["icpsr"])


def read_lep(source, key_method=_lep_key):
    # TODO: handle second header line in code.
    with open(source) as s:
        reader = csv.DictReader(s, delimiter="\t")
        for_merging = {}
        for row in reader:
                for_merging[key_method(row)] = row
    return for_merging


def combine(first, second):
    combined = {}
    for k, d in first.items():
        if k in second:
            combined[k] = list(d.values()) + list(second[k].values())

    # TODO: less wasteful.
    unmatched_firsts = {k:v.values() for k, v in first.items() if k not in second}
    unmatched_seconds = {k:v.values() for k, v in second.items() if k not in first}

    return combined, unmatched_firsts, unmatched_seconds 


def _simple_write(lines, output, sep=","):
    if not lines:
        return

    with open(output, "w") as o:
        for k, v in lines.items():
            o.write(sep.join(v) + "\n")


def main():
    parser = argparse.ArgumentParser(description="One of utility to merge \
    different congressional data sets.")
    args = parser.parse_args()


    all_congress = read_all_congress(_all_congress)
    lep = read_lep(_lep)
    combined, all_congress_unmatched, lep_unmatched = combine(all_congress, lep)

    _simple_write(combined, "merged.csv")
    _simple_write(all_congress_unmatched, "all_congress_unmatched.csv")
    _simple_write(lep_unmatched, "lep_unmatched.csv")


if __name__ == "__main__":
        main()
