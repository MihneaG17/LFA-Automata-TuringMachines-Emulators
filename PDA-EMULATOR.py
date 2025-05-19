def removeComments(line):
    return line.split("#", 1)[0].strip()

def PdaReadFromFile(filename):
    sectiune_curenta = None
    sectiuni = {}
    transitions = {}

    with open(filename, 'r') as fin:
        for line in fin:
            line = removeComments(line)
            if not line:
                continue
            if line.startswith("<") and line.endswith(">"):
                if line == "<end>":
                    sectiune_curenta = None
                else:
                    sectiune_curenta = line[1:-1]
                    sectiuni[sectiune_curenta] = []
            elif sectiune_curenta:
                sectiuni[sectiune_curenta].append(line)

    required_sections=['states', 'alphabet', 'stack_alphabet', 'transitions', 'initial_state', 'accept_states', 'initial_stack_symbol']
    for section in required_sections:
        if section not in sectiuni or not sectiuni[section]:
            if section != 'accept_states':
                print(f"Eroare: Sectiunea obligatorie {section} lipseste sau e goala")
                return

    states_list = sectiuni.get('states',[""])[0].split()
    if not states_list:
        print("Eroare: Sectiunea states nu contine stari definite")
        return
    states=set(states_list)

    alphabet_list=sectiuni.get('alphabet',[""])[0].split()
    alphabet=set(alphabet_list)

    stack_alphabet_list=sectiuni.get('stack_alphabet',[""])[0].split()
    if not stack_alphabet_list:
        print("Eroare: Sectiunea stack_alphabet nu contine simboluri definite")
        return
    stack_alphabet=set(stack_alphabet_list)

    initial_state_string=sectiuni.get('initial_state',[""])[0].strip()
    if not initial_state_string:
        print("Eroare: Sectiunea initial_state e goala")
        return
    if initial_state_string not in states:
        print("Eroare: Starea initiala nu se afla in sectiunea states")
        return
    initial_state=initial_state_string

    accept_states_list=sectiuni.get('accept_states',[""])[0].split()
    accept_states=set(accept_states_list)

    initial_stack_symbol_str=sectiuni.get('initial_stack_symbol',[""])[0].strip()
    if not initial_stack_symbol_str:
        print("Eroare: Sectiunea initial_stack_symbol este goala.")
        return
    if initial_stack_symbol_str not in stack_alphabet:
        print("Eroare: Simbolul initial al stivei nu e definit in sectiunea 'stack_alphabet")
        return
    initial_stack_symbol=initial_stack_symbol_str


    for transition in sectiuni.get('transitions', []):
        parts = transition.split()
        if len(parts) == 5:
            src_state, input_symbol, stack_top, dest_state, stack_push = parts
            
            if src_state not in states:
                print("Eroare: Stare sursa din sectiunea transitions nu este definita")
                return
            if dest_state not in states:
                print("Eroare: Stare destinatie din sectiunea transitions nu este definita")
                return
            
            if input_symbol!="epsilon" and input_symbol not in alphabet:
                print("Eroare:Simbolul de intrare nu e epsilon si nu se afla in alphabet")
                return
            
            if stack_top not in stack_alphabet:
                print("Eroare: Simbolul din varful stivei nu se afla in alfabetul stivei")
                return

            if stack_push != "epsilon":
                for s in stack_push:
                    if s not in stack_alphabet:
                        print("Eroare: O tranzitie contine un simbol care nu se afla in alfabetul stivei")
                        return
            
            key = (src_state, input_symbol, stack_top)
            if key not in transitions:
                transitions[key] = []
            transitions[key].append((dest_state, stack_push))

    return {
        'states': states,
        'alphabet': alphabet,
        'stack_alphabet': stack_alphabet,
        'initial_state': initial_state,
        'accept_states': accept_states,
        'initial_stack_symbol': initial_stack_symbol,
        'transitions': transitions
    }

def PdaEpsilonClosure(pda, current_configs):
    reachable_configs=set(current_configs)
    configs_to_process=list(current_configs) #lista folosita pe post de stiva pentru explorare

    while configs_to_process:
        current_state, current_stack_tuple = configs_to_process.pop()
        current_stack=list(current_stack_tuple)

        stack_top=current_stack[-1] if current_stack else None

        transition_key=(current_state, "epsilon", stack_top) if stack_top is not None else None

        possible_destinations=pda['transitions'].get(transition_key, []) if transition_key else []

        for dest_state, stack_push_str in possible_destinations:
            new_stack=current_stack[:-1] if stack_top is not None else list(current_stack)

            if stack_push_str != "epsilon":
                new_stack.extend(list(stack_push_str[::-1]))
            
            new_config = (dest_state, tuple(new_stack))

            if new_config not in reachable_configs:
                reachable_configs.add(new_config)
                configs_to_process.append(new_config)
        
        return reachable_configs

def PdaEmulator(pda, input_str):
    if pda is None: 
        print("Eroare la citirea PDA-ului")
        return False

    initial_configs = {(pda['initial_state'], (pda['initial_stack_symbol'],))}
    
    current_configurations = PdaEpsilonClosure(pda, initial_configs)

    processed_input = input_str.strip()

    #Tratam cazul sirului vid inainte de a intra in bucla
    if not processed_input:
         print("Sirul de intrare este vid.")
         for state, stack_content in current_configurations:
             if state in pda['accept_states']:
                 return True
         return False


    for symbol in processed_input:

        #Validare pentru simbolul de intrare
        if symbol not in pda['alphabet']:
            print(f"Eroare: Simbolul {symbol} nu se afla in alphabet.")
            return False
        
        #Setul de configuratii atinse dupa consumarea simbolului curent
        next_configurations_after_symbol: set[tuple[str, tuple[str, ...]]] = set()
        
        for current_state, current_stack_tuple in current_configurations:
            current_stack = list(current_stack_tuple)
            stack_top = current_stack[-1] if current_stack else None

            transition_key = (current_state, symbol, stack_top) if stack_top is not None else None
            possible_destinations = pda['transitions'].get(transition_key, []) if transition_key else []

            for dest_state, stack_push_str in possible_destinations:
                 new_stack = current_stack[:-1] if stack_top is not None else list(current_stack)
                 
                 if stack_push_str != "epsilon":
                      new_stack.extend(list(stack_push_str[::-1]))

                 new_config = (dest_state, tuple(new_stack))
                 next_configurations_after_symbol.add(new_config)

        if not next_configurations_after_symbol:
            return False 

        current_configurations = PdaEpsilonClosure(pda, next_configurations_after_symbol)
        
    for state, stack_content in current_configurations:
        if state in pda['accept_states']:
            return True

    return False 

pda=PdaReadFromFile("file1.pda")
input_str=input("Introduceti un input: ")
print(PdaEmulator(pda, input_str))