def removeComments(line):
    return line.split("#", 1)[0].strip()

def NfaReadFromFile(filename):
    sectiune_curenta=None
    sectiuni={}
    transitions={}
    epsilon_transitions={}

    with open(filename, 'r') as fin:
        for line in fin:
            line=line.strip()
            if not line:
                continue
            line=removeComments(line)
            if not line:
                continue
            elif line.startswith("<") and line.endswith(">"):
                if line == '<end>':
                    sectiune_curenta = None
                else:
                    sectiune_curenta=line[1:-1]
                    sectiuni[sectiune_curenta]=[]
            elif sectiune_curenta:
                sectiuni[sectiune_curenta].append(line)
    #Validare aditionala a continutului fisierului (sa fiu sigur ca definitia NFA-ului contine toate componentele sale)
    required_sections=['states', 'alphabet', 'transitions', 'initial_state', 'accept_states']
    for section in required_sections:
        if section not in sectiuni or not sectiuni[section]:
            print(f"Eroare: Sectiunea obligatorie {section} lipseste sau este goala.")
            return
    
    states_list=sectiuni['states'][0].split()
    if not states_list:
        print(f"Eroare: Sectiunea states nu contine stari definite")
        return
    states=set(states_list)

    alphabet_list=sectiuni['alphabet'][0].split()
    alphabet=set(alphabet_list)
    
    initial_state_string=sectiuni['initial_state'][0].strip()
    if not initial_state_string:
        print(f"Eroare: Sectiunea initial_state este goala")
        return
    if initial_state_string not in states:
        print(f"Eroare: Starea initiala {initial_state_string} nu este definita in sectiunea states.")
        return
    initial_state=initial_state_string
    
    accept_states_list=sectiuni['accept_states'][0].split()
    accept_states=set(accept_states_list)

    for state in accept_states:
        if state not in states:
            print(f"Avertisment: Starea de accept {state} nu este definita in states")
    #accept_states=accept_states.intersection(states)

    for transition in sectiuni.get('transitions',[]):
        parts=transition.split()
        if len(parts)==3:
            state1,symbol,state2=parts
            #Validare pentru parsare
            if state1 not in states:
                print("Eroare in sectiunea de tranzitii: O stare sursa nu este definita")
                return
            if state2 not in states:
                print("Eroare in sectiunea de tranzitii: O stare destinatie nu este definita")
                return

            if symbol=="epsilon":
                if state1 not in epsilon_transitions:
                    epsilon_transitions[state1]=set()
                epsilon_transitions[state1].add(state2)
            else:
                if symbol not in alphabet:
                    print("Eroare: unul dintre simbolurile din sectiunea transitions nu se afla in alphabet.")
                    return

                if (state1,symbol) not in transitions:
                    transitions[(state1,symbol)]=set()
                transitions[(state1,symbol)].add(state2)
        
    return {
        'states': states,
        'alphabet': alphabet,
        'transitions': transitions,
        'epsilon_transitions': epsilon_transitions,
        'initial_state': initial_state,
        'accept_states': accept_states
    }

def EpsilonString(nfa,states): #handle-uieste cazurile in care simbolul din functia de tranzitie este epsilon
    epsilon_states=set(states) #multimea de stari accesibile prin epsilon
    stack=list(states) #stiva care parcurge starile atinse prin epsilon - in stiva este starea initiala

    while stack:
        state=stack.pop()
        if state in nfa['epsilon_transitions']:
            for next_state in nfa['epsilon_transitions'][state]:
                if next_state not in epsilon_states:
                    epsilon_states.add(next_state)
                    stack.append(next_state) #pt a verifica daca la randul ei starea x are tranzitii epsilon
    return epsilon_states

def NfaEmulator(nfa,input_str):

    if nfa is None:
        print("Eroare la citirea NFA-ului")
        return False

    current_states=EpsilonString(nfa, {nfa['initial_state']})
    
    for symbol in input_str.strip():
        if symbol not in nfa['alphabet']:
            print(f"Eroare: Simbolul {symbol} nu se afla in alfabet")
            return False
        next_states=set()

        for state in current_states:
            if (state,symbol) in nfa['transitions']:
                next_states.update(nfa['transitions'][(state,symbol)])

        if not next_states:
            print(f"Nicio stare accesibila dupa consumarea simbolului {symbol}")
            return False
        
        current_states=EpsilonString(nfa, next_states)
    
    return bool(current_states & nfa['accept_states'])

nfa=NfaReadFromFile('file1.nfa')
input_str=input("Introduceti un input: ")
print(NfaEmulator(nfa,input_str))