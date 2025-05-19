def print_stack(stack, tokens, action, rule=None):
    stack_str = ' '.join(str(s) for s in stack)
    token_str = ' '.join(tok[1] for tok in tokens)
    if action.startswith('s'):
        action_str = f"Shift to {action[1:]}"
    elif action.startswith('r'):
        action_str = f"Reduce by rule {action[1:]}"
    elif action == 'acc':
        action_str = 'Accept'
    else:
        action_str = action
    print(f"PILA: [{stack_str}] | Entrada: [{token_str}] | Acción: {action_str} {f'-> {rule}' if rule else ''}")
