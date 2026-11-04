#!/usr/bin/env python3
"""Reproduce the corpus counts, Table II (theme shares), and the control-locus indicators of Paper 2.

usage: python3 scripts/bibliometrics.py data/harvest/harvest.json [--sample-dropped N SEED out.csv]

All rules are listed here and in Appendix A of the paper. Shares come with 95% Wilson intervals.
"""
import json, re, sys, math, csv, random, collections
from scipy.stats import fisher_exact

AGENT = re.compile(r'(agent|assistant|dialog|conversation|chat)', re.I)  # title OR abstract; reproduces n = 840

# Table II: title-level theme rules (case-insensitive; a title may match several themes)
THEMES = [
    ('Benchmarks, evaluation',              r'benchmark|evaluat'),
    ('Graph or structured memory',          r'graph|structured|hierarch|tree'),
    ('Retrieval, RAG',                      r'retriev|\bRAG\b'),
    ('Security, privacy',                   r'secur|privacy|attack|poison|safety|leak'),
    ('Forgetting, updating, consolidation', r'forget|updat|consolidat|obsolete|outdated'),
    ('Multi-agent or shared memory',        r'multi-agent|multiagent|shared|collaborat'),
    ('Personalization',                     r'personal'),
    ('Learned control (RL, policy)',        r'reinforcement|\bRL\b|policy optimi[sz]ation|\bGRPO\b|\bPPO\b'),
    ('Long context, compression',           r'long context|long-context|compress'),
    ('Parametric memory, editing',          r'parametric|knowledge editing|model editing|weights|fine-tun'),
]

# Control-locus indicators: abstract-level rules (more sensitive than titles; still keyword-based)
LOCI = [
    ('Learned (RL-trained memory policy)', r'reinforcement learning|\bRL\b|\bGRPO\b|\bPPO\b|policy optimi[sz]ation'),
    ('Model-directed (tool/function calls)', r'tool call|function call|memory tools?\b|memory operations? as (tools|actions)'),
    ('Architectural (test-time memory)', r'test-time (training|learning|memori[sz]ation)|neural memory module|memory layer'),
]

def wilson(k, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (100 * max(0, c - h), 100 * min(1, c + h))

def main():
    d = json.load(open(sys.argv[1])); recs = d['records']
    uniq = len(recs); titled = [r for r in recs if r['topic_centric']]
    corp = [r for r in titled if AGENT.search(r['title'] + ' ' + r['abstract'])]
    year = lambda r: r['published'][:4]
    n = collections.Counter(year(r) for r in corp)
    print(f'unique={uniq} memory-titled={len(titled)} agent-corpus={len(corp)} by year={dict(sorted(n.items()))}')
    pvals = []
    print('\nTable II (title rules): theme | 2025 % [95% CI] | 2026 % [95% CI]')
    for name, rx in THEMES:
        p = re.compile(rx, re.I); c = collections.Counter(year(r) for r in corp if p.search(r['title']))
        row = []
        for y in ('2025', '2026'):
            lo, hi = wilson(c[y], n[y]); row.append(f'{100*c[y]/n[y]:.1f} [{lo:.1f}, {hi:.1f}] (k={c[y]})')
        _, pv = fisher_exact([[c['2025'], n['2025'] - c['2025']], [c['2026'], n['2026'] - c['2026']]])
        pvals.append((name, pv))
        print(f'{name:38s} | ' + ' | '.join(row) + f' | Fisher p={pv:.4f}')
    # Holm-Bonferroni over the 10 themes
    m = len(pvals); adj = {}; run = 0.0
    for i, (name, pv) in enumerate(sorted(pvals, key=lambda x: x[1])):
        run = max(run, min(1.0, (m - i) * pv)); adj[name] = run
    print('Holm-adjusted p:', {k: round(v, 4) for k, v in adj.items()})
    print('\nControl-locus indicators (abstract rules): locus | 2024 | 2025 | 2026')
    for name, rx in LOCI:
        p = re.compile(rx, re.I); c = collections.Counter(year(r) for r in corp if p.search(r['abstract']))
        row = []
        for y in ('2024', '2025', '2026'):
            lo, hi = wilson(c[y], n[y]); row.append(f'{100*c[y]/n[y]:.1f} [{lo:.1f}, {hi:.1f}] (k={c[y]})')
        print(f'{name:38s} | ' + ' | '.join(row))
    if '--sample-corpus' in sys.argv:
        i = sys.argv.index('--sample-corpus'); k, seed, out = int(sys.argv[i+1]), int(sys.argv[i+2]), sys.argv[i+3]
        sample = random.Random(seed).sample(sorted(corp, key=lambda r: r['id']), k)
        with open(out, 'w', newline='') as f:
            w = csv.writer(f); w.writerow(['id', 'published', 'title', 'abstract', 'agent_memory_coder1', 'notes'])
            for r in sample: w.writerow([r['id'], r['published'], r['title'], r['abstract'], '', ''])
        print(f'wrote {k} of {len(corp)} corpus records to {out} (seed {seed})')
    if '--sample-dropped' in sys.argv:
        i = sys.argv.index('--sample-dropped'); k, seed, out = int(sys.argv[i+1]), int(sys.argv[i+2]), sys.argv[i+3]
        dropped = sorted((r for r in recs if not r['topic_centric']), key=lambda r: r['id'])
        sample = random.Random(seed).sample(dropped, k)
        with open(out, 'w', newline='') as f:
            w = csv.writer(f); w.writerow(['id', 'published', 'title', 'abstract', 'in_scope_coder1', 'in_scope_coder2', 'notes'])
            for r in sample: w.writerow([r['id'], r['published'], r['title'], r['abstract'], '', '', ''])
        print(f'\nwrote {k} of {len(dropped)} title-dropped records to {out} (seed {seed})')

if __name__ == '__main__':
    main()
