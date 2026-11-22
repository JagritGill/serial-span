"""Bounded batch evidence for RFC 1982 comparison, without sequence unwrapping."""

from itertools import combinations
import re

DECIMAL = re.compile(r"(?:0|[1-9][0-9]{0,19})\Z")
MAX_RECORDS = 128


class InputError(ValueError):
    """Invalid or unsupported input; messages do not echo supplied values."""


def _validate(document):
    if type(document) is not dict or set(document) != {"bits", "serials"}:
        raise InputError("expected exactly bits and serials")
    bits, raw = document["bits"], document["serials"]
    if type(bits) is not int or not 2 <= bits <= 64:
        raise InputError("bits must be an integer from 2 through 64")
    if type(raw) is not list or not 1 <= len(raw) <= MAX_RECORDS:
        raise InputError("serials must contain 1..128 decimal strings")
    modulus = 1 << bits
    values = []
    for i, item in enumerate(raw, 1):
        if type(item) is not str or not DECIMAL.fullmatch(item):
            raise InputError(f"record {i}: expected a canonical unsigned decimal string")
        value = int(item)
        if value >= modulus:
            raise InputError(f"record {i}: serial exceeds the declared bit width")
        values.append(value)
    return bits, values


def _minimum_arc(unique, modulus):
    # A covering arc is the complement of an empty gap between adjacent values.
    candidates = []
    for i, end in enumerate(unique):
        start = unique[(i + 1) % len(unique)]
        gap = (start - end) % modulus if len(unique) > 1 else modulus
        candidates.append((modulus - gap, start, end))
    span, start, end = min(candidates)
    return {"start": str(start), "end": str(end), "span": str(span)}


def analyze(document: object) -> dict:
    """Return a fresh deterministic batch report; never mutate or repair input.

    Serial-sized values in the report are decimal strings to preserve 64-bit
    precision in JSON consumers. Source record numbers are one-based integers.
    """
    bits, values = _validate(document)
    modulus, half = 1 << bits, 1 << (bits - 1)
    positions = {}
    for index, value in enumerate(values, 1):
        positions.setdefault(value, []).append(index)
    unique = sorted(positions)
    arc = _minimum_arc(unique, modulus)
    coherent = int(arc["span"]) < half
    equals = sum(len(indices) * (len(indices) - 1) // 2 for indices in positions.values())
    antipodal = [(a, a + half) for a in unique if a < half and a + half in positions]
    undefined = sum(len(positions[a]) * len(positions[b]) for a, b in antipodal)
    witness = None
    if antipodal:
        a, b = antipodal[0]
        witness = {"kind": "half_range_pair", "records": [positions[a][0], positions[b][0]],
                   "serials": [str(a), str(b)], "forward_distance": str(half)}
    elif not coherent:
        # With no antipodal pair, the distinct comparisons form a tournament.
        # A non-transitive tournament contains a directed triangle.
        for a, b, c in combinations(unique, 3):
            distances = [b - a, c - b, modulus - c + a]
            if all(0 < distance < half for distance in distances):
                witness = {"kind": "comparison_cycle",
                           "records": [positions[v][0] for v in (a, b, c)],
                           "serials": [str(v) for v in (a, b, c)],
                           "forward_distances": [str(x) for x in distances]}
                break
        if witness is None:
            raise AssertionError("incoherent batch has no comparison witness")

    # Every nonempty compatible subset has an observed first value. Including
    # all records strictly within half a turn from it cannot reduce its size.
    best = None
    for start in unique:
        keep = [i for i, value in enumerate(values, 1) if (value - start) % modulus < half]
        candidate = (-len(keep), start, keep)
        if best is None or candidate[:2] < best[:2]:
            best = candidate
    negative_count, start, keep = best
    kept = set(keep)
    excluded = [i for i in range(1, len(values) + 1) if i not in kept]
    span = max((values[i - 1] - start) % modulus for i in keep)
    subset = {"start": str(start), "end": str((start + span) % modulus), "span": str(span),
              "retained_count": -negative_count, "excluded_count": len(excluded),
              "retained_records": keep, "excluded_records": excluded}
    order = None
    if coherent:
        origin = int(arc["start"])
        order = sorted(range(1, len(values) + 1), key=lambda i: ((values[i - 1] - origin) % modulus, i))
    return {"schema_version": 1, "bits": bits, "modulus": str(modulus), "half_range": str(half),
            "observation_count": len(values), "distinct_count": len(unique),
            "equal_observation_pairs": equals, "undefined_observation_pairs": undefined,
            "coherent": coherent, "minimum_arc": arc, "serial_order_records": order,
            "witness": witness, "largest_coherent_subset": subset}
