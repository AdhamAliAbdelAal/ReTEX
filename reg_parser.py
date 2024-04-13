import json

class Validator:

    alphanumeric = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    dot = list('.')
    parentheses = list('()')
    brackets = list('[]')
    operators = list('|&*-?+')
    terminals = alphanumeric + dot + parentheses + brackets + operators

    S = '_S'
    A = '_A'
    B = '_B'
    E = '_E'
    R = '_R'
    G = '_G'
    T = '_T'
    C = '_C'

    rules = {
        S: [[S, '|', A], [A]],
        A: [[A, B], [B]],
        B: [[E, '*'], [E, '+'], [E, '?'], [E]],
        E: [['(', S, ')'], ['[', R, ']'], [T]],
        R: [[R, G], [G]],
        G: [[C, '-', C], [C]],
        T: [[C], ['.']],
        C: [[c] for c in alphanumeric]
    }

    rule2Index = {
        S: 0,
        A: 1,
        B: 2,
        E: 3,
        R: 4,
        G: 5,
        T: 6,
        C: 7
    }
    index2Rule = {v: k for k, v in rule2Index.items()}

    @staticmethod
    def is_terminal(c: str) -> bool:
        return c in Validator.terminals

    @staticmethod
    def all_terminals(rule: list[str]) -> bool:
        return all([Validator.is_terminal(c) for c in rule])

    def contains_terminals(rule: list[str]) -> bool:
        return any([Validator.is_terminal(c) for c in rule])

    @staticmethod
    def get_indices_inbound(c: str, l: int, r: int, symbolIndices: dict[str, list[int]]) -> list[int]:
        if c not in symbolIndices:
            return []
        return [i for i in symbolIndices[c] if l <= i <= r]

    @staticmethod
    def solve(left: int, right:int, idx: int, reg: str, symbolIndices: dict[str, list[int]], mem) -> bool:
        if mem[left][right][idx] != -1:
            return mem[left][right][idx]
        if left > right:
            mem[left][right][idx] = False
            return mem[left][right][idx]
        rule = Validator.index2Rule[idx]
        for r in Validator.rules[rule]:
            # case1 r contains terminals only
            # base case
            if Validator.all_terminals(r):
                if reg[left:right+1] == ''.join(r):
                    mem[left][right][idx]= True
                    return mem[left][right][idx]
            # case2 r contains terminals
            elif Validator.contains_terminals(r):
                # brackets
                if Validator.is_terminal(r[0]) and Validator.is_terminal(r[-1]):
                    terminal_indices_left = Validator.get_indices_inbound(r[0], left, right, symbolIndices)
                    terminal_indices_right = Validator.get_indices_inbound(r[-1], left, right, symbolIndices)
                    if len(terminal_indices_left) > 0 and len(terminal_indices_right)>0 and left == terminal_indices_left[0] and right == terminal_indices_right[-1] and Validator.solve(left+1, right-1, Validator.rule2Index[r[1]],reg,symbolIndices,mem):
                        mem[left][right][idx]= True
                        return mem[left][right][idx]
                else:
                    # r[1] is a terminal
                    terminal_indices = Validator.get_indices_inbound(r[1], left, right, symbolIndices)
                    for i in terminal_indices:
                        if Validator.solve(left, i-1, Validator.rule2Index[r[0]],reg,symbolIndices,mem):
                            if len(r) == 2:
                                if i == right:
                                    mem[left][right][idx]=True
                                    return mem[left][right][idx]
                            elif Validator.solve(i+1, right, Validator.rule2Index[r[2]],reg,symbolIndices,mem):
                                mem[left][right][idx]=True
                                return mem[left][right][idx]
            # case3 r contains non-terminals only
            else:
                # match all string
                if len(r) == 1:
                    if Validator.solve(left, right, Validator.rule2Index[r[0]],reg,symbolIndices,mem):
                        mem[left][right][idx] =True
                        return mem[left][right][idx]
                else:
                # match till right-1
                    for i in range(left, right):
                        if Validator.solve(left, i, Validator.rule2Index[r[0]],reg,symbolIndices,mem) and Validator.solve(i+1, right, Validator.rule2Index[r[1]],reg,symbolIndices,mem):
                            mem[left][right][idx]=True
                            return mem[left][right][idx]
        mem[left][right][idx]= False
        return False
    @staticmethod
    def fill_symbol_indices(reg: str) -> dict[str, list[int]]:
        symbolIndices = {}
        for i,c in enumerate(reg):
            if c not in symbolIndices:
                symbolIndices[c] = [i]
            else:
                symbolIndices[c].append(i)
        return symbolIndices
    
    @staticmethod
    def validate(reg: str) -> bool:
        symbolIndices = Validator.fill_symbol_indices(reg)
        mem = [[[-1 for _ in range(len(Validator.rules))] for _ in range(len(reg))] for _ in range(len(reg))]
        return Validator.solve(0, len(reg)-1, Validator.rule2Index[Validator.S], reg, symbolIndices, mem)


class Operator:
    @staticmethod
    def precedence(op):
        if op == '|':
            return 2
        elif op == '&':
            return 1
        elif op == '-':
            return 0
        elif op == '*':
            return 0
        elif op == '+':
            return 0
        elif op == '?':
            return 0
        else:
            # brackets
            return None


class State:
    count = 0

    def __init__(self, is_accepting: bool = False, transitions: list["Transition"] = []):
        self.is_terminating = is_accepting
        self.transitions: list[Transition] = []
        self.id = State.count
        State.count += 1

    def to_json(self):
        transitions_dict = {}
        for t in self.transitions:
            if t.input in transitions_dict:
                if type(transitions_dict[t.input]) == list:
                    transitions_dict[t.input].append(f'S{t.to.id}')
                else:
                    transitions_dict[t.input] = [
                        transitions_dict[t.input], f'S{t.to.id}']
            else:
                transitions_dict[t.input] = f'S{t.to.id}'

        return {
            f'S{self.id}': {
                "isTerminatingState": self.is_terminating,
                **transitions_dict
            }
        }


class Transition:
    def __init__(self, input: str, to: State):
        self.to = to
        self.input = input


unary_operators = ['*', '+', '?']
binary_operators = ['|', '&', '-']
opening_brackets = ['(']
closing_brackets = [')']


class Preprocessor:
    @staticmethod
    def preprocess(text):
        ret = ""
        sz = len(text)
        square_brackets = 0
        i = 0
        while i < sz-1:
            ret += text[i]
            square_brackets += (text[i] == '[')
            square_brackets -= (text[i] == ']')
            if square_brackets==0 and not (text[i] in binary_operators or text[i] in opening_brackets or text[i+1] in binary_operators or text[i+1] in closing_brackets or text[i+1] in unary_operators):
                ret += '&'
            i += 1
        ret += text[sz-1]
        return ret


class FA:
    def __init__(self) -> None:
        self.start = None
        self.end = None

    def add_operand_FA(self, operand: str, states: list[State]):
        self.start = State()
        self.end = State()
        states.append(self.start)
        states.append(self.end)
        if operand == '.':
            # for all digits and alphabets
            for i in range(26):
                if i < 10:
                    transition = Transition(chr(ord('0')+i), self.end)
                    self.start.transitions.append(transition)
                transition = Transition(chr(ord('a')+i), self.end)
                self.start.transitions.append(transition)
                transition = Transition(chr(ord('A')+i), self.end)
                self.start.transitions.append(transition)
        else:
            transition = Transition(operand, self.end)
            self.start.transitions.append(transition)

    def add_or_FA(self, operands: list["FA"], states: list[State]):
        self.start = State()
        self.end = State()
        states.append(self.start)
        states.append(self.end)
        self.start.transitions.append(Transition("eps", operands[0].start))
        self.start.transitions.append(Transition("eps", operands[1].start))
        operands[0].end.transitions.append(Transition("eps", self.end))
        operands[1].end.transitions.append(Transition("eps", self.end))

    def add_and_FA(self, operands: list["FA"], states: list[State]):
        self.start = operands[0].start
        self.end = operands[1].end
        operands[0].end.transitions.append(
            Transition("eps", operands[1].start))

    def add_square_bracket_FA(self, block: str, states: list[State]):
        self.start = State()
        self.end = State()
        states.append(self.start)
        states.append(self.end)
        transition = Transition(block, self.end)
        self.start.transitions.append(transition)

    def add_asterisk_FA(self, operand: "FA", states: list[State]):
        self.start = State()
        self.end = State()
        states.append(self.start)
        states.append(self.end)
        self.start.transitions.append(Transition("eps", self.end))
        self.start.transitions.append(Transition("eps", operand.start))
        operand.end.transitions.append(Transition("eps", self.end))
        operand.end.transitions.append(Transition("eps", self.start))

    def add_plus_FA(self, operand: "FA", states: list[State]):
        self.start = State()
        self.end = State()
        states.append(self.start)
        states.append(self.end)
        self.start.transitions.append(Transition("eps", operand.start))
        operand.end.transitions.append(Transition("eps", self.end))
        operand.end.transitions.append(Transition("eps", self.start))

    def add_question_mark_FA(self, operand: "FA", states: list[State]):
        self.start = State()
        self.end = State()
        states.append(self.start)
        states.append(self.end)
        self.start.transitions.append(Transition("eps", self.end))
        self.start.transitions.append(Transition("eps", operand.start))
        operand.end.transitions.append(Transition("eps", self.end))


class RegParser:
    def __init__(self, text):
        if not Validator.validate(text):
            raise Exception("Invalid Regular Expression")
        self.text = Preprocessor.preprocess(text)
        print(self.text)
        self.build()
        print(self.q)
        self.states: list[State] = []

    def build(self):
        q = []
        text = self.text
        st = []
        sz = len(text)
        i = 0
        while i<sz:
            # case 1: alphabet, digit, dot
            if text[i].isalpha() or text[i].isdigit() or text[i] == '.' or text[i] == '-':
                q.append(text[i])
            # case 2: operators
            elif Operator.precedence(text[i]) is not None:
                while len(st) > 0 and Operator.precedence(st[-1]) is not None and Operator.precedence(st[-1]) <= Operator.precedence(text[i]):
                    q.append(st.pop())
                st.append(text[i])
            # case 3: opening brackets
            elif text[i] in opening_brackets:
                st.append(text[i])
            # case 4: closing brackets
            elif text[i] in closing_brackets:
                opening = '('
                while len(st) > 0 and st[-1] != opening:
                    q.append(st.pop())
                if len(st) == 0:
                    raise Exception("Invalid Regular Expression")
                st.pop()
            elif text[i] == '[':
                while i<sz and text[i] != ']':
                    q.append(text[i])
                    i += 1
                q.append(text[i])
            i+=1
        while (len(st) > 0):
            if (st[-1] in opening_brackets):
                raise Exception("Invalid Regular Expression")
            else:
                q.append(st[-1])
            st.pop()
        self.q = q

    @staticmethod
    def is_operand(c):
        return c.isalpha() or c.isdigit() or c == '.'

    def parse(self):
        sz = len(self.q)
        st: list[FA] = []
        i = 0
        while i < sz:
            fa = FA()
            if not RegParser.is_operand(self.q[i]):
                if self.q[i] == '|':
                    fa.add_or_FA([st[-2], st[-1]], self.states)
                    st.pop()
                    st.pop()
                elif self.q[i] == '&':
                    fa.add_and_FA([st[-2], st[-1]], self.states)
                    st.pop()
                    st.pop()
                elif self.q[i] == '*':
                    fa.add_asterisk_FA(st[-1], self.states)
                    st.pop()
                elif self.q[i] == '+':
                    fa.add_plus_FA(st[-1], self.states)
                    st.pop()
                elif self.q[i] == '?':
                    fa.add_question_mark_FA(st[-1], self.states)
                    st.pop()
                elif self.q[i] == '[':
                    i+=1
                    substr = '['
                    while i<sz and self.q[i] != ']':
                        substr += self.q[i]
                        i += 1
                    substr += self.q[i]
                    fa.add_square_bracket_FA(substr, self.states)
            else:
                fa.add_operand_FA(self.q[i], self.states)
            st.append(fa)
            i += 1
        st[-1].end.is_terminating = True
        ret = {
            "startingState": f'S{st[-1].start.id}',
        }
        for s in self.states:
            ret.update(s.to_json())
        return ret

if __name__ == '__main__':
    parser = RegParser("[a*7]")
    ans = parser.parse()
    print(ans)
    with open("output.json", "w") as f:
        f.write(json.dumps(ans, indent=4))
