"""Plain-text view of bounded batch evidence."""


def render(report):
    arc, subset = report['minimum_arc'], report['largest_coherent_subset']
    lines = [f"serial-span: {report['bits']}-bit batch, {report['observation_count']} observations",
             f"coherent={str(report['coherent']).lower()} distinct={report['distinct_count']} "
             f"equal_pairs={report['equal_observation_pairs']} undefined_pairs={report['undefined_observation_pairs']}",
             f"minimum arc: {arc['start']} -> {arc['end']}, span={arc['span']}; required span < {report['half_range']}"]
    witness = report['witness']
    if witness:
        if witness['kind'] == 'comparison_cycle':
            sequence = witness['serials'] + witness['serials'][:1]
            lines.append('comparison cycle: ' + ' < '.join(sequence))
        else:
            lines.append('undefined pair: ' + ' vs '.join(witness['serials']))
        lines.append('witness records: ' + ', '.join(map(str, witness['records'])))
    else:
        lines.append('serial order records: ' + ', '.join(map(str, report['serial_order_records'])))
    lines.append(f"largest coherent subset: retain={subset['retained_count']} exclude={subset['excluded_count']} "
                 f"start={subset['start']} span={subset['span']}")
    lines.append('retained records: ' + ', '.join(map(str, subset['retained_records'])))
    lines.append('excluded records: ' + (', '.join(map(str, subset['excluded_records'])) or '(none)'))
    lines.append('Comparison model only: no chronology, wrap-count recovery or automatic repair.')
    return '\n'.join(lines)
