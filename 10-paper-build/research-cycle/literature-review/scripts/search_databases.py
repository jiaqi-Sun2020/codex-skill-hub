#!/usr/bin/env python3
"""
Literature Database Search Script
Processes normalized search records locally; does not query databases.
"""

import argparse
import json
import math
import re
import sys
import stat
from pathlib import Path
from urllib.parse import unquote
from typing import Dict, List
from datetime import datetime

def format_search_results(results: List[Dict], output_format: str = 'json') -> str:
    """
    Format search results for output.

    Args:
        results: List of search results
        output_format: Format (json, markdown, or bibtex)

    Returns:
        Formatted string
    """
    if output_format == 'json':
        return json.dumps(results, indent=2)

    elif output_format == 'markdown':
        md = f"# Literature Search Results\n\n"
        md += f"**Export Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        md += f"**Total Results**: {len(results)}\n\n"

        for i, result in enumerate(results, 1):
            md += f"## {i}. {result.get('title', 'Untitled')}\n\n"
            md += f"**Authors**: {result.get('authors', 'Unknown')}\n\n"
            md += f"**Year**: {result.get('year', 'N/A')}\n\n"
            md += f"**Source**: {result.get('source', 'Unknown')}\n\n"

            if result.get('abstract'):
                md += f"**Abstract**: {result['abstract']}\n\n"

            if result.get('doi'):
                md += f"**DOI**: [{result['doi']}](https://doi.org/{result['doi']})\n\n"

            if result.get('url'):
                md += f"**URL**: {result['url']}\n\n"

            if result.get('citations') is not None:
                md += f"**Citations**: {result['citations']}\n\n"

            if result.get('triage_year_state', '').startswith('pending'):
                md += "**Year review**: pending; not established eligible by date\n\n"
            if result.get('triage_duplicate_records'):
                md += "**Duplicate/version review**: pending; retained originals: " + json.dumps(result['triage_duplicate_records'], ensure_ascii=False) + "\n\n"
            md += "---\n\n"

        return md

    elif output_format == 'bibtex':
        bibtex = ""
        used_keys = set()
        for i, result in enumerate(results, 1):
            entry_type = result.get('type', 'article')
            base_key = re.sub(r'[^a-zA-Z0-9_-]', '',
                              f"{result.get('first_author') or 'unknown'}{result.get('year') or '0000'}")
            cite_key, suffix = base_key, 2
            while cite_key in used_keys:
                cite_key = f'{base_key}_{suffix}'
                suffix += 1
            used_keys.add(cite_key)

            if result.get('triage_year_state', '').startswith('pending') or result.get('triage_duplicate_records'):
                bibtex += "% Pending triage/version review; inspect JSON export and raw records.\n"
            bibtex += f"@{entry_type}{{{cite_key},\n"
            bibtex += f"  title = {{{result.get('title', '')}}},\n"
            bibtex += f"  author = {{{result.get('authors', '')}}},\n"
            bibtex += f"  year = {{{result.get('year', '')}}},\n"

            if result.get('journal'):
                bibtex += f"  journal = {{{result['journal']}}},\n"

            if result.get('volume'):
                bibtex += f"  volume = {{{result['volume']}}},\n"

            if result.get('pages'):
                bibtex += f"  pages = {{{result['pages']}}},\n"

            if result.get('doi'):
                bibtex += f"  doi = {{{result['doi']}}},\n"

            bibtex += "}\n\n"

        return bibtex

    else:
        raise ValueError(f"Unknown format: {output_format}")

def normalize_record_doi(value) -> str:
    return unquote(re.sub(r'^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)', '',
                         str(value or '').strip(), flags=re.I)).lower()


def deduplicate_results(results: List[Dict]) -> List[Dict]:
    """Group hits, not studies; keep conflicting originals and source indices."""
    seen = {}
    unique = []
    for index, result in enumerate(results):
        doi = normalize_record_doi(result.get('doi'))
        title = str(result.get('title') or '').lower().strip()
        key = ('doi', doi) if doi else (('title', title) if title else ('row', index))
        if key in seen:
            representative = seen[key]
            representative.setdefault('triage_duplicate_records', []).append(dict(result))
            representative.setdefault('triage_duplicate_indices', []).append(index)
            representative['triage_duplicate_review'] = 'pending'
        else:
            representative = dict(result)
            representative['triage_source_index'] = index
            seen[key] = representative
            unique.append(representative)
    return unique

def rank_results(results: List[Dict], criteria: str = 'citations') -> List[Dict]:
    """
    Rank results by specified criteria.

    Args:
        results: List of search results
        criteria: Ranking criteria (citations, year, relevance)

    Returns:
        Ranked list
    """
    field = {'citations': 'citations', 'year': 'year', 'relevance': 'relevance_score'}.get(criteria)
    if field is None:
        return results
    def score(record):
        try:
            value = float(record.get(field))
            return value if math.isfinite(value) else float('-inf')
        except (ValueError, TypeError):
            return float('-inf')
    return sorted(results, key=score, reverse=True)

def parse_record_year(value):
    """Accept an explicit four-digit calendar year; never change the raw field."""
    if isinstance(value, bool) or not re.fullmatch(r'\d{4}', str(value)):
        return None
    year = int(value)
    return year if 1 <= year <= 9999 else None


def filter_by_year(results: List[Dict], start_year: int = None, end_year: int = None) -> List[Dict]:
    """Always assess year information; apply a range only when requested.

    Unknown/conflicting years survive filtering as pending. Kept original source
    indices refer to raw inputs, not positions after filtering or ranking.
    """
    filtered = []
    has_range = start_year is not None or end_year is not None
    for index, original in enumerate(results):
        result = dict(original)
        result.setdefault('triage_source_index', index)
        duplicates = result.get('triage_duplicate_records', [])
        def year_identity(record):
            raw = record.get('year')
            parsed = parse_record_year(raw)
            return ('parsed', parsed) if parsed is not None else (
                'unparsed', json.dumps(raw, sort_keys=True, ensure_ascii=False))
        if duplicates and len({year_identity(r) for r in [result, *duplicates]}) > 1:
            result['triage_year_information_state'] = 'conflicting'
            result['triage_year_range_state'] = 'pending_review' if has_range else 'not_requested'
            result['triage_year_state'] = 'pending_version_conflict'
            filtered.append(result)
            continue  # a representative's old date must not hide a newer report
        value = result.get('year')
        year = parse_record_year(value)
        if year is not None:
            result['triage_year_information_state'] = 'parsed'
            if start_year is not None and year < start_year:
                continue
            if end_year is not None and year > end_year:
                continue
            result['triage_year_range_state'] = 'within_requested_range' if has_range else 'not_requested'
            result['triage_year_state'] = ('within_requested_range_not_eligibility' if has_range
                                          else 'parsed_not_range_filtered')
        else:
            result['triage_year_information_state'] = ('missing' if value is None or
                (isinstance(value, str) and not value.strip()) else 'unparseable')
            result['triage_year_range_state'] = 'pending_review' if has_range else 'not_requested'
            result['triage_year_state'] = 'pending'
        filtered.append(result)
    return filtered

def generate_search_summary(results: List[Dict]) -> Dict:
    """
    Generate summary statistics for search results.

    Args:
        results: List of search results

    Returns:
        Summary dictionary
    """
    summary = {
        'total_results': len(results),
        'sources': {},
        'year_distribution': {},
        'avg_citations': 0,
        'total_citations': 0
    }

    citations = []

    for result in results:
        # Count by source
        source = result.get('source', 'Unknown')
        summary['sources'][source] = summary['sources'].get(source, 0) + 1

        # Count by year
        year = result.get('year', 'Unknown')
        # JSON objects/lists are invalid years but must remain reportable.
        if isinstance(year, (dict, list)):
            year = json.dumps(year, sort_keys=True, ensure_ascii=False)
        summary['year_distribution'][year] = summary['year_distribution'].get(year, 0) + 1

        # Collect citations
        if result.get('citations') is not None:
            try:
                value = int(result['citations'])
                if value >= 0:
                    citations.append(value)
            except (ValueError, TypeError):
                pass

    if citations:
        summary['avg_citations'] = sum(citations) / len(citations)
        summary['total_citations'] = sum(citations)

    return summary


def validate_output(path: Path) -> None:
    """Reject existing destinations and linked/reparse paths; never create parents."""
    path = path.absolute()
    for part in (path, *path.parents):
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if (stat.S_ISLNK(info.st_mode) or
                getattr(info, 'st_file_attributes', 0) & 0x400):
            raise ValueError(f'linked/reparse output path is not allowed: {part}')
    if path.exists():
        raise FileExistsError(f'output already exists; choose a new approved path: {path}')


def write_new_output(path: Path, content: str) -> None:
    validate_output(path)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(content)


def main():
    """Process a JSON array; refuse raw provider envelopes and unknown options."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('results_file', type=Path)
    parser.add_argument('--format', choices=['json', 'markdown', 'bibtex'], default='markdown')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--rank', choices=['citations', 'year', 'relevance'])
    parser.add_argument('--year-start', type=int)
    parser.add_argument('--year-end', type=int)
    parser.add_argument('--deduplicate', action='store_true')
    parser.add_argument('--summary', action='store_true')
    args = parser.parse_args()
    if args.year_start is not None and args.year_end is not None and args.year_start > args.year_end:
        parser.error('--year-start must not exceed --year-end')
    try:
        results = json.loads(args.results_file.read_text(encoding='utf-8'))
        if not isinstance(results, list) or any(not isinstance(r, dict) for r in results):
            raise ValueError('input must be a normalized JSON array of record objects, not a provider response')
        if args.output:
            validate_output(args.output)
        if args.deduplicate:
            results = deduplicate_results(results)
        results = filter_by_year(results, args.year_start, args.year_end)
        if args.rank:
            results = rank_results(results, args.rank)
        if args.summary:
            summary = generate_search_summary(results)
            summary['pending_years'] = [r.get('triage_source_index', i) for i, r in enumerate(results)
                                        if r.get('triage_year_state', '').startswith('pending')]
            summary['duplicate_groups'] = [
                {'representative_index': r['triage_source_index'],
                 'duplicate_indices': r.get('triage_duplicate_indices', []),
                 'review_state': 'pending'}
                for r in results if r.get('triage_duplicate_records')]
            summary['scope'] = 'record processing only; no eligibility, quality or study-identity decision'
            print(json.dumps(summary, indent=2), file=sys.stderr)
        output = format_search_results(results, args.format)
        if args.output:
            write_new_output(args.output, output)
            print(f'[OK] Results saved to: {args.output}', file=sys.stderr)
        else:
            print(output)
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, f'[FAIL] {exc}\n')


if __name__ == '__main__':
    main()
