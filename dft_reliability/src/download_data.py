"""Retrieve immutable upstream data; verify Git blob identity before use."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
COMMIT = '322a41229f7707a58626a7c03ce850d67920fad0'
FILES = {
    'ani_1x_tz_configs.xyz': '9e7139d1f1982d518c8d11fa4562b1d0cdc9cc9d',
    'transition1x_configs.xyz': '40e0cce4f7aaa07e8eea23a29226bba61df7ba28',
    'aimnet2_configs.xyz': 'd0fd4a3b826f47b61040ccbac9ec5d8ff6fa9d5e',
    'spice_configs.xyz': '80bd6fb1bb0b12fdfb9dc7a9d5b493442e2d521e',
}

def download(item):
    name, expected = item
    url = f'https://raw.githubusercontent.com/water-ice-group/datasets_dft_accuracy/{COMMIT}/force_discrepancies/{name}'
    path = ROOT / 'data' / name
    data = path.read_bytes() if path.exists() else urllib.request.urlopen(url, timeout=60).read()
    actual = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if actual != expected:
        raise ValueError(f'Blob mismatch: {name}')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    print(name, len(data), actual, flush=True)
    return dict(file=name, source_url=url, upstream_commit=COMMIT, git_blob=actual,
                sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))

if __name__ == '__main__':
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        manifest = list(pool.map(download, FILES.items()))
    (ROOT / 'data' / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
