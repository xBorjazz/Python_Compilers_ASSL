from stack_trace import print_stack

class LRParser:
    def __init__(self, table, rules):
        self.table = table
        self.rules = rules

    def parse(self, tokens):
        stack = [0]
        idx = 0

        while True:
            state = stack[-1]
            current_token = tokens[idx][0]
            action = self.table.loc[str(state), current_token]

            print_stack(stack, tokens[idx:], action)

            if not action:
                raise SyntaxError(f"Token inesperado: {tokens[idx]}")

            if action.startswith('s'):
                next_state = int(action[1:])
                stack.extend([current_token, next_state])
                idx += 1

            elif action.startswith('r'):
                rule_num = int(action[1:])
                size, head = self.rules[rule_num]
                for _ in range(size * 2):
                    stack.pop()
                state = stack[-1]
                goto = self.table.loc[str(state), head]
                if goto == '':
                    raise SyntaxError(f"No hay transición para {head} desde estado {state}")
                stack.extend([head, int(goto)])
                print_stack(stack, tokens[idx:], action, rule=f"{head} ← ...")

            elif action == 'acc':
                print("✅ Cadena aceptada")
                break
