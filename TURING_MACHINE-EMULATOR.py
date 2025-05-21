def removeComments(line):
    return line.split("#", 1)[0].strip()

def TmReadFromFile(filename):
    sectiune_curenta=None
    sectiuni={}

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
    
    #verificare sectiuni obligatorii
    required_sections=['states', 'input_alphabet', 'tape_alphabet', 'blank_symbol', 'initial_state', 'stop_state', 'transitions']
    for section in required_sections:
        if section not in sectiuni or not sectiuni[section]:
            print(f"Eroare: Sectiunea obligatorie {section} lipseste sau este goala.")
            return
    states_list=sectiuni.get('states',[""])[0].split()
    if not states_list:
        print("Eroare: Sectiunea states este goala")
        return
    states=set(states_list)

    input_alphabet_list = sectiuni.get('input_alphabet', [""])[0].split()
    input_alphabet = set(input_alphabet_list)

    tape_alphabet_list = sectiuni.get('tape_alphabet', [""])[0].split()
    if not tape_alphabet_list:
        print("Eroare: Sectiunea tape_alphabet este goala")
        return
    tape_alphabet=set(tape_alphabet_list)

    blank_symbol_str = sectiuni.get('blank_symbol', [""])[0].strip()
    if not blank_symbol_str:
        print("Eroare: Sectiunea blank_symbol este goala")
        return
    blank_symbol=blank_symbol_str
    if blank_symbol not in tape_alphabet:
        print("Eroare: Blank symbol nu se afla in tape_alphabet")
        return
    
    initial_state_str = sectiuni.get('initial_state', [""])[0].strip()
    if not initial_state_str:
        print("Eroare: Sectiunea initial_state este goala")
        return
    initial_state=initial_state_str

    stop_state_str=sectiuni.get('stop_state', [""])[0].strip()
    if not stop_state_str:
        print("Eroare: Sectiunea stop_state este goala")
        return
    stop_state=stop_state_str

    #tranzitii
    transitions={}
    valid_moves={'L','R','S'}
    
    for transition_line in sectiuni.get('transitions',[]):
        parts=transition_line.split()
        if len(parts)==5:
            current_state, current_char, next_state, write_char, move = parts

            #validari pentru parsare
            if current_state not in states: 
                print("Eroare: Starea curenta {current_state} nu e definita in sectiunea states")
                return None
            if current_char not in tape_alphabet: 
                print("Eroare: Caracterul curent {current_char} nu e definit in sectiunea tape_alphabet")
                return None
            if next_state not in states: 
                print("Eroare: Starea urmatoare {next_state} nu e definita in sectiunea states")
                return None
            if write_char not in tape_alphabet: 
                print("Eroare: Caracterul de scris {write_char} nu e definit in sectiunea tape_alphabet")
                return None
            if move not in valid_moves: 
                print("Eroare: Miscarea {move} nu e definita in valid_moves")
                return None
            
            transition_key=(current_state, current_char)
            
            transitions[transition_key]=(next_state, write_char,move)
        else:
            print("Eroare: Linie din tranzitii nu respecta formatul corect definit pentru o Masina Turing")
            return None
    
    return {
        'states': states,
        'input_alphabet': input_alphabet,
        'tape_alphabet': tape_alphabet,
        'blank_symbol': blank_symbol,
        'initial_state': initial_state,
        'stop_state': stop_state,
        'transitions': transitions 
    }

def TMEmulator(tm_definition, input_str):
    if tm_definition is None:
        print("Eroare: Nu s-a putut citi definitia Masinii Turing din fisier")
        return None
    
    states=tm_definition['states']
    input_alphabet=tm_definition['input_alphabet']
    tape_alphabet=tm_definition['tape_alphabet']
    blank_symbol=tm_definition['blank_symbol']
    initial_state=tm_definition['initial_state']
    stop_state=tm_definition['stop_state']
    transitions=tm_definition['transitions']

    tape=list(input_str)
    tape.extend([blank_symbol]*max(50, len(input_str))) #adaugam blank-uri de padding la final - head se va tot deplasa de-a lungul benzii, pentru a nu iesi din range-ul benzii adaug padding-uri suplimentare

    head=0
    state=initial_state

    max_steps=len(input_str)*100 #o limita de siguranta pentru a evita buclele infinite
    current_steps=0

    halted = False #flag care indica daca executia TM s-a oprit

    while state!=stop_state and current_steps<max_steps:
        current_steps+=1
        if head<0:
            current_char=blank_symbol
            print("Avertisment: Capul citeste la stanga de indexul 0. Se considera blank_symbol")
        elif head>=len(tape):
            current_char=blank_symbol
        else:
            #head se afla in limitele normale
            current_char=tape[head]
        
        transition_key=(state, current_char)
        determined_transition=transitions.get(transition_key, None)

        if determined_transition is None:
            print(f"Halting: Nu exista nicio tranzitie definita pentru starea {state} si caracterul {current_char}")
            halted=True #se opreste executia
            break
        else:
            next_state, write_char, move=determined_transition
            #verificari suplimentare pentru a ne asigura ca head-ul este in limitele benzii si nu se produc erori
            if head<0:
                print("Eroare: Capul e la stanga de indexul 0")
                halted=True
                break
            elif head>=len(tape):
                while len(tape)<=head:
                    tape.append(blank_symbol)
                tape[head]=write_char
            else:
                tape[head]=write_char
            
            if move=='R': #right
                head+=1
            elif move=='L': #left
                head-=1
            #daca e S (Stay), nu se intampla nimic, capul ramane la pozitia actuala

            state=next_state
    
    #verificari in cazul in care bucla s-a oprit neasteptat
    if current_steps>=max_steps:
        print("Avertisment: limita maxima de pasi a fost depasita")
    
    if halted:
        print("Emularea s-a oprit din cauza unei erori.")
    
    final_tape_str_stripped=''.join(tape).rstrip(blank_symbol) #eliminam blank-urile din sirul final

    try:
        final_dollar_index=final_tape_str_stripped.find('$')
        if final_dollar_index!=-1:
            result_string=final_tape_str_stripped[:final_dollar_index+1]
            return result_string
        else:
            return final_tape_str_stripped
    
    except Exception as e:
        print("Eroare la construirea sirului rezultat")
        return final_tape_str_stripped
    

tm_add_definition=TmReadFromFile("tm-add.txt")
input_str=input("Introduceti sirul:")
print(TMEmulator(tm_add_definition,input_str))


