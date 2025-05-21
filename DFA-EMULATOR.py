def removeComments(line):
    return line.split("#", 1)[0].strip()

def dfaReadFromFile(filename):
    sectiune_curenta = None
    sectiuni={}
    transitions={}

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

    #validare extra pentru parsare-verific daca in fisier sunt prezente toate sectiunile necesare descrierii unui DFA
    required_sections = ['states', 'alphabet', 'initial_state', 'accept_states', 'transitions']
    for section in required_sections:
        if section not in sectiuni or not sectiuni[section]:
            print(f"Eroare: Sectiunea {section} nu a fost gasita in fisier")
            return
    
    states_list=sectiuni['states'][0].split()
    if not states_list:
        print(f"Eroare: Sectiunea states nu contine stari definite")
        return
    states=set(states_list)

    alphabet_list=sectiuni['alphabet'][0].split()
    if not alphabet_list:
        print(f"Eroare: Sectiunea alphabet nu contine simboluri definite")
        return
    alphabet=set(alphabet_list)
    
    initial_state_string=sectiuni['initial_state'][0].strip()
    if not initial_state_string:
        print(f"Eroare: Sectiunea initial_state este goala")
        return
    initial_state=initial_state_string
    
    accept_states_list=sectiuni['accept_states'][0].split()
    accept_states=set(accept_states_list)


    for transition in sectiuni.get('transitions', []):
        parts=transition.split()
        if len(parts)==3:
            state1,symbol,state2=parts
            #verificari suplimentare pentru corectitudinea definirii DFA-ului
            if state1 not in states:
                print("Eroare in sectiunea de tranzitii: O stare sursa nu este definita")
                return
            
            if symbol not in alphabet:
                print("Eroare in sectiunea de tranzitii: Un simbol nu este definit")
                return
            
            if state2 not in states:
                print("Eroare in sectiunea de tranzitii: O stare destinatie nu este definita")
                return
            transitions[(state1,symbol)]=state2
    
    return {
        'states': states,
        'alphabet': alphabet,
        'transitions': transitions,
        'initial_state': initial_state,
        'accept_states': accept_states
    }

def dfaEmulator(dfa, input_str):
    current_state = dfa['initial_state']
    for symbol in input_str.strip():
        if symbol not in dfa['alphabet']:
            print("Eroare: Simbolul nu se afla in alfabet")
            return False
        if (current_state, symbol) in dfa['transitions']:
            current_state=dfa['transitions'][(current_state, symbol)]
        else:
            print("Eroare: Tranzitie lipsa")
            return False
    return current_state in dfa['accept_states']
        

dfa_data=dfaReadFromFile("file1.dfa")
input_str=input("Introduceti un input: ")
print(dfaEmulator(dfa_data,input_str)) #Afiseaza True daca se ajunge in starea finala si False in caz contrar



