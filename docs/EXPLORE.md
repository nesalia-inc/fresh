# Explore Command

`fresh learn explore` discovers concepts for a topic.

## Usage

```bash
fresh learn explore probability
# Returns: [fundamentals, distributions, conditional, random-variables]
```

## How It Works

### For Technical Topics (synced docs)
Analyzes the synced documentation structure.

### For Theoretical Topics
Uses web search to find related concepts.

## Output

```
fundamentals
distributions
conditional
random-variables
```

Then add them to the queue:

```bash
fresh learn add probability-theory fundamentals --priority high
fresh learn add probability-theory distributions --priority medium
```
