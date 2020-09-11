import random

# dictionary with act as key and corresponding words as values
rules = {}
rules['ack'] = ['okay', 'okay um', 'alright']
rules['affirm'] = ['yes right', 'right', 'yes']
rules['bye'] = ['see you', 'good bye', 'bye']
rules['confirm'] = ['is it']
rules['deny'] = ['i dont want']
rules['hello'] = ['hi', 'hello']
rules['inform'] = ['looking for']
rules['negate'] = ['no']
rules['repeat'] = ['can you repeat that', 'what did you say']
rules['reqalts'] = ['how about']
rules['reqmore'] = ['more']
rules['request'] = ['what is', 'where']
rules['restart'] = ['start over']
rules['thankyou'] = ['thank you', 'thanks']


not_aborted = True
while not_aborted:
    acts = []
    sentence = input('Enter a sentence or type quit to exit the program:')
    if sentence.lower() != 'quit':
        for k, v in rules.items():
            if any(keywords in sentence.lower() for keywords in v):
                acts.append(k)

        if not acts:
            print('null')
        else:
            print(random.choice(acts))

    elif sentence.lower() == 'quit':
        not_aborted = False
    print('')

