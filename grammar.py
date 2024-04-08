alphanumeric = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
dot = list('.')
parentheses = list('()')
brackets = list('[]')
operators = list('|&*-?+')

terminals = alphanumeric + dot + parentheses + brackets + operators

"""
 -> S||A | A
A -> AB | B
B  -> E* | E+ | E? | E
E -> (S) | [R] | T | ()
// range
R -> RG | G
G -> C-C | C
//terminals
T -> C | .
C -> alphanumeric 

"""
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
print(rule2Index)
N=100
mem = [[[-1 for _ in range(N)] for _ in range(N)] for _ in range(N)]


def is_terminal(c: str) -> bool:
    return c in terminals


def all_terminals(rule: list[str]) -> bool:
    return all([is_terminal(c) for c in rule])

def contains_terminals(rule: list[str]) -> bool:
    return any([is_terminal(c) for c in rule])


def get_indices_inbound(c: str, l: int, r: int, symbolIndices: dict[str, list[int]]) -> list[int]:
    if c not in symbolIndices:
        return []
    return [i for i in symbolIndices[c] if l <= i <= r]

def solve(left: int, right:int, idx: int, reg: str, symbolIndices: dict[str, list[int]]) -> bool:
    if left > right:
        return False
    rule = index2Rule[idx]
    for r in rules[rule]:
        # case1 r contains terminals only
        # base case
        if all_terminals(r):
            if len(r) != right-left+1:
                return False
            if reg[left:right+1] == ''.join(r):
                return True
        # case2 r contains terminals
        elif contains_terminals(r):
            if is_terminal(r[0]) and is_terminal(r[-1]):
                terminal_indices_left = get_indices_inbound(r[0], left, right, symbolIndices)
                terminal_indices_right = get_indices_inbound(r[-1], left, right, symbolIndices)
                for i in terminal_indices_left:
                    for j in terminal_indices_right:
                        if i < j and solve(i+1, j-1, rule2Index[r[1]],reg,symbolIndices):
                            return True
            else:
                # r[1] is a terminal
                terminal_indices = get_indices_inbound(r[1], left, right, symbolIndices)
                for i in terminal_indices:
                    if solve(left, i-1, rule2Index[r[0]],reg,symbolIndices):
                        if len(r) == 2:
                            if i == right:
                                return True
                        elif solve(i+1, right, rule2Index[r[2]],reg,symbolIndices):
                            return True
        # case3 r contains non-terminals only
        else:
            # match all string
            if len(r) == 1:
                if solve(left, right, rule2Index[r[0]],reg,symbolIndices):
                    return True
            else:
            # match till right-1
                for i in range(left, right):
                    if solve(left, i, rule2Index[r[0]],reg,symbolIndices) and solve(i+1, right, rule2Index[r[1]],reg,symbolIndices):
                        return True
    return False

def fill_symbol_indices(reg: str) -> dict[str, list[int]]:
    symbolIndices = {}
    for i,c in enumerate(reg):
        if c not in symbolIndices:
            symbolIndices[c] = [i]
        else:
            symbolIndices[c].append(i)
    return symbolIndices
reg = 'a?'

symbolIndices = fill_symbol_indices(reg)
print(solve(0, len(reg)-1, 0, reg, symbolIndices))


test_cases = [
    # Valid Regular Expression
    {"input": "a|b|c", "expected_output": True},
    
    # Invalid Regular Expression (Missing Closing Bracket)
    {"input": "((ABC)|(abc)", "expected_output": False},
    
    # Valid Regular Expression with Group
    {"input": "((ABC)|(abc))", "expected_output": True},
    
    # Valid Regular Expression with Character Range
    {"input": "[a-cA-C5]", "expected_output": True},
    
    # Invalid Regular Expression with Character Range (Incomplete Range)
    {"input": "[a-cA-C", "expected_output": False},
    
    # Valid Regular Expression with Any Single Character
    {"input": "a.c", "expected_output": True},
    
    # Valid Regular Expression with Zero or One Repetition
    {"input": "a?", "expected_output": True},
    
    # Valid Regular Expression with Zero or More Repetition
    {"input": "A*", "expected_output": True},
    
    # Valid Regular Expression with One or More Repetition
    {"input": "A+", "expected_output": True},
    
    # Invalid Regular Expression with Invalid Characters
    {"input": "$*?+", "expected_output": False},
    
    # Valid Regular Expression with Combination of Operators
    {"input": "A?(B|C)*D+", "expected_output": True},
    
    # Invalid Regular Expression with Improper Operator Usage
    {"input": "(A|B+C)*D?", "expected_output": False},
    
    # Empty Regular Expression
    {"input": "", "expected_output": False}
]

for test_case in test_cases:
    input_str = test_case["input"]
    expected_output = test_case["expected_output"]
    symbolIndices = fill_symbol_indices(input_str)
    output = solve(0, len(input_str)-1, 0, input_str, symbolIndices)
    print(f"Test case passed with input: {input_str} and expected output: {expected_output}. Output: {output}")