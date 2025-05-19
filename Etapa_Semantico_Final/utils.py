import pandas as pd

def load_lr_table(path):
    return pd.read_csv(path, index_col=0).fillna('')

def load_grammar(path):
    rules = []
    with open(path, 'r') as f:
        lines = f.readlines()[1:]  # Skip first line (count)
        for line in lines:
            parts = line.strip().split('\t')
            if len(parts) == 3:
                idx, size, head = parts
                rules.append((int(size), head))
    return rules
