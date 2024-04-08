import json


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

    def add_square_bracket_FA(self, ranges: list[list[str]], states: list[State]):
        self.start = State()
        self.end = State()
        states.append(self.start)
        states.append(self.end)
        for operands in ranges:
            if len(operands) == 2:
                for i in range(ord(operands[0]), ord(operands[1])+1):
                    transition = Transition(chr(i), self.end)
                    self.start.transitions.append(transition)
            else:
                transition = Transition(operands[0], self.end)
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
                    substr = ''
                    while i<sz and self.q[i] != ']':
                        substr += self.q[i]
                        i += 1
                    ranges = []
                    j = 0
                    while j < len(substr):
                        if j+2 < len(substr) and substr[j+1] == '-':
                            ranges.append([substr[j], substr[j+2]])
                            j += 3
                        else:
                            ranges.append([substr[j]])
                            j += 1
                    fa.add_square_bracket_FA(ranges, self.states)
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
    # text = Preprocessor.preprocess("a((b?|c)(2*u))d*[a-zA-C]")
    # text = Preprocessor.preprocess("[a-zA-Z]")
    # text = Preprocessor.preprocess("a(b?|c)")
    # parser = RegParser("[a-zA-Z]").parse()
    parser = RegParser("a*[0b-c1-5i]?")
    ans = parser.parse()
    print(ans)
    # parser = RegParser("a((b?|c)(2*u))d*[a-zA-C]").parse()
    with open("output.json", "w") as f:
        f.write(json.dumps(ans, indent=4))
