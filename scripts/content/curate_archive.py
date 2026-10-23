"""Remove generated repetitions and build a guarded, concise archive release."""
import argparse
import json
from collections import defaultdict
from pathlib import Path

from build import digest, render

# Editorial estimates for the existing local contracts. These are not ACMP ratings.
DIFFICULTY = {
    'aplusb':2, 'sum_n':8, 'sum_squares':16, 'sum_cubes':20, 'mod_sum':12,
    'mod_product':15, 'power':32, 'fibonacci':35, 'tribonacci':24, 'gcd':19,
    'lcm':19, 'abs_diff':3, 'min_three':4, 'median_three':8, 'sign':3,
    'array_sum':7, 'array_max':7, 'array_min':7, 'average':10, 'positive':8,
    'even_count':8, 'second_max':15, 'reverse_array':9, 'prefix':18, 'distinct_count':18,
    'sort_asc':15, 'sort_desc':15, 'kth':22, 'median':22, 'inversions':48,
    'sort_even':18, 'closest':15, 'mode':24, 'sort_unique':20, 'merge':22,
    'prime':25, 'divisor_count':26, 'divisor_sum':28, 'digit_sum':12, 'digit_count':10,
    'rectangle_area':3, 'rectangle_perimeter':3, 'triangle_area':5, 'distance':12,
    'circle_area':10, 'coins':20, 'pieces':4, 'budget':25, 'parity':3, 'leap':12,
    'fizzbuzz':8, 'binary':16, 'reverse_number':16, 'factorial':16, 'choose':32,
    'arrangements':24, 'pascal':28, 'catalan':45, 'stairs':26, 'max_subarray':35,
    'find':12, 'lower_bound':27, 'at_least':27, 'isqrt':28, 'icbrt':32,
    'length':3, 'reverse_string':8, 'vowels':10, 'consonants':10, 'uppercase':8,
    'palindrome':16, 'frequent_char':18, 'deduplicate_string':20, 'words':18, 'rle':24,
    'nn26-abiturients':30, 'nn26-bells':20, 'nn26-desks':15, 'nn26-digitsort':28,
    'nn26-pik-lenin':32, 'nn26-trails':35,
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('current', type=Path)
    parser.add_argument('--original', type=Path, default=Path('artifacts/content-audit/original.json'))
    parser.add_argument('--output', type=Path, default=Path('artifacts/acmp-migration/curated.json'))
    args = parser.parse_args()
    current = json.loads(args.current.read_text(encoding='utf-8'))
    original = json.loads(args.original.read_text(encoding='utf-8-sig'))
    originals = {p['code']:p for p in original['problems']}
    assert not current['translations'], 'Translated statements need their own review'
    assert set(originals) == {p['code'] for p in current['problems']}, 'Inventory changed'
    contest_ids = {p['problem_id'] for p in current['contest_problems']}
    families = defaultdict(list)
    rows = []
    for problem in current['problems']:
        updated = render(originals[problem['code']])
        family = updated['family']
        # Prefer an existing contest/solved problem as the surviving archive entry.
        families[family].append(problem)
        name = updated['name'].split(' (N ≤ ')[0].split(' #')[0]
        before = {key:problem[key] for key in ('name','description')}
        before.update(difficulty=problem.get('difficulty'), is_listed=problem.get('is_listed', True))
        protected = {key:problem[key] for key in ('time_limit','memory_limit','points','partial','is_public','is_manually_managed')}
        rows.append(dict(id=problem['id'], code=problem['code'], family=family,
                         before=before, protected=protected,
                         after=dict(name=name, description=updated['description'],
                                    difficulty=DIFFICULTY[family], is_listed=False)))
    assert set(families) == set(DIFFICULTY), 'Unreviewed family'
    kept = set()
    for problems in families.values():
        chosen = sorted(problems, key=lambda p:(p['id'] not in contest_ids, -p['user_count'], p['code']))[0]
        kept.add(chosen['code'])
    for row in rows:
        row['after']['is_listed'] = row['code'] in kept
    release = dict(schema=2, problems=rows, current_sha256=digest(current),
                   listed=len(kept), hidden=len(rows)-len(kept), difficulty_source='editorial estimates')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(release, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(dict(reviewed=len(rows), listed=release['listed'], hidden=release['hidden'])))


if __name__ == '__main__':
    main()
