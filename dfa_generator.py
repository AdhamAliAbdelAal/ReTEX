import json
from typing import Tuple, Union
from collections import deque
from matplotlib import pyplot as plt
import pyvis.network as net
import networkx as nx

EPS = 'eps'


class State:
    def __init__(self, id: str, is_terminating_state: bool, transitions: dict[str, list[str]]):
        self.id = id
        self.is_terminating_state = is_terminating_state
        self.transitions = transitions

    def have_transition(self, input: str) -> bool:
        return input in self.transitions.keys()


class AutomataMachine:
    def __init__(self, name: str = 'Automata'):
        self.name = name
        self.starting_state: str = None
        self.states = {}

    def init_from_file(self, json_file):
        self.states = self.load_json(json_file)
        return self

    def init_from_dict(self, states: dict[str, bool], starting_state: str, transitions: dict[str, dict[str, list[str]]]):
        self.starting_state = starting_state
        for state, is_terminal in states.items():
            self.add_state(state, is_terminal, transitions[state])

    def load_json(self, json_file) -> dict[str, State]:
        with open(json_file, 'r') as file:
            data = json.load(file)
        # print(data)
        self.starting_state: str = data['startingState']
        data.pop('startingState')

        states = {}
        for key, value in data.items():
            # v can be a list of states or a single state
            transitions = {k: [v] if not isinstance(
                v, list) else v for k, v in value.items() if k != 'isTerminatingState'}

            states[key] = State(
                key, value['isTerminatingState'], transitions)
        return states

    def get_starting_state(self):
        return self.starting_state

    def get_state(self, state):
        return self.states[state]

    def is_terminating_state(self, state):
        return self.states[state].is_terminating_state

    def get_next_state(self, state, input) -> Union[list[str], None]:
        """
        Returns the next state given the current state and input 
        and `None` if the transition is not possible
        """
        if input not in self.states[state].transitions.keys():
            return None
        nxt_state = self.states[state].transitions[input]
        return nxt_state

    def add_state(self, state: str, is_terminating_state: bool, transitions: dict[str, list[str]]):
        self.states[state] = State(state, is_terminating_state, transitions)

    def add_transition(self, state: str, input: str, next_state: str):
        if state not in self.states.keys():
            self.add_state(state, False, {})
        if input not in self.states[state].transitions.keys():
            self.states[state].transitions[input] = []

        self.states[state].transitions[input].append(next_state)

    def draw(self):
        g = nx.MultiDiGraph(seed=42)
        for state in self.states.values():
            # https://stackoverflow.com/questions/74082881/adding-icon-for-node-shape-using-networkx-and-pyvis-python
            g.add_node(
                state.id, color='gray' if not state.id == self.starting_state else 'orange', shape='diamond' if state.is_terminating_state else 'circle'
            )
            for k, v in state.transitions.items():
                for dest_state in v:
                    g.add_edge(state.id, dest_state, label=k,
                               color='red' if k == EPS else 'black', merge=False,)

        nt = net.Network(notebook=True, cdn_resources='remote', directed=True)
        nt.show_buttons(filter_=['physics'])
        nt.from_nx(g)
        nt.repulsion(spring_strength=0.02)
        nt.toggle_physics(True)
        nt.show(f'{self.name}_FSM.html')

        # draw using nx instead
        # pos = nx.planar_layout(g)
        # plt.figure()
        # nx.draw(g,pos,with_labels=True)
        # plt.show()
        # Drawing the graph
        # First obtain the node positions using one of the layouts


class dfa_generator:

    def __init__(self, json_file):
        self.nfa_sm = AutomataMachine().init_from_file(json_file)

    def get_states_group_id(self, states: set[str]):
        """
        if a group contains S0, S3 and S4, the id will be S0_S3_S4
        """
        l = list(states)
        l.sort()
        return '_'.join(l)

    def get_closure(self, state: State) -> Tuple[set[str], set[str], bool]:
        """
        Returns the epsilon closure of a state
        2 sets are returned, one for the states and the other for the combined Transitions
        """
        ret_states = set()
        ret_transitions = set()
        q = deque()
        q.append(state)
        is_terminating = False
        while q:
            curr_state = q.popleft()
            ret_states.add(curr_state.id)
            is_terminating = is_terminating or curr_state.is_terminating_state
            # the transitions of the group is the union of all transitions from each state
            ret_transitions = ret_transitions.union(
                set(curr_state.transitions.keys()))

            if EPS in curr_state.transitions.keys():
                for s in curr_state.transitions[EPS]:
                    if s not in ret_states:
                        q.append(self.nfa_sm.get_state(s))

        return ret_states, ret_transitions, is_terminating

    def convert_to_dfa(self):
        """
        Converts an NFA to a DFA
        """
        start_state = self.nfa_sm.get_starting_state()
        start_closure_states, start_closure_T, is_terminal = self.get_closure(
            self.nfa_sm.get_state(start_state))

        states: dict[str, bool] = {}
        # {state: {input: [next_states]}}
        transitions: dict[str, dict[str, list[str]]] = {}
        q = deque()
        q.append((start_closure_states, start_closure_T, is_terminal))

        while q:
            curr_group_states, curr_group_Ts, is_terminal = q.popleft()
            curr_id = self.get_states_group_id(curr_group_states)
            states[curr_id] = is_terminal
            transitions[curr_id] = {}
            for t in curr_group_Ts:
                if t == EPS:
                    continue
                next_group_states = set()
                next_group_Ts = set()
                next_is_terminal = False

                for state in curr_group_states:
                    s = self.nfa_sm.get_state(state)
                    if s.have_transition(t):
                        # reachable from the current group
                        next_states = s.transitions[t]
                        for ns in next_states:
                            se, te, it = self.get_closure(
                                self.nfa_sm.get_state(ns))
                            next_group_states = next_group_states.union(se)
                            next_group_Ts = next_group_Ts.union(te)
                            next_is_terminal = next_is_terminal or it

                transitions[curr_id][t] = [
                    self.get_states_group_id(next_group_states)]
                if self.get_states_group_id(next_group_states) not in states.keys():
                    q.append((next_group_states, next_group_Ts, next_is_terminal))

        new_dfa = AutomataMachine(name='DFA')
        new_dfa.init_from_dict(states, self.get_states_group_id(
            start_closure_states), transitions)
        return new_dfa

    def minimize_dfa(self, dfa):
        """
        Minimizes a DFA
        """
        pass


if __name__ == "__main__":
    state_machine = AutomataMachine().init_from_file('r1.json')
    print(state_machine.get_state('S1').transitions)
    print(state_machine.is_terminating_state('S0'))
    print(state_machine.get_next_state('S0', '1a'))
    print(state_machine.get_next_state('S0', '1'))
    print(state_machine.get_starting_state())
    state_machine.draw()
    dfa = dfa_generator('r1.json')
    aa = dfa.get_closure(dfa.nfa_sm.get_state('S2'))
    new_dfa = dfa.convert_to_dfa()
    new_dfa.draw()
    print(aa)
