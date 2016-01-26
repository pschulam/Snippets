"""Tools for reading the European Data Format (EDF).

For information on the spec see:

http://www.edfplus.info/

"""
from collections import OrderedDict, namedtuple

import numpy as np

__all__ = ['header_and_signals', 'samples_per_sec']


_RAW_INT_SIZE = 2
"""The size in bytes of the integer encoding of signal samples."""

StartDate = namedtuple('StartDate', ['year', 'month', 'day'])
"""Data structure for the start date field."""

StartTime = namedtuple('StartTime', ['hour', 'minute', 'second'])
"""Data structure for the start time field."""


def header_and_signals(edf_file):
    """Extract the header and signals from an EDF file.

    Parameters
    ----------
    edf_file : A file object opened to read bytes.

    Returns
    -------
    A 2-tuple containing a dictionary of header fields and a
    dictionary of signals.

    """
    assert 'b' in edf_file.mode
    assert edf_file.tell() == 0

    header = _read_header(edf_file)
    signals = _read_signals(edf_file, header)

    return header, signals


def samples_per_sec(header):
    """Number of samples per second for each signal."""
    hertz = header['samples_per_record'] / header['seconds_per_record']
    return OrderedDict(zip(header['label'], hertz))


def _read_header(edf_file):
    """Extract the contents of the EDF header as a dictionary.

    Parameters
    ----------
    edf_file : An open file object.

    Returns
    -------
    A dictionary mapping filed names to values.

    """
    read = edf_file.read
    read_ascii = lambda n: read(n).decode('ascii').strip()
    read_int = lambda n: int(read_ascii(n))
    read_float = lambda n: float(read_ascii(n))

    version = int(read(8).decode('ascii').strip())
    assert version == 0

    header = OrderedDict()

    header['local_patient_id'] = read_ascii(80)
    header['local_recording_id'] = read_ascii(80)

    unpack_ts = lambda n: [int(x) for x in read_ascii(n).split('.')]
    header['start_date'] = StartDate(*unpack_ts(8))
    header['start_time'] = StartTime(*unpack_ts(8))

    header['num_header_bytes'] = read_int(8)

    read(44)

    header['num_records'] = read_int(8)
    header['seconds_per_record'] = read_int(8)
    header['num_signals'] = nsig = read_int(4)

    header['label'] = [read_ascii(16) for _ in range(nsig)]
    header['transducer_type'] = [read_ascii(80) for _ in range(nsig)]
    header['units'] = [read_ascii(8) for _ in range(nsig)]
    header['physical_min'] = np.array([read_float(8) for _ in range(nsig)])
    header['physical_max'] = np.array([read_float(8) for _ in range(nsig)])
    header['digital_min'] = np.array([read_float(8) for _ in range(nsig)])
    header['digital_max'] = np.array([read_float(8) for _ in range(nsig)])
    header['prefiltering'] = [read_ascii(80) for _ in range(nsig)]
    header['samples_per_record'] = np.array([read_int(8) for _ in range(nsig)])

    read(32 * nsig)

    assert edf_file.tell() == header['num_header_bytes']

    return header


def _read_signals(edf_file, header):
    """Read all signals from the file.

    Parameters
    ----------
    edf_file : An open file object from which a header has been read.
    header : The header dictionary read from the file object.

    Returns
    -------
    A dictionary containing the full signals.

    """
    signals = OrderedDict([(label, []) for label in header['label']])

    while True:
        try:
            record = _read_record(edf_file, header)
        except EOFError:
            break

        for label, signal in record.items():
            signals[label].append(signal)

    for label, signal in signals.items():
        signals[label] = np.concatenate(signal)

    return signals


def _read_record(edf_file, header):
    """Read a single record from the EDF file.

    Parameters
    ----------
    edf_file : An open file object from which a header has been read.
    header : The header dictionary read from the file object.

    Returns
    -------
    A list containing the signals in the record as arrays.

    """
    labels = header['label']
    signals = OrderedDict()

    for channel in range(header['num_signals']):
        num_bytes = _bytes_per_record(channel, header)
        raw_bytes = edf_file.read(num_bytes)
        if not len(raw_bytes) == num_bytes:
            raise EOFError('Could not read a full record.')

        digital = np.fromstring(raw_bytes, '<i2').astype(np.float)
        physical = _dig_to_phys(digital, channel, header)
        signals[labels[channel]] = physical

    return signals


def _bytes_per_record(channel, header):
    """The number of bytes from this channel per record."""
    num_samples = header['samples_per_record'][channel]
    return num_samples * _RAW_INT_SIZE


def _dig_to_phys(dig, channel, header):
    """Convert digital values to physical values."""
    pmin = header['physical_min'][channel]
    pmax = header['physical_max'][channel]
    dmin = header['digital_min'][channel]
    dmax = header['digital_max'][channel]
    gain = (pmax - pmin) / (dmax - dmin)
    return (dig - dmin) * gain + pmin
