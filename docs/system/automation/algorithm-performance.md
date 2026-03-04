# Algorithm & Performance Automation

Automating algorithmic decisions and performance optimization.

## The Problem

We reinvent too much:
- Sorting: quicksort, mergesort, heapsort (researched optimal)
- Searching: BFS, DFS, A*, Dijkstra (proven optimal)
- Data structures: Hash tables, Trees, Graphs (known complexity)

Yet agents reinvent these instead of using known solutions.

## Algorithm Selection

```
INPUT: "I need to find if a user exists"

SYSTEM ANALYZES:
1. Operation type: SEARCH
2. Data size: Unknown (< 10M)
3. Frequency: Frequent
4. Consistency: Strong required
5. Query pattern: Exact match

OUTPUT:
RECOMMENDED: Hash table / HashMap
Time complexity: O(1) average, O(n) worst
Space complexity: O(n)

Implementation:
const userExists = new Set(users).has(userId);
```

## Performance Rules (Automatable)

### N+1 Query Detection

```
DETECT:
for (const user of users) {
  const posts = await db.posts.find({ user: user.id });
}

SUGGEST:
const posts = await db.posts.find({
  user: { $in: users.map(u => u.id) }
});
```

### Missing Index Detection

```
DETECT:
WHERE email = 'user@example.com' (no index)

SUGGEST:
CREATE INDEX idx_users_email ON users(email);
```

### Missing Cache

```
DETECT:
function getConfig() {
  return fetch('/api/config').then(r => r.json());
}
// Called on every request

SUGGEST:
const getConfig = memoize(() =>
  fetch('/api/config').then(r => r.json())
);
```

## Complexity Analysis

### Detect O(n²)

```
DETECT:
for (const a of items) {
  for (const b of items) {
    if (a.id === b.id) ...
  }
}

SUGGEST:
const itemsById = new Map(items.map(i => [i.id, i]));
// Lookup is O(1)
```

### Detect Unnecessary Iterations

```
DETECT:
const allExist = items.every(item =>
  otherItems.find(o => o.id === item.id)
);
// O(n × m)

SUGGEST:
const otherIds = new Set(otherItems.map(i => i.id));
const allExist = items.every(item => otherIds.has(item.id));
// O(n + m)
```

## Integration Points

```
1. CLI (pre-commit):
   fresh-analyze --performance

2. Language Server:
   Inline warnings + quick fixes

3. Compiler/Transformer:
   AST-based analysis + auto-fix

4. CI/CD:
   Block merge if critical issues
```

---

*Last updated: 2026-03-04*
