#!/usr/bin/env python3
import tempfile, glob, os, sqlite3, regex, sys

def main():
    t = tempfile.gettempdir()
    dirs = sorted(glob.glob(os.path.join(t, 'JWLManager_*')), key=os.path.getmtime, reverse=True)
    if not dirs:
        print('No JWLManager_* temp directories found in', t)
        return 2
    latest = dirs[0]
    print('Using temp dir:', latest)
    db = os.path.join(latest, 'userData.db')
    if not os.path.exists(db):
        print('No userData.db in', latest)
        return 3
    con = sqlite3.connect(db)
    cur = con.cursor()
    sql = """
        SELECT NoteId, Title, Content, LocationId
        FROM Note
        WHERE (Title IS NOT NULL AND Title != '')
           OR (Content IS NOT NULL AND Content != '')
    """
    cur.execute(sql)
    rows = cur.fetchall()
    def normalize(s):
        if s is None:
            return ''
        s = str(s)
        return s
    groups = {}
    for note_id, title, content, location_id in rows:
        key = (normalize(title), normalize(content), location_id)
        groups.setdefault(key, []).append((note_id, title or '', content or '', location_id))
    dup_groups = {k: v for k, v in groups.items() if len(v) > 1}
    total_groups = len(dup_groups)
    total_duplicates = sum(len(v)-1 for v in dup_groups.values())
    print(f'Found {total_groups} duplicate groups with {total_duplicates} duplicates')
    printed = 0
    for idx, (k, entries) in enumerate(dup_groups.items(), 1):
        if printed >= 10:
            break
        title = entries[0][1][:80]
        loc = entries[0][3]
        print(f"Group {idx}: Title='{title}' Location={loc} Count={len(entries)}")
        for e in entries:
            nid, t, c, l = e
            snippet = (c or '')[:160].replace('\n',' ')
            print('  -', nid, snippet)
        printed += 1
    con.close()
    return 0

if __name__ == '__main__':
    sys.exit(main())
