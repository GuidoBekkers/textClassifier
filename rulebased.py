import random

# dictionary with act as key and corresponding words as values
rules = {'ack': ['okay', 'okay um', 'alright'], 'affirm': ['yes right', 'right', 'yes'],
         'bye': ['see you', 'good bye', 'bye'], 'confirm': ['is it'], 'deny': ['i dont want'], 'hello': ['hi', 'hello'],
         'inform': ['looking for'], 'negate': ['no'], 'repeat': ['can you repeat that', 'what did you say'],
         'reqalts': ['how about'], 'reqmore': ['more'], 'request': ['what is', 'where'], 'restart': ['start over'],
         'thankyou': ['thank you', 'thanks']}

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

