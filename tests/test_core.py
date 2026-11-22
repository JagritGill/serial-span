import copy
import itertools
import random
import unittest

from serial_span import InputError, analyze


def precedes(a, b, bits):
    # Independent literal RFC inequalities, not the production arc calculation.
    half = 2 ** (bits - 1)
    return (a < b and b - a < half) or (a > b and a - b > half)


def finite_ring_oracle(values, bits):
    # Materialize every integer point and rotate at EVERY possible cut. Small
    # rings only; no production validation, gap algorithm or subset helper.
    ring = list(range(2 ** bits))
    arcs, cohorts = [], []
    for cut in ring:
        walk = ring[cut:] + ring[:cut]
        last = max(walk.index(v) for v in values)
        arcs.append((last, cut, walk[last]))
        window = set(walk[:len(ring) // 2])
        keep = [i for i, v in enumerate(values, 1) if v in window]
        if cut in values:
            cohorts.append((-len(keep), cut, keep))
    return min(arcs), min(cohorts)


class CoreTests(unittest.TestCase):
    def check_model(self, values, bits):
        doc = dict(bits=bits, serials=list(map(str, values)))
        report = analyze(doc)
        (span, start, end), (negative, subset_start, keep) = finite_ring_oracle(values, bits)
        self.assertEqual(report['minimum_arc'], dict(start=str(start), end=str(end), span=str(span)))
        self.assertEqual(report['coherent'], span < 2 ** (bits - 1))
        self.assertEqual(report['distinct_count'], len(set(values)))
        self.assertEqual(report['equal_observation_pairs'], sum(a == b for a,b in itertools.combinations(values, 2)))
        undefined = sum(a != b and not precedes(a,b,bits) and not precedes(b,a,bits)
                        for a,b in itertools.combinations(values,2))
        self.assertEqual(report['undefined_observation_pairs'], undefined)
        subset = report['largest_coherent_subset']
        self.assertEqual(subset['retained_count'], -negative)
        self.assertEqual(subset['start'], str(subset_start))
        self.assertEqual(subset['retained_records'], keep)
        self.assertEqual(subset['excluded_records'], [i for i in range(1,len(values)+1) if i not in keep])
        retained = [values[i-1] for i in keep]
        self.assertEqual(subset['span'], str(max((v-subset_start) % (2**bits) for v in retained)))
        self.assertLess(int(subset['span']), 2 ** (bits-1))
        witness = report['witness']
        if report['coherent']:
            self.assertIsNone(witness)
            order = report['serial_order_records']
            self.assertEqual(sorted(order), list(range(1,len(values)+1)))
            for i,j in itertools.combinations(order,2):
                self.assertTrue(values[i-1] == values[j-1] or precedes(values[i-1],values[j-1],bits))
        else:
            self.assertIsNone(report['serial_order_records'])
            records = witness['records']
            self.assertEqual(witness['serials'], [str(values[i-1]) for i in records])
            if undefined:
                self.assertEqual(witness['kind'], 'half_range_pair')
                a,b = [values[i-1] for i in records]
                self.assertFalse(precedes(a,b,bits) or precedes(b,a,bits) or a == b)
            else:
                self.assertEqual(witness['kind'], 'comparison_cycle')
                cycle = [values[i-1] for i in records]
                for a,b in zip(cycle, cycle[1:] + cycle[:1]):
                    self.assertTrue(precedes(a,b,bits))

    def test_all_ordered_three_bit_batches_through_four_records(self):
        count = 0
        for size in range(1,5):
            for values in itertools.product(range(8), repeat=size):
                self.check_model(values, 3); count += 1
        self.assertEqual(count,4680)

    def test_seeded_larger_rings(self):
        rng = random.Random(221126)
        for _ in range(300):
            bits = rng.choice([4,5,6])
            self.check_model([rng.randrange(2**bits) for _ in range(rng.randrange(1,13))],bits)

    def test_subset_optimality_by_exhaustive_removal(self):
        # Check a second independent objective directly: every record subset.
        rng = random.Random(1982)
        for _ in range(100):
            values = [rng.randrange(16) for _ in range(7)]
            best = 0
            for mask in range(1,1 << 7):
                subset = [v for i,v in enumerate(values) if mask & (1 << i)]
                arc,_ = finite_ring_oracle(subset,4)
                if arc[0] < 8: best = max(best,len(subset))
            r = analyze(dict(bits=4,serials=list(map(str,values))))
            self.assertEqual(r['largest_coherent_subset']['retained_count'],best)

    def test_weighted_tie_and_witness(self):
        r = analyze(dict(bits=8,serials=['0','100','200','200','200']))
        self.assertEqual(r['witness']['serials'],['0','100','200'])
        self.assertEqual(r['witness']['forward_distances'],['100','100','56'])
        self.assertEqual(r['largest_coherent_subset']['retained_records'],[2,3,4,5])
        self.assertEqual(r['largest_coherent_subset']['start'],'100')

    def test_half_range_is_not_cycle_or_equality(self):
        r = analyze(dict(bits=8,serials=['0','128','0','128']))
        self.assertEqual(r['undefined_observation_pairs'],4)
        self.assertEqual(r['equal_observation_pairs'],2)
        self.assertEqual(r['witness']['kind'],'half_range_pair')
        self.assertEqual(r['minimum_arc']['span'],'128')
        self.assertFalse(r['coherent'])

    def test_wrap_order_duplicates_and_singleton(self):
        r = analyze(dict(bits=8,serials=['2','250','6','2']))
        self.assertEqual(r['serial_order_records'],[2,1,4,3])
        self.assertEqual(r['minimum_arc'],dict(start='250',end='6',span='12'))
        self.check_model([3,3,3],2)

    def test_64_bit_precision_and_half_boundaries(self):
        m=2**64;h=m//2
        r = analyze(dict(bits=64,serials=[str(m-2),'1']))
        self.assertEqual(r['minimum_arc']['span'],'3')
        self.assertEqual(r['modulus'],str(m))
        for distance,coherent in [(h-1,True),(h,False),(h+1,True)]:
            r=analyze(dict(bits=64,serials=['0',str(distance)]))
            self.assertEqual(r['coherent'],coherent)

    def test_maximum_observations(self):
        r=analyze(dict(bits=8,serials=['0']*128))
        self.assertEqual(r['equal_observation_pairs'],8128)
        self.assertEqual(r['largest_coherent_subset']['retained_count'],128)

    def test_distinct_record_bound_without_antipodes(self):
        r=analyze(dict(bits=9,serials=[str(3*i) for i in range(128)]))
        self.assertEqual(r['minimum_arc']['span'],'381')
        self.assertEqual(r['undefined_observation_pairs'],0)
        self.assertEqual(r['witness']['serials'],['0','3','258'])
        self.assertEqual(r['largest_coherent_subset']['retained_count'],86)
        self.assertEqual(r['largest_coherent_subset']['start'],'0')

    def test_input_unchanged_and_repeatable(self):
        d=dict(bits=8,serials=['200','0','100','0']);saved=copy.deepcopy(d)
        first=analyze(d);self.assertEqual(d,saved);self.assertEqual(analyze(d),first)

    def test_invalid_shapes_values_and_bounds(self):
        bad=[None,[],{},dict(bits=8,serials=[]),dict(bits=8,serials=['0'],extra=1)]
        bad += [dict(bits=b,serials=['0']) for b in [True,1,65,8.0,'8']]
        bad += [dict(bits=8,serials=[v]) for v in [0,True,None,'','00','01','+1','-1',' 1','1 ','1.0','1e2','١','256','1'*5000,'bad\x1b[31m']]
        bad += [dict(bits=64,serials=[str(2**64)]),dict(bits=8,serials=['0']*129)]
        for doc in bad:
            with self.subTest(doc=doc), self.assertRaises(InputError):analyze(doc)


if __name__=='__main__':unittest.main()
