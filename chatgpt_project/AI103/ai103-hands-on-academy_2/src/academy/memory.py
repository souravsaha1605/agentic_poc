# Purpose: Store local conversation state with expiry
# Learn: Inspect SQLite user/session keys and character windows; this local example assumes one application tenant.
# Run: Imported by lesson code; do not run this file directly. Follow the importing lesson in MASTER_GUIDE.md.

import json
import sqlite3
import time
class Memory:
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.execute('CREATE TABLE IF NOT EXISTS memory (user TEXT,session TEXT,value TEXT,expires REAL,PRIMARY KEY(user,session))')
    def put(self,user,session,messages,ttl=60):
        with self.db:self.db.execute('INSERT OR REPLACE INTO memory VALUES (?,?,?,?)',
                                    (user,session,json.dumps(messages),time.time()+ttl))
    def get(self,user,session):
        r=self.db.execute('SELECT value,expires FROM memory WHERE user=? AND session=?',(user,session)).fetchone()
        return json.loads(r[0]) if r and r[1]>time.time() else []
    def delete(self,user,session):
        with self.db:
            self.db.execute('DELETE FROM memory WHERE user=? AND session=?',(user,session))
    def close(self):
        self.db.close()
def window(messages,max_chars=800):
    # Character budget is a teaching approximation, not a tokenizer.
    """Keep the newest messages within a character budget; real token budgets need a tokenizer."""
    out=[]
    size=0
    for m in reversed(messages):
        cost=len(m['content'])
        if size+cost>max_chars:
            break
        out.insert(0,m)
        size+=cost
    return out
