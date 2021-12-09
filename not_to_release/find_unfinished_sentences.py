import os
from sys import exit
from conllu import parse
os.chdir('/Users/elliottlash/Documents/GitHub/UD_Old_Irish-CritMinorGlosses/')

#************************************************************************************************************************
#Function Definitions

#The following series of functions produces several lists of unfinished sentences organized according to length.

def new_sentences_list(filename):
    return [a_sentence for a_sentence in parse(open(filename, 'r', encoding='utf-8').read())]

def check_head_deprel(sentence):
    
    realwords=[]
    done=[]
    
    for word in sentence:
        
        if isinstance(word['id'], int) and 'PUNCT' not in word['upos']:
            realwords.append(word)

    for word in realwords:
        
        if word['head'] != None and word['deprel'] != '_':
            done.append(1)
        elif word['head'] == None and word['deprel'] != '_':
            done.append(0)
        elif word['head'] == None and word['deprel'] == '_':
            done.append(0)

    return done, len(realwords)

def check_finished_sentences(filename):
    
    finished_sentences = []
    unfinished_sentences = []
        
    for sentence in new_sentences_list(filename):
        
        done, len_sent = check_head_deprel(sentence)
        
        if all(done):
            finished_sentences.append((sentence.metadata['sent_id'], len_sent))
        else:
            unfinished_sentences.append((sentence.metadata['sent_id'], len_sent))
            
    return finished_sentences, unfinished_sentences

def organize_unfinished_sentences(unfinished_sentences):
    
    #The following statement makes a list of empty lists based on the number of unique sentence lengths in the list of unfinished sentences
    list_of_sentence_lengths = [ [] for _ in range(list({sentence[1] for sentence in unfinished_sentences})[-1]) ]
    
    #The following for-loop fills the empty lists
    for sentence in unfinished_sentences:
        
        for count, li in enumerate(list_of_sentence_lengths):
            
            if sentence[1] == count+1:
                li.append(sentence)
                #if len(l) >= 1: ---- For testing purposes; note that this and the next line might need to be embedded in a for-loop on their own: for c,l in enumerate(list_of_sentence_lengths):
                     #print(c+1, len(l))
                
    return list_of_sentence_lengths


#************************************************************************************************************************
#User Input Section

answer_tracker = True

userinput_file = input('What is the name of your file? ')

finished_sentences, unfinished_sentences = check_finished_sentences(userinput_file)
list_of_sentence_lengths = organize_unfinished_sentences(unfinished_sentences)

userinput_length = input('What length of list do you want to test? ')

if len(list_of_sentence_lengths[int(userinput_length)-1]) == 1:
    print(f'There is {len(list_of_sentence_lengths[int(userinput_length)-1])} sentence in your list.')
elif len(list_of_sentence_lengths[int(userinput_length)-1]) >= 1:
    print(f'There are {len(list_of_sentence_lengths[int(userinput_length)-1])} sentences in your list.')
else:
    print(f'There are no sentences in your list.')
    answer_tracker = False

while answer_tracker == True:
    userinput_list = input('Do you want to print out the ids of the sentences in this list? y/n: ')

    if userinput_list == 'y':
        print('\n')
        print('\n')
        print(list_of_sentence_lengths[int(userinput_length)-1])
        print('\n')
        print('\n')
        break
    else:
        break

userinput_continue = input('Do you want to explore the rest of the data? y/n: ')
print('\n')
print('\n')
if 'y' in userinput_continue:
    print('Use the variable "finished_sentences" to see all finished sentences.')
    print('Use the variable "unfinished_sentences" to see all unfinished sentences.')
    print('Use the variable "list_of_sentence_lengths" to see a list of all unfinished sentences organized by length.')

else:
    print('Goodbye!')
    os._exit(0)
