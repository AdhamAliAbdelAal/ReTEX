from queue import Queue

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
    

# class RegParser:


if __name__ == '__main__':
    text = Preprocessor.preprocess("a((b?|c)(2*u))d*[a-zA-C]")
    # text = Preprocessor.preprocess("[a-zA-Z]")
    # text = Preprocessor.preprocess("a(b?|c)")
    print(text)
    q = Queue()
    st = []
    sz = len(text)
    for i in range(sz):
        # case 1: alphabet, digit, dot
        if text[i].isalpha() or text[i].isdigit() or text[i]=='.':
            q.put(text[i])
        # case 2: operators
        elif Operator.precedence(text[i]) is not None:
            while len(st)>0 and Operator.precedence(st[-1]) is not None and Operator.precedence(st[-1]) <= Operator.precedence(text[i]):
                q.put(st.pop())
            st.append(text[i])
        # case 3: opening brackets
        elif text[i] in opening_brackets:
            st.append(text[i])
        # case 4: closing brackets
        elif text[i] in closing_brackets:
            opening = '(' if text[i] == ')' else '['
            while len(st)>0 and st[-1] != opening:
                q.put(st.pop())
            if len(st)==0:
                raise Exception("Invalid Regular Expression")
            st.pop()
    while(len(st)>0):
        if(st[-1] in opening_brackets):
            raise Exception("Invalid Regular Expression")
        else:
            q.put(st[-1])
        st.pop()
    while(q.qsize()>0):
        print(q.get())
    