"""Read-only verification independent of the patcher's reconstruction code."""
import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path
from disc import Disc

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def file_hash(disc, item):
    disc.f.seek(item['offset'])
    left = item['size']
    result = hashlib.sha256()
    while left:
        chunk = disc.f.read(min(left, 4 * 1024 * 1024))
        if not chunk:
            raise EOFError(item['path'])
        result.update(chunk)
        left -= len(chunk)
    return result.hexdigest()


def main():
    parser = argparse.ArgumentParser(description='Read-only v0.81 ISO verification')
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--reference', type=Path)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads((ROOT/'patcher/release-config.json').read_text(encoding='utf-8'))
    assert args.source.stat().st_size == config['source']['size']
    assert digest(args.source) == config['source']['sha256']
    assert args.target.stat().st_size == config['target']['size']
    target_hash = digest(args.target)
    assert target_hash == config['target']['sha256']
    with zipfile.ZipFile(ROOT/'patches'/config['bundle']) as bundle:
        manifest = json.loads(bundle.read('manifest.json'))
    discs = [Disc(args.source), Disc(args.target)]
    if args.reference:
        discs.append(Disc(args.reference))
    try:
        tables = [{e['path']:e for e in d.entries if not e['directory']} for d in discs]
        expected = {e['path']:e for e in manifest['files']}
        assert all(set(t) == set(expected) for t in tables)
        changed = 0
        for path, record in expected.items():
            old_hash, new_hash = [file_hash(d, t[path]) for d,t in zip(discs[:2], tables[:2])]
            assert tables[1][path]['size'] == record['size'], path
            assert tables[0][path]['size'] == record['source_size'], path
            if record.get('delta'):
                assert old_hash == record['source_sha256'] and new_hash == record['sha256'], path
                changed += 1
            else:
                assert old_hash == new_hash, path
            if args.reference:
                assert tables[2][path]['size'] == record['size'], path
                assert file_hash(discs[2], tables[2][path]) == new_hash, path
        original = discs[0].read(tables[0]['default.xbe']['offset'], tables[0]['default.xbe']['size'])
        patched = discs[1].read(tables[1]['default.xbe']['offset'], tables[1]['default.xbe']['size'])
        assert original == patched
        assert hashlib.sha256(patched).hexdigest() == config['xbe_sha256']
        media = struct.unpack_from('<I', patched, 0x220)[0]
        assert media == 0x202 and changed == 99
        result = dict(version=config['version'],files=len(expected),changed_files=changed,
                      unchanged_files=len(expected)-changed,target_sha256=target_hash,
                      all_file_paths_sizes_and_hashes_verified=True,
                      all_file_hashes_match_reference=bool(args.reference),
                      xbe_byte_identical_to_original=True,xbe_sha256=config['xbe_sha256'],
                      xbe_media_field=hex(media),hdd_media_patch_applied=False,
                      source_opened_read_only=True,target_opened_read_only=True)
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result,indent=2))
    finally:
        for disc in discs:
            disc.f.close()


if __name__ == '__main__':
    main()
