#!/usr/bin/env python3
"""Helper for bump-version.sh JSON updates"""
import json
import re
import sys

def main():
    if len(sys.argv) < 3:
        print("Usage: bump-version-helper.py <file> <mode> [version] [cmds] [agents] [skills]")
        sys.exit(2)

    file_path = sys.argv[1]
    mode = sys.argv[2]  # "version" or "counts"
    version = sys.argv[3] if len(sys.argv) > 3 else ""
    cmds = sys.argv[4] if len(sys.argv) > 4 else ""
    agents = sys.argv[5] if len(sys.argv) > 5 else ""
    skills = sys.argv[6] if len(sys.argv) > 6 else ""

    with open(file_path, 'r') as f:
        data = json.load(f)

    changed = False

    # Version updates (only in "version" mode)
    if mode == "version":
        if 'version' in data and data['version'] != version:
            data['version'] = version
            changed = True
        if 'metadata' in data and 'version' in data['metadata'] and data['metadata']['version'] != version:
            data['metadata']['version'] = version
            changed = True
        if 'plugins' in data and data['plugins'] and 'version' in data['plugins'][0] and data['plugins'][0]['version'] != version:
            data['plugins'][0]['version'] = version
            changed = True

    # Count updates (both modes)
    def fix_counts(desc):
        if not desc:
            return desc, False
        orig = desc
        desc = re.sub(r'\d+ commands', cmds + ' commands', desc)
        desc = re.sub(r'\d+ agents', agents + ' agents', desc)
        desc = re.sub(r'\d+ skills', skills + ' skills', desc)
        return desc, desc != orig

    for key_path in [('description',), ('metadata', 'description'), ('plugins', 0, 'description')]:
        obj = data
        try:
            for k in key_path[:-1]:
                obj = obj[k]
            last = key_path[-1]
            if last in obj and obj[last]:
                obj[last], c = fix_counts(obj[last])
                changed = changed or c
        except (KeyError, IndexError, TypeError):
            pass

    if changed:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
            f.write('\n')
        print('updated')
    else:
        print('unchanged')

if __name__ == '__main__':
    main()
