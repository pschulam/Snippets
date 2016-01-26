"""Test edf.py module."""

from imp import reload
from pprint import pprint

import edf
reload(edf)

edf_filename = 'test/sample.edf'

with open(edf_filename, 'rb') as f:
    # header = edf._read_header(f)
    header, signals = edf.header_and_signals(f)

pprint(header)
pprint(signals)
pprint(edf.samples_per_sec(header))
