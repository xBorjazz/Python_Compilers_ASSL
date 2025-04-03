class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None

    def error(self, msg=None):
        token_info = (
            f"Línea {self.current_token.line}, Columna {self.current_token.column}"
            if self.current_token else "Fin de secuencia"
        )
        raise Exception(
            f"Error sintáctico: {msg if msg else ''} cerca de "
            f"{token_info}, Token: {self.current_token}"
        )

    def eat(self, token_type):
        """Verifica que el token actual sea del tipo esperado y avanza."""
        if self.current_token and self.current_token.type == token_type:
            self.pos += 1
            self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None
        else:
            self.error(f"Se esperaba '{token_type}'")

    def parse(self):
        """
        Método principal que inicia el parseo.
        Retorna un valor (ej. un árbol sintáctico) o simplemente consume los tokens.
        """
        self.program()
        if self.current_token is not None:
            self.error("Tokens extra al final del programa")

    # --------------------------------------------------------
    # Reglas de la gramática
    # --------------------------------------------------------
    def program(self):
        # PROGRAM -> STATEMENT_LIST
        self.statement_list()

    def statement_list(self):
        # STATEMENT_LIST -> STATEMENT STATEMENT_LIST | ε
        while self.current_token and self.current_token.type in (
            'IF', 'WHILE', 'PRINT', 'INT', 'FLOAT', 'IDENT'
        ):
            self.statement()

    def statement(self):
        # STATEMENT -> DECLARATION | ASSIGNMENT | IF_STATEMENT | WHILE_STATEMENT | PRINT_STATEMENT
        if self.current_token.type in ('INT', 'FLOAT'):
            self.declaration()
        elif self.current_token.type == 'IDENT':
            self.assignment()
        elif self.current_token.type == 'IF':
            self.if_statement()
        elif self.current_token.type == 'WHILE':
            self.while_statement()
        elif self.current_token.type == 'PRINT':
            self.print_statement()
        else:
            self.error("Declaración, asignación, if, while o print esperados")

    def declaration(self):
        # DECLARATION -> (int|float) IDENTIFIER ( '=' EXPRESSION )? ';'
        if self.current_token.type in ('INT', 'FLOAT'):
            self.eat(self.current_token.type)  # comemos INT o FLOAT
        else:
            self.error("Tipo de dato esperado (int/float)")

        self.eat('IDENT')  # nombre de variable

        if self.current_token and self.current_token.type == 'ASSIGN':
            self.eat('ASSIGN')
            self.expression()

        self.eat('SEMI')

    def assignment(self):
        # ASSIGNMENT -> IDENTIFIER '=' EXPRESSION ';'
        self.eat('IDENT')
        self.eat('ASSIGN')
        self.expression()
        self.eat('SEMI')

    def if_statement(self):
        # IF_STATEMENT -> 'if' '(' EXPRESSION ')' '{' STATEMENT_LIST '}' ( 'else' '{' STATEMENT_LIST '}' )?
        self.eat('IF')
        self.eat('LPAREN')
        self.expression()
        self.eat('RPAREN')
        self.eat('LBRACE')
        self.statement_list()
        self.eat('RBRACE')

        if self.current_token and self.current_token.type == 'ELSE':
            self.eat('ELSE')
            self.eat('LBRACE')
            self.statement_list()
            self.eat('RBRACE')

    def while_statement(self):
        # WHILE_STATEMENT -> 'while' '(' EXPRESSION ')' '{' STATEMENT_LIST '}'
        self.eat('WHILE')
        self.eat('LPAREN')
        self.expression()
        self.eat('RPAREN')
        self.eat('LBRACE')
        self.statement_list()
        self.eat('RBRACE')

    def print_statement(self):
        # PRINT_STATEMENT -> 'print' '(' (IDENTIFIER | NUMBER) ')' ';'
        self.eat('PRINT')
        self.eat('LPAREN')

        if self.current_token.type == 'IDENT':
            self.eat('IDENT')
        elif self.current_token.type in ('INT_LIT', 'FLOAT_LIT'):
            self.eat(self.current_token.type)
        else:
            self.error("Se esperaba un identificador o número en print")

        self.eat('RPAREN')
        self.eat('SEMI')

    # --------------------------------------------------------
    # Nuevas reglas para EXPRESIONES con operadores relacionales
    # --------------------------------------------------------
    def expression(self):
        """
        EXPRESSION -> RELATIONAL_EXPR
        (en otras gramáticas, podrías mezclar relacional con aritmético,
         pero aquí lo separamos para mayor claridad).
        """
        self.relational_expr()

    def relational_expr(self):
        """
        RELATIONAL_EXPR -> add_expr ( ( < | > | <= | >= | == | != ) add_expr )*
        """
        self.add_expr()
        while self.current_token and self.current_token.type in (
            'OP_LT', 'OP_GT', 'OP_LEQ', 'OP_GEQ', 'OP_EQ', 'OP_NEQ'
        ):
            op_type = self.current_token.type
            self.eat(op_type)
            self.add_expr()

    def add_expr(self):
        """
        ADD_EXPR -> TERM ( ( + | - ) TERM )*
        """
        self.term()
        while self.current_token and self.current_token.type in ('PLUS', 'MINUS'):
            op_type = self.current_token.type
            self.eat(op_type)
            self.term()

    def term(self):
        """
        TERM -> FACTOR ( ( * | / ) FACTOR )*
        """
        self.factor()
        while self.current_token and self.current_token.type in ('MULT', 'DIV'):
            op_type = self.current_token.type
            self.eat(op_type)
            self.factor()

    def factor(self):
        """
        FACTOR -> NUMBER | IDENTIFIER | ( '(' EXPRESSION ')' )
        """
        if self.current_token.type in ('INT_LIT', 'FLOAT_LIT'):
            self.eat(self.current_token.type)
        elif self.current_token.type == 'IDENT':
            self.eat('IDENT')
        elif self.current_token.type == 'LPAREN':
            self.eat('LPAREN')
            self.expression()
            self.eat('RPAREN')
        else:
            self.error("Factor no válido (se esperaba número, identificador o expresión entre paréntesis)")
