import sys
from collections import deque


class Lexer:
    # def __init__(self, string):
    # 	self.string = string

    NUM, ID, LPAR, RPAR, PLUS, MINUS, EQUAL, DIVIDE, MULT, SEMICOLON, EOF = range(11)

    SYMBOLS = {'=': EQUAL, ';': SEMICOLON, '(': LPAR, ')': RPAR, '+': PLUS, '-': MINUS, '/': DIVIDE, '*': MULT}

    # текущий символ, считанный из исходника
    ch = ' '  # допустим, первый символ - это пробел

    def error(self, msg):
        print('Lexer error: ', msg)
        sys.exit(1)

    def getc(self):
        # self.ch = self.string[0]
        self.ch = sys.stdin.read(1)

    def next_tok(self):
        self.value = None
        self.sym = None
        while self.sym == None:
            if len(self.ch) == 0:
                self.sym = Lexer.EOF
            elif self.ch.isspace():
                self.getc()
            elif self.ch in Lexer.SYMBOLS:
                self.sym = Lexer.SYMBOLS[self.ch]
                self.getc()
            elif self.ch.isdigit():
                intval = 0
                while self.ch.isdigit():
                    intval = intval * 10 + int(self.ch)
                    self.getc()
                self.value = intval
                self.sym = Lexer.NUM
            elif self.ch.isalpha():
                ident = ''
                while self.ch.isalpha():
                    ident = ident + self.ch.lower()
                    self.getc()
                if len(ident) == 1:
                    self.sym = Lexer.ID
                    self.value = ord(ident) - ord('a')
                else:
                    self.error('Unknown identifier: ' + ident)
            else:
                self.error('Unexpected symbol: ' + self.ch)


class Node:
    def __init__(self, kind, value=None, left=None, right=None, parent=None):
        self.kind = kind
        self.value = value
        self.left = left
        self.right = right
        self.parent = parent

    def print_tree(self):
        if self.left:
            self.left.PrintTree()
        print(self.kind),
        if self.right:
            self.right.PrintTree()

    def __str__(self):
        lines = _build_tree_string(self, 0, False, '-')[0]
        return '\n' + '\n'.join((line.rstrip() for line in lines))


def _build_tree_string(root, curr_index, index=False, delimiter='-'):

    if root is None:
        return [], 0, 0, 0
    dict_lex = {
        0: 'VAR',
        1: 'CONST',
        2: 'ADD',
        3: 'SUB',
        4: 'MULTIPLY',
        5: 'DIVIDE',
        6: 'SET',
        7: 'EMPTY',
        8: 'EXPR',
        9: 'PROG'
    }
    line1 = []
    line2 = []
    if root.kind == 0 or root.kind == 1:
        value = root.value
    else:
        value = dict_lex[root.kind]
    if index:
        node_repr = '{}{}{}'.format(curr_index, delimiter, value)
    else:
        node_repr = str(value)

    new_root_width = gap_size = len(node_repr)

    # Get the left and right sub-boxes, their widths, and root repr positions
    l_box, l_box_width, l_root_start, l_root_end = \
        _build_tree_string(root.left, 2 * curr_index + 1, index, delimiter)
    r_box, r_box_width, r_root_start, r_root_end = \
        _build_tree_string(root.right, 2 * curr_index + 2, index, delimiter)

    # Draw the branch connecting the current root node to the left sub-box
    # Pad the line with whitespaces where necessary
    if l_box_width > 0:
        l_root = (l_root_start + l_root_end) // 2 + 1
        line1.append(' ' * (l_root + 1))
        line1.append('_' * (l_box_width - l_root))
        line2.append(' ' * l_root + '/')
        line2.append(' ' * (l_box_width - l_root))
        new_root_start = l_box_width + 1
        gap_size += 1
    else:
        new_root_start = 0

    # Draw the representation of the current root node
    line1.append(node_repr)
    line2.append(' ' * new_root_width)

    # Draw the branch connecting the current root node to the right sub-box
    # Pad the line with whitespaces where necessary
    if r_box_width > 0:
        r_root = (r_root_start + r_root_end) // 2
        line1.append('_' * r_root)
        line1.append(' ' * (r_box_width - r_root + 1))
        line2.append(' ' * r_root + '\\')
        line2.append(' ' * (r_box_width - r_root))
        gap_size += 1
    new_root_end = new_root_start + new_root_width - 1

    # Combine the left and right sub-boxes with the branches drawn above
    gap = ' ' * gap_size
    new_box = [''.join(line1), ''.join(line2)]
    for i in range(max(len(l_box), len(r_box))):
        l_line = l_box[i] if i < len(l_box) else ' ' * l_box_width
        r_line = r_box[i] if i < len(r_box) else ' ' * r_box_width
        new_box.append(l_line + gap + r_line)

    # Return the new box, its width and its root repr positions
    return new_box, len(new_box[0]), new_root_start, new_root_end


def set_parent(root, par=None):
    if root:
        root.parent = par
        set_parent(root.left, root)
        set_parent(root.right, root)


def in_order(node):
    if node is None:
        return
    in_order(node.left)
    in_order(node.right)
    if node.kind == 1:
        if node.parent.right.kind == 1 and node.parent.left.kind == 1:
            path.append(node.parent)
            new_node = Node(Parser.CONST, perform(node.parent), parent=node.parent.parent)
            node.parent.parent.right = new_node


class Parser:
    VAR, CONST, ADD, SUB, MULTIPLY, DIVIDE, SET, EMPTY, EXPR, PROG = range(10)

    def __init__(self, lexer):
        self.lexer = lexer

    @staticmethod
    def error(msg):
        print('Parser error:', msg)
        sys.exit(1)

    def term(self):
        if self.lexer.sym == Lexer.ID:
            n = Node(Parser.VAR, self.lexer.value)
            self.lexer.next_tok()
            return n
        elif self.lexer.sym == Lexer.NUM:
            n = Node(Parser.CONST, self.lexer.value)
            self.lexer.next_tok()
            return n
        else:
            return self.paren_expr()

    def negative(self):
        n = self.term()
        while self.lexer.sym == Lexer.MINUS:
            if self.lexer.sym == Lexer.MINUS:
                kind = Parser.SUB
            self.lexer.next_tok()
            n = Node(kind, left=n, right=self.paren_expr())
        return n

    def multiplication(self):
        n = self.term()
        while self.lexer.sym == Lexer.MULT or self.lexer.sym == Lexer.DIVIDE:
            if self.lexer.sym == Lexer.MULT:
                kind = Parser.MULTIPLY
            else:
                kind = Parser.DIVIDE
            self.lexer.next_tok()
            n = Node(kind, left=n, right=self.term())
        return n

    def addition(self):
        n = self.multiplication()
        while self.lexer.sym == Lexer.PLUS or self.lexer.sym == Lexer.MINUS:
            if self.lexer.sym == Lexer.PLUS:
                kind = Parser.ADD
            else:
                kind = Parser.SUB
            self.lexer.next_tok()
            n = Node(kind, left=n, right=self.multiplication())  # changed right self.term()
        return n

    def expr(self):
        if self.lexer.sym != Lexer.ID:
            return self.addition()
        n = self.addition()
        if n.kind == Parser.VAR and self.lexer.sym == Lexer.EQUAL:
            self.lexer.next_tok()
            n = Node(Parser.SET, left=n, right=self.expr())
        return n

    def paren_expr(self):
        if self.lexer.sym != Lexer.LPAR:
            self.error('"(" expected')
        self.lexer.next_tok()
        n = self.expr()
        if self.lexer.sym != Lexer.RPAR:
            self.error('")" expected')
        self.lexer.next_tok()
        return n

    def statement(self):
        if self.lexer.sym == Lexer.SEMICOLON:
            n = Node(Parser.EMPTY)
            self.lexer.next_tok()
        else:
            n = Node(Parser.EXPR, left=self.expr())
            if self.lexer.sym != Lexer.SEMICOLON:
                self.error('";" expected')
            self.lexer.next_tok()
        return n

    def parse(self):
        self.lexer.next_tok()
        node = Node(Parser.PROG, left=self.statement())
        if self.lexer.sym != Lexer.EOF:
            self.error("Invalid statement syntax")
        return node


def print_tree(root):
    buf = deque()
    output = []
    if not root:
        print('$')
    else:
        buf.append(root)
        count, next_count = 1, 0
        while count:
            node = buf.popleft()
            if node:
                output.append(node.kind)
                count -= 1
                for n in (node.left, node.right):
                    if n:
                        buf.append(n)
                        next_count += 1
                    else:
                        buf.append(None)
            else:
                output.append('$')
            if not count:
                print(output)
                output = []
                count, next_count = next_count, 0
        # print the remaining all empty leaf node part
        output.extend(['$'] * len(buf))
        print(output)


def perform(node):
    if node.kind == Parser.ADD:
        return node.left.value + node.right.value
    elif node.kind == Parser.SUB:
        return node.left.value - node.right.value
    elif node.kind == Parser.MULTIPLY:
        return node.left.value * node.right.value
    elif node.kind == Parser.DIVIDE:
        return node.left.value / node.right.value


path = []
lex = Lexer()
p = Parser(lex)
ast = p.parse()
# print_tree(ast)
print(ast)
set_parent(ast)
in_order(ast)
print(*path, sep=' ')
print(ast)


# 3 + 4 * (2 + 1) - 2 + 6 * 4
