#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Updated Fri Feb 8 2022
@author elliottlash
DFG project
Georg-August-Universität Göttingen
Sprachwissenschaftliches Seminar

"""

import os
from sys import exit
from conllu import parse
os.chdir('/Users/elliottlash/Documents/GitHub/UD_Old_Irish-CritMinorGlosses/') #Change this to the directory where your conllu file is stored.

# ========================================================================================================================================================================================================
#
# This python script finds sentences in a conllu file whose tagging has not been completed. 
#
# ========================================================================================================================================================================================================
#Part 1. Function Definitions

def new_sentences_list(filename):
    '''
    Opens a conllu file and returns a List of senences, where each sentence is a TokenList.
    '''
    return [a_sentence for a_sentence in parse(open(filename, 'r', encoding='utf-8').read())]

def check_head_deprel(sentence):
    '''
    For each "real" word in a given sentence, this function checks to see if the word has been tagged.
    '''
    realwords=[] #Words exclusive of concatenated morphs and punctuation
    done=[] #Tagged Words (Head and Deprel columns are filled)
    
    for word in sentence:
        
        if isinstance(word['id'], int) and 'PUNCT' not in word['upos']: #The 'isinstance' statement excluded concatenated morphs which have a tuple in the id column.
            realwords.append(word)

    for word in realwords:
        
        if word['head'] != None and word['deprel'] != '_': # The tagging of a word is done, if both the head and the deprel column are filled in. Because these columns are encoded differently, the "done" value for each is distinct. Finished heads have a done value of "not None". Finished deprels have a done value of "not _". 
            done.append(1) #Fully tagged words get the value 1 (= True). Unfinished words get the value 0 (= False).
        elif word['head'] == None and word['deprel'] != '_': # If only the deprel is done, the word is not fully tagged.
            done.append(0)
        elif word['head'] == None and word['deprel'] == '_': # If both the head and the deprel are not tagged, the word is not fully tagged.
            done.append(0)                                   # Why not have a fourth condition: head is done but deprel isn't?

    return done, len(realwords)


#The following series of functions produces several lists of unfinished sentences organized according to length.

def check_finished_sentences(filename):
    '''
    This function checks each sentence to see if the tagging of that sentence is completed or not.
    '''
    finished_sentences = []
    unfinished_sentences = []
        
    for sentence in new_sentences_list(filename):
        
        done, len_sent = check_head_deprel(sentence)
        
        if all(done): #If every word in a sentence is done (has a value of 1
            finished_sentences.append((sentence.metadata['sent_id'], len_sent)) #Append the sentence to the list of finished sentences.
        else:
            unfinished_sentences.append((sentence.metadata['sent_id'], len_sent)) #Otherwise append the sentence to the list of unfinished sentences.
            
    return finished_sentences, unfinished_sentences

def organize_unfinished_sentences(unfinished_sentences):
    '''
    This function creates a list of unfinished sentences organized by length.
    '''
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

def write_out(save_trigger, list_of_sentence_lengths, filename, length):
    '''
    This function writes out a list of unfinished sentences to a file.
    '''
    if save_trigger == 'save':
        
        newlist = []
        print('\n')
        print('\n')

        userinput_output = input('Enter the name of the output file: ')

        #The following for-loop compares the selected list with the complete list of parsed sentences to match sentence ids of the selected unfinished sentences with the contents of those sentences.
        for id_length in list_of_sentence_lengths[int(length)-1]:  #Note that every item in each list in the list_of_sentence_length is a tuple consisting of a sentence id and a sentence length.
            
            for sentence in new_sentences_list(filename):
                
                if int(length)-1 >= 1 and sentence.metadata['sent_id'] == id_length[0]: #If the selected length is 1 or more and the sentence id of the current sentence is equal to the first item of the tuple,
                    
                    newlist.append(sentence)

        if len(newlist) >= 1: #If newlist actually consists of a list of sentences.

            with open(userinput_output, 'w', encoding='utf-8') as file_out: 

                for sent in newlist:
                    
                    file_out.write(sent.metadata['sent_id'])
                    file_out.write(' ' + str(sent))
                    file_out.write('\n')

            print('\n')
            print('\n')
            print('The sentences have been saved to a file!')
            print('\n')
            print('\n')
            print('Goodbye!')
            os._exit(0)
    else:
        return False #If the user does not want to save, the function returns False. Below this is saved to the variable "answer_tracker". This has the result of stopping the while-loop.
    
#************************************************************************************************************************
#Part 2. User Input Section

answer_tracker = True

userinput_file = input('What is the name of your file? ')

finished_sentences, unfinished_sentences = check_finished_sentences(userinput_file)
list_of_sentence_lengths = organize_unfinished_sentences(unfinished_sentences)

userinput_length = input('What length of list do you want to test? ')

print('\n')

if len(list_of_sentence_lengths[int(userinput_length)-1]) == 1:
    print(f'There is {len(list_of_sentence_lengths[int(userinput_length)-1])} sentence in your list.')
elif len(list_of_sentence_lengths[int(userinput_length)-1]) >= 1:
    print(f'There are {len(list_of_sentence_lengths[int(userinput_length)-1])} sentences in your list.')
else:
    print(f'There are no sentences in your list.')
    answer_tracker = False

print('\n')

#The while-loop presents the user with a series of questions if the "answer_tracker" is not False, that is, if there are actually sentences to display in the selected list. If there are no sentences, "answer_tracker" is set to False and the while-loop stops.
while answer_tracker == True:
    
    userinput_list = input('Do you want to print out the ids of the sentences in this list? y/n: ')
    print('\n')
    print('\n')
    
    if userinput_list == 'y':
        print(list_of_sentence_lengths[int(userinput_length)-1])
        print('\n')
        print('\n')
        userinput_save_to_file = input('If you want to save these sentences to a file and quit, type "save", otherwise type "continue": ')
        answer_tracker = write_out(userinput_save_to_file, list_of_sentence_lengths, userinput_file, userinput_length)
    elif userinput_list == 'n':
        userinput_save_to_file = input('If you want to save these sentences to a file and quit, type "save", otherwise type "continue": ')
        answer_tracker = write_out(userinput_save_to_file, list_of_sentence_lengths, userinput_file, userinput_length)
    else:
        break

print('\n')
print('\n')   
userinput_continue = input('Do you want to explore the rest of the data? y/n: ')
print('\n')
print('\n')   

if 'y' in userinput_continue:
    if len(unfinished_sentences) == 1:
        print(f'There is still {len(unfinished_sentences)} fully or partially untagged sentence.')
    elif len(unfinished_sentences) >= 1:
        print(f'There are still {len(unfinished_sentences)} fully or partially untagged sentences.')
    else:
        print('All the sentences have been tagged.')
        print('\n')
        print('\n')
        print('Goodbye!')
        os._exit(0)
    print('\n')
    print('\n')
    print('*******************************************************************************')
    print('>>> Use the list variable "finished_sentences" to see all finished sentences.')
    print('>>> Use the list variable "unfinished_sentences" to see all unfinished sentences.')
    print('>>> Use the list variable "list_of_sentence_lengths" to see all unfinished sentences organized by length.')
else:
    print('\n')
    print('\n') 
    print('Goodbye!')
    os._exit(0)

#********************************************************************************************************************************************
#Part 3. Extensions to the basic script
'''
list_of_sentences = new_sentences_list('sga_critminorglosses-ud-test.conllu')
list_of_ids = [sentence_id[0] for sentence_id in list_of_sentence_lengths[NUMBER1]] #NUMBER1 is the number length of the sentence minus one

sentences = []
sentences_beginning_tuple = []
sentences_beginning_idest = []
other_sentences = []
final_sentences = []
ids_of_sentences = [] #Perhaps superfluous
ids_of_accounted_for_sentences = [] #Perhaps superfluous

for sentence in list_of_sentences:
    for idn in list_of_ids:
        if sentence.metadata['sent_id'] == idn:
            sentences.append(sentence)
			
for sentence in sentences:
    ids_of_sentences.append(sentence.metadata['sent_id'])
    if len(sentence) == NUMBER2 and isinstance(sentence[0]['id'], tuple): #NUMBER2 is the number length of the sentence plus one
        sentence_beginning_tuple.append(sentence)
    elif len(sentence) == NUMBER2 and sentence[0]['form'] == '.i.' and isinstance(sentence[1]['id'], tuple):
        sentence_beginning_idest.append(sentence)
    elif len(sentence) == NUMBER3 #NUMBER2 is the number length of the sentence
        other_sentences.append(sentence)
    else:
        final_sentences.append(sentence)
    ids_of_accounted_for_sentences.append(sentence.metadata['sent_id'])

#All of the rest below may be superfluous...
for sentence in (sentence_beginning_tuple + sentence_beginning_idest + sentence_beginning_idest):
    ids_of_accounted_for_sentences.append(sentence.metadata['sent_id'])

list_of_unaccounted_for_sentences = list(set(ids_of_sentences)-set(ids_of_accounted_for_sentences)))

for sentence in sentences:
    for idn in list_of_unaccounted_for_sentences:
        if sentence.metadata['sent_id'] == idn:
            final_sentences.append(sentence)

To find negative copula sentences:
f,u=check_finished_sentences('sga_critminorglosses-ud-test.conllu')
real=[]
negativecopulasentence=[]
for fin in f:
	for sent in s:
		if sent.metadata['sent_id'] == fin[0]:
			for word in sent:
				if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
					real.append(word)
			for c,real_word in enumerate(real):
				if c+1 != len(real) and 'negative' in real_word['xpos'] and real[c+1]['upos'] == 'AUX':
					negativecopulasentence.append(sent)
			real=[]
'''

	
