"""Restore losslessly compressed public result files, validating SHA-256."""
from pathlib import Path
import gzip,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
manifest=ROOT/'results/compressed_manifest.json'
if manifest.exists():
 for item in json.loads(manifest.read_text()):
  dest=ROOT/item['path']
  if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest()==item['sha256']:continue
  data=gzip.decompress(b''.join((ROOT/p).read_bytes() for p in item['parts']))
  if hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('Checksum mismatch: '+item['path'])
  dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
 print('All compressed result files restored and verified.')
else:
 print('No compressed manifest; research archive already contains uncompressed files.')
