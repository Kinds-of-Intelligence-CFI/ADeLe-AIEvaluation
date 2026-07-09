"""Run one MMs annotation prompt through litellm and parse CSV output."""

from __future__ import annotations

import argparse
import csv
import os
import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
RIVERCROSS = HERE.parent
DEFAULT_OUT_DIR = HERE / 'labels'
LOCAL_ANTHROPIC_KEY_FILE = HERE / 'local_anthropic_key.txt'
LOCAL_OPENAI_KEY_FILE = HERE / 'local_openai_key.txt'
REQUIRED_COLUMNS = ['custom_id', 'level', 'reason']

def provider_env_hint(model: str) -> str | None:
    lower = model.lower()
    if lower.startswith(('gpt-', 'o1', 'o3', 'o4', 'o5', 'openai/')):
        return 'OPENAI_API_KEY'
    if lower.startswith(('claude', 'anthropic/')):
        return 'ANTHROPIC_API_KEY'
    if lower.startswith(('gemini/', 'google/')):
        return 'GOOGLE_API_KEY or GEMINI_API_KEY'
    return None


def load_local_key(env_name: str) -> None:
    local_files = {
        'ANTHROPIC_API_KEY': (LOCAL_ANTHROPIC_KEY_FILE, 'PASTE_ANTHROPIC_API_KEY_HERE'),
        'OPENAI_API_KEY': (LOCAL_OPENAI_KEY_FILE, 'PASTE_OPENAI_API_KEY_HERE'),
    }
    if os.getenv(env_name) or env_name not in local_files:
        return
    path, placeholder = local_files[env_name]
    if not path.exists():
        return
    key = path.read_text(encoding='utf-8').strip()
    if key and key != placeholder:
        os.environ[env_name] = key

def extract_csv_text(response: str) -> str:
    fence = chr(96) * 3
    start = response.find(fence)
    if start < 0:
        return response.strip()
    start = response.find('\n', start) + 1
    end = response.find(fence, start)
    return response[start:end].strip() if end >= 0 else response[start:].strip()

def parse_csv_response(response: str) -> pd.DataFrame:
    csv_text = extract_csv_text(response)
    rows = list(csv.DictReader(csv_text.splitlines()))
    if not rows:
        raise ValueError('response did not contain parseable CSV rows')
    df = pd.DataFrame(rows)
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f'parsed CSV missing columns: {missing}')
    df = df[REQUIRED_COLUMNS].copy()
    df['level'] = pd.to_numeric(df['level'], errors='coerce')
    bad = df['level'].isna() | (df['level'] < 0) | (df['level'] > 5)
    if bad.any():
        raise ValueError(f'parsed CSV has {int(bad.sum())} invalid levels')
    return df

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--prompt', type=Path, required=True)
    ap.add_argument('--model', required=True)
    ap.add_argument('--out-dir', type=Path, default=DEFAULT_OUT_DIR)
    ap.add_argument('--name', default=None)
    ap.add_argument('--max-tokens', type=int, default=4096)
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    prompt = args.prompt.read_text(encoding='utf-8')
    approx_tokens = max(1, len(prompt) // 4)
    hint = provider_env_hint(args.model)
    print(f'prompt: {args.prompt}')
    print(f'model: {args.model}')
    print(f'approx_input_tokens: {approx_tokens}')
    if hint:
        keys = [part.strip() for part in hint.split(' or ')]
        for key in keys:
            load_local_key(key)
        status = 'set' if any(os.getenv(k) for k in keys) else 'missing'
        print(f'credential_hint: {hint}')
        print(f'credential_status: {status}')
    if args.dry_run:
        return
    if hint:
        keys = [part.strip() for part in hint.split(' or ')]
        for key in keys:
            load_local_key(key)
        if not any(os.getenv(k) for k in keys):
            raise SystemExit(f'missing API credential: set {hint}')

    import litellm
    response = litellm.completion(model=args.model, messages=[{'role': 'user', 'content': prompt}], max_tokens=args.max_tokens)
    content = response['choices'][0]['message']['content']
    safe_model = re.sub('[^A-Za-z0-9_.-]+', '_', args.model)
    stem = args.name or f'{args.prompt.stem}_{safe_model}'
    args.out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = args.out_dir / f'{stem}.raw.txt'
    csv_path = args.out_dir / f'{stem}.csv'
    raw_path.write_text(content, encoding='utf-8')
    df = parse_csv_response(content)
    df.to_csv(csv_path, index=False)
    def display(path: Path) -> Path:
        resolved = path.resolve()
        try:
            return resolved.relative_to(RIVERCROSS)
        except ValueError:
            return resolved

    print(f'wrote raw response: {display(raw_path)}')
    print(f'wrote parsed labels: {display(csv_path)} ({len(df)} rows)')

if __name__ == '__main__':
    main()
