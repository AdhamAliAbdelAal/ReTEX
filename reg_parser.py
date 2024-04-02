class Operator:
    @staticmethod
    def precedence(op):
        if op == '|':
            return 1
        elif op == '&':
            return 2
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
    def __init__(self, is_accepting: bool = False, transitions: list["Transition"] = []):
        self.is_terminating = is_accepting
        self.transitions = transitions

    
class Transition:
    def __init__(self, input: str, to: State):
        self.to = to
        self.input = input

unary_operators = ['*', '+', '?']
binary_operators = ['|', '&', '-']
opening_brackets = ['(', '[']
closing_brackets = [')', ']']

class Preprocessor:
    @staticmethod
    def preprocess(text):
        ret = ""
        sz = len(text)
        square_brackets = 0
        i=0
        while i < sz-1:
            ret+=text[i]
            square_brackets += (text[i] == '[')
            square_brackets -= (text[i] == ']')
            if not(text[i] in binary_operators or text[i] in opening_brackets or text[i+1] in binary_operators or text[i+1] in closing_brackets or text[i+1] in unary_operators):
                ret+='&' if square_brackets ==0 else '|'
            i+=1
        ret+=text[sz-1]
        return ret
    
class FA:
    def __init__(self) -> None:
        self.start = None
        self.end = None

    def add_operand_FA(self, operand: str ,states: list[State]):
        self.start = State()
        self.end = State()
        states.append(self.start)
        states.append(self.end)
        if operand == '.':
            # for all digits and alphabets
            for i in range(26):
                if i<10:
                    transition = Transition(chr(ord('0')+i), self.end)
                    self.start.transitions.append(transition)
                transition = Transition(chr(ord('a')+i), self.end)
                self.start.transitions.append(transition)
                transition = Transition(chr(ord('A')+i), self.end)
                self.start.transitions.append(transition)
        else:
            transition = Transition(operand, self.end)
            self.start.transitions.append(transition)
    
    def add_or_FA(self, operator: str,operands: list["FA"], states: list[State]):
        self.start = State()
        self.end = State()
        states.append(self.start)
        states.append(self.end)
        self.start.transitions.append(Transition("eps",operands[0].start))
        self.start.transitions.append(Transition("eps",operands[1].start))
        operands[0].end.transitions.append(Transition("eps",self.end))
        operands[1].end.transitions.append(Transition("eps",self.end))
    
    def add_and_FA(self, operator: str,operands: list["FA"], states: list[State]):
        self.start = operands[0].start
        self.end = operands[1].end
        operands[0].end.transitions.append(Transition("eps",operands[1].start))

    def add_minus_FA(self, operator: str,operands: list[str], states: list[State]):
        self.start = State()
        self.end = State()
        states.append(self.start)
        states.append(self.end)
        for i in range(ord(operands[0]),ord(operands[1])+1):
            transition = Transition(chr(i), self.end)
            self.start.transitions.append(transition)
    
    def add_asterisk_FA(self, operator: str,operand: "FA", states: list[State]):
        self.start = State()
        self.end = State()
        states.append(self.start)
        states.append(self.end)
        self.start.transitions.append(Transition("eps",self.end))
        self.start.transitions.append(Transition("eps",operand.start))
        operand.end.transitions.append(Transition("eps",self.end))
        operand.end.transitions.append(Transition("eps",self.start))

    def add_plus_FA(self, operator: str,operand: "FA", states: list[State]):
        self.start = State()
        self.end = State()
        states.append(self.start)
        states.append(self.end)
        self.start.transitions.append(Transition("eps",operand.start))
        operand.end.transitions.append(Transition("eps",self.end))
        operand.end.transitions.append(Transition("eps",self.start))

    def add_question_mark_FA(self, operator: str,operand: "FA", states: list[State]):
        self.start = State()
        self.end = State()
        states.append(self.start)
        states.append(self.end)
        self.start.transitions.append(Transition("eps",self.end))
        self.start.transitions.append(Transition("eps",operand.start))
        operand.end.transitions.append(Transition("eps",self.end))
    

    
class RegParser:
    def __init__(self, text):
        self.text = Preprocessor.preprocess(text)
        self.build()
        self.states = []
    
    def build(self):
        q = []
        text = self.text
        st = []
        sz = len(text)
        for i in range(sz):
            # case 1: alphabet, digit, dot
            if text[i].isalpha() or text[i].isdigit() or text[i]=='.':
                q.append(text[i])
            # case 2: operators
            elif Operator.precedence(text[i]) is not None:
                while len(st)>0 and Operator.precedence(st[-1]) is not None and Operator.precedence(st[-1]) <= Operator.precedence(text[i]):
                    q.append(st.pop())
                st.append(text[i])
            # case 3: opening brackets
            elif text[i] in opening_brackets:
                st.append(text[i])
            # case 4: closing brackets
            elif text[i] in closing_brackets:
                opening = '(' if text[i] == ')' else '['
                while len(st)>0 and st[-1] != opening:
                    q.append(st.pop())
                if len(st)==0:
                    raise Exception("Invalid Regular Expression")
                st.pop()
        while(len(st)>0):
            if(st[-1] in opening_brackets):
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
        for i in range(sz):
            if not RegParser.is_operand(self.q[i]):
                if self.q[i] == '|':
                    pass
                elif self.q[i] == '&':
                    pass
                elif self.q[i] == '-':
                    pass
                elif self.q[i] == '*':
                    pass
                elif self.q[i] == '+':
                    pass
                elif self.q[i] == '?':
                    pass
                else:
                    pass




if __name__ == '__main__':
    # text = Preprocessor.preprocess("a((b?|c)(2*u))d*[a-zA-C]")
    # text = Preprocessor.preprocess("[a-zA-Z]")
    # text = Preprocessor.preprocess("a(b?|c)")
    # parser = RegParser("[a-zA-Z]").parse()
    parser = RegParser("a(b?|c)").parse()
    # parser = RegParser("a((b?|c)(2*u))d*[a-zA-C]").parse()
    
    