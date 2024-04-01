from queue import Queue

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
            if square_brackets>0:
                i+=1
                continue
            if not(text[i] in binary_operators or text[i] in opening_brackets or text[i+1] in binary_operators or text[i+1] in closing_brackets or text[i+1] in unary_operators):
                ret+='&'
            i+=1
        ret+=text[sz-1]
        return ret
    

if __name__ == '__main__':
    print(Preprocessor.preprocess("a((b?|c)(2*u))d*[a-zA-C]"))
        