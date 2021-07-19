#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Updated Mon Jul 12 2021
@author elliottlash
DFG project
Georg-August-Universität Göttingen
Sprachwissenschaftliches Seminar

This will add concatenated strings and punctuation in new rows of an alreaady processed conllu file.


"""

import itertools
import os
import sys
import re
from conllu import parse

os.chdir('/Users/elliottlash/Documents/GitHub/UD_Old_Irish-CritMinorGlosses/')

# ========================================================================================================================================================================================================
# ========================================================================================================================================================================================================
#
#
#****************** About the project ******************
#*******************************************************
#
#
# This python script edits conllu files.

#
# To run this script put it in a folder with the csv file and use Terminal (on a Mac). Navigate to the directory with the python script and the csv file.
# Then type the following at the commandline:
#
#                       python3 name_of_py_script name_of_csv_file current_conllu_file new_conllu_file
#
#
# If an interactive python session is required in order to test any function in this script, run this script in a python shell compatible with python 3
# (N.B. ignore the Traceback error referring to do_all(sys.argv[2], new_sentences_list(sys.argv[1])).
#
# At the command line type first os.chdir('/path to file/') and then data_file='name_of_conllu_file'. The variable name "data_file" can be used in the functions
# in Section 1 to read this file. Note that all of the libraries in the import statements above need to be installed.
#
# Important: sentence metadata (newdoc id, sent_id, text, text_en) can be accessed by typing current_sentence.metada['key'],
# where 'key' = 'newdoc id', 'sent_id', 'text', 'text_en'.
#
# For example, given 'test.conllu', running the script in an interactive session proceeds as follows:
#
# os.chdir('/path to file/'
# data_file = 'test.conllu')
# new_sentences = new_sentences_list(data_file)  ## N.B. this creates a list in python.
# new_sentences[0].metada['text']
# '.i. airndib múcnae 7 airndib ecmailt ánétach 7 ambiad 7 andeug innaní prithchite hiris 7 condib trianuile ṁbethaid ón dano 7 nib cuit ree ·'

# The metadata can also be saved to a variable: text=new_sentences[0].metada['text'].
# The string in the variable text can now be split by typing text.split() (N.B. this means it has type str in python)
# To access the attributes of words, one needs to type word['attribute'] where 'attribute' can be one of the following:
# 'id' = the line number associated with the word. (N.B. type = int in python)
# 'form' = the word itself. (N.B. type = str in python)
# 'lemma' = the form of the word that is found as the dictionary headword. (N.B. type = str in python)
# 'upos' = the universal dependencies approved part of speech, e.g. VERB for verbs, ADP for prepositions, PART for particles, etc. (N.B. type = str in python)
# 'xpos' = the ChronHib-derived part of speech as found on the CorPH website. (N.B. type = str in python)
# 'feats' = A dict of attribute:value pairs that specify the morphological makeup of the word, e.g. adjective might have the following attribute:value pairs: Case:Nom,Number:Sing,Gender:Neut. (N.B. type = dict in python).
# 'head' = The head/governor of the current word. (N.B. type = int in python).
# 'deprel' = The deprel that is assigned to the current word to tag its function in relation to the head. (N.B. type = str in python).
# 'deps' = The combination of head and deprel in the schema head:deprel. 
# 'misc' = Usually has a gloss in this treebank. (N.B. type = dict in python)
#
# For example if the first sentence in the list new_sentences is new_sentences[0] (see above for the string corresponding to the text of new_sentences[0]),
# the first word is new_sentences[0][0] and the form of that word is new_sentences[0][0]['form'], which corresponds to the string '.i.'.
#
# 
# ========================================================================================================================================================================================================
# ========================================================================================================================================================================================================
#
# ========================================================================================================================================================================================================

# Part 1. Editing the deps column in conllu file and adding extra lines for punctuations and concatenated morphs.

#This function opens a file and creates a list of sentences. To run, write: f = 'x', new_sentences_list(f).
def new_sentences_list(filename):
    conllu_file = open(filename, 'r', encoding='utf-8')
    data = conllu_file.read()
    parsed_data = parse(data)
    sentences = [a_sentence for a_sentence in parsed_data]
    return sentences


#This function fills the deps column in the conllu file.
def fill_deps_in(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int):
            word['deps'] = f"{word['head']}:{word['deprel']}"


#The following function moves various counters  (morph_y, word_y) forward and resets test strings (accalt and acc)

def iteratorformorphs(morph_y, word_y, j, acc, accalt=None):

    morph_y = j+1
    accalt=''
    acc=''
    word_y +=1

    return morph_y, word_y, acc


#The following function combines the iteratorformorphs functionality with conditional statements that test whether certain
#counters are the same. The first conditional is the simple case for most concatenations. The second conditional is used
#whenever for certain exceptional cases which otherwise would fail to meet the criteria for concatenations. It is used especially
#for when a punctuation mark is found in the text string that is not in the list of morphs.

def tijappend(morph_y, tij, word_y, j, morphs, acc, accalt=None):

    if morph_y != j:

        tij.append((word_y, morph_y+1, j+1)) # a concatenated string is formed

    elif morph_y == j and acc != morphs[j]:

        tij.append((word_y, morph_y+2, j+1))

    #Consider replacing the following with the iteratorformorphs function.
    morph_y = j+1 # moves on to the next morph
    accalt = ''
    acc = '' # resets the accumulated string
    word_y += 1 # moves on to the next word

    return morph_y, word_y, acc, tij


#The following function iterates over morphs in a list of morphs and words in text string and tests whether an accumulated string made up of one or more of the morphs is the same a word in the
#text string. There are various exceptional cases that are also dealt with if the accumulated string does not match a word.

def check_concatenations3(list_of_words, list_of_morphs, sentence):

    words = [re.sub("[^0-9a-zA-Z_À-ÿ]+", '', x) for x in list_of_words] # uses the regex library to remove all non-alphanumeric characters before comparison
    morphs = [re.sub("[^0-9a-zA-Z_À-ÿ]+", '', x[0]) for x in list_of_morphs] # "
    word_y = 0 # iterator
    morph_y = 0 # "
    tij = [] # initialization
    accumulated = '' # empty accumulated string
    currentact = []

    for j in range(len(morphs)): # loops over every morph

        accumulated += morphs[j]
        currentact.append(({'accumulated':accumulated, 'current_morph':morphs[j], 'currentword':words[word_y], 'word_y':word_y, 'morph_y':morph_y, 'j':j})) #This keeps track of all the morphs and words that pass through the iterator.

        if accumulated.casefold() == words[word_y].casefold(): # Test to see if a concatenated string matches a word in a sentence.

            morph_y, word_y, accumulated, tij = tijappend(morph_y, tij, word_y, j, morphs, accumulated)

        elif accumulated.casefold() != words[word_y].casefold(): # Introduces various tests if no match is found.

            if len(accumulated.casefold()) <= len(words[word_y].casefold()) - 2: #This is the most general case of no match.
                pass

            elif j+1 < len(morphs) and (morphs[j+1] != 'n' or morphs[j+1] != 'm') and (accumulated == 'inna' or accumulated == 'na' or accumulated == 'a'): #Nasalizing Test

                accumulated1 = accumulated + 'n' #is this strictly necessary?
                accumulated2 = accumulated + 'm' #is this strictly necessary?

                morph_y, word_y, accumulated = iteratorformorphs(morph_y, word_y, j, accumulated1, accumulated2)

            elif accumulated.startswith('nd') or accumulated.startswith('ng') or accumulated.startswith('mb'): #Nasalized Test

                accumulated3 = accumulated[1:] #is this strictly necessary?

                morph_y, word_y, accumulated = iteratorformorphs(morph_y, word_y, j, accumulated3)

            elif 'ss' in accumulated: #Copula Test

                accumulated4 = 'i' + accumulated[2:]

                if accumulated4.casefold() == words[word_y].casefold():

                    morph_y, word_y, accumulated, tij = tijappend(morph_y, tij, word_y, j, morphs, accumulated4)

            elif words[word_y].endswith('s'): #Trailing s Test

                accumulated5 = accumulated + 's' #is this strictly necessary?

                morph_y, word_y, accumulated = iteratorformorphs(morph_y, word_y, j, accumulated5)

            elif accumulated.startswith('s') and words[word_y] == accumulated[1:]: #Prefixed s Test

                accumulated6 = accumulated[1:] #is this strictly necessary?

                morph_y, word_y, accumulated = iteratorformorphs(morph_y, word_y, j, accumulated6)

            elif words[word_y] == 'rp' or words[word_y] == 'pp' or words[word_y] == 'cp': #Tests to see if the current word is a punctuation mark.

                punctuation = {'id' : morph_y+1, 'form' : words[word_y], 'lemma' : words[word_y], 'upos' : 'PUNCT', 'xpos' : 'punctuation'} #Prepares a conllu-version of a punctuation mark
                sentence.insert(morph_y, punctuation) #Inserts punctuation marks into the sentence.

                if accumulated == words[word_y+1]: #Tests whether the accumulated morphs are the same as the next word. This is necessary because the accumulated morph will never correspond to the current word, which is the punctuation mark.
                    morph_y = j+1
                    word_y += 2
                    accumulated = ''
                elif accumulated != words[word_y+1]: #Tests whether the accumulated morph is not the same as the next word. This might happen if the next word is a new chunk (a concatenated string of words).
                    morph_y = j+1
                    word_y += 1

    return tij, currentact

#The above function does not add trailing punctuation. It's probably because they are beyond range(len(morphs)).
#There is still some issue with sentence count 67. There are also data problems in count 58, 52, 47, 46, 29.


#The following function finds punctuation marks in a text string.

def getpunct(sent):

    sentencestring = sent.metadata['text'] #Gets the text string.
    punctlist = [('.', 'p'), (',', 'c'), ('·', 'r')] #The list of main punctuation marks and their alphanumeric "equivalent".
    newstring = re.sub(' ([.,·]) ', r' \1punct ', sentencestring) #Substitutes the punctuation marks in a string with interim alphanumeric characters for search purposes.
    finallist = []

    for w in newstring.split(): #Iterates through a string

        if w.endswith('punct'): #Finds punctuation marks

            wstart = w[:-5] #Gets rid of the interim marker of punctuation (i.e. "punct")

            for p in punctlist: #Goes through the list of punctuation marks

                if p[0] == wstart: #Checks if the current punctuation mark in the text string is the same as the current item in the list of punctuation marks.

                    w = p[1] + 'p' #Creates a alphanumeric version of the punctuation mark.

        finallist.append(w) #Creates a list of words which includes the alphanumeric versions of punctuation marks.

    return finallist


#The following function goes through the list of sentences and inserts chunks (concatenated strings).

def insert_chunks(sent):

    cnt = 1
    list_of_words = None
    list_of_morphs = []

    for word in sent:

        list_of_words = getpunct(sent) #Creates a list of words with alphanumeric versions of punctuation marks.
        list_of_morphs.append((word['form'], word['id'])) #Creates a list of morphs.

    tij, currentact = check_concatenations3(list_of_words, list_of_morphs, sent)

    for word in sent:

        if tij != []:

            t, i, j = tij[0]

            if cnt == i:

                cdict={'id': (i, '-', j), 'form': list_of_words[t]}
                sent.insert(i-1, cdict) #Inserts concatenated strings.
                tij.pop(0)

        cnt += 1

    return currentact


#The following function creates interim ids for newly added concatenated string. This is necessary because concatenated strings always have a tuple as an id but this is not conducive to comparison
#with the original morphs in a list of morphs which have integer ids. The specific comparison that needs ids to be integers is the sorting function below.

def reassignids(sent):

    for word in sent:

        if isinstance(word['id'], tuple):

            word['interim'] = word['id']
            word['id'] = word['id'][0]

    return


#The following function finds the id number for a morph in a list of morphs.

def get_id(word):
    return word.get('id')


#The following function uses the id numbers of morphs in a list of morphs to sort the list into numeric ascending order .

def sortsent(sent):
    return sent.sort(key=get_id)


#The following function iterates through morphs in a list of morphs to find concatenated morphs and their component parts.
#The point of this to ensure that the concatenated morphs are actually in the right place in the sentence. There could be occasions where a concatenated morph has been
#inserted into the wrong place and will need to be shifted.

def checkchunkorder(sent):

    chunk=[] #This will be a list consisting of the concatenated morph and its supposed subelements.
    allchunks=[] #This will be a list consisting of all the concatenated morphs and their subelements in a sentence.
    dif = None #A counter.

    for word in sent:

        if word.get('interim'): #Gets morphs that are concatenated morphs - only concatenated morphs have the key "interim" because of the reassignids function.

            dif = abs(word['interim'][2] - word['interim'][0]) #Assigns the difference between the two parts of interim to the counter. The two parts of interim define a range of elements that ought to be subparts of the concatenated morphs. The difference between the two can be used to tell the iterator how many words to add to the chunk list.
            chunk.append(word) #Adds the concatenate morph to the chunk list.

        elif dif != None and dif >= 0 and not word.get('interim'): #Checks whether the counter is an integer and if it is larger than or equal to 0 and if the current word is a normal morph.

            dif -= 1 #Decreases the counter
            chunk.append(word) #Appends the word to the chunk list.

            if dif < 0: #Checks if the counter is less than 0. This means that the range of words for a given chunk has already been looked at.

                allchunks.append(chunk) #Appends the chunk list (consisting of the concatenated morph and its subelement) to the list of all chunks in a sentence.
                chunk = [] #Empties the current chunk. #consider also adding dif == None here?

        elif dif == None: #If an integer has not been assigned to the counter, then there is no need to add anything to a chunk list. This happens if there are no chunks in a given stretch of the list.

            pass

    return allchunks


#The following function will use the information gathered in the previous function to change the order of stray concatenate morphs.

def changechunkorder(allchunks, sentence):

    lastid = None #The id of the last subelement of a chunk.
    searchlen = None
    badindex = None

    for chunk in allchunks:  #Iterates through the list of all the chunks in a sentence

        accumulated, firstword, *_, lastword = chunk #Assigns the subelements of a chunk to various variables.

        accumulated_string = re.sub("[^0-9a-zA-Z_À-ÿ]+", '', str(accumulated['form'])) #Makes an alphanumeric test string out of the various variables
        firstword_string = re.sub("[^0-9a-zA-Z_À-ÿ]+", '', str(firstword['form']))
        lastword_string = re.sub("[^0-9a-zA-Z_À-ÿ]+", '', str(lastword['form']))

        if firstword_string not in accumulated_string and lastword_string not in accumulated_string: #Finds chunks that are not really chunks; basically if the first morph in the chunk is not in the accumulated string (the concatenated morph) and the last morph in the chunk is not in the accumulated string, this is a false chunk. The accumulated string will need to be shifted to the position where its subelements actually are in the sentence.

            lastid = chunk[0]['interim'][2] #Assigns the final element of the interim id to lastid. #consider changing to "accumulated".
            badindex = sentence.index(chunk[0]) #Gets the current location of the accumulated string in the sentence — Note that this is the wrong location. #consider changing to "accumulated".
            searchlen = len(chunk)-2 #Sets a search length. Basically this will be used to find the first submember of a concatenated morph.

        else:

            pass

    for cnt, word in enumerate(sentence): #Goes through morphs in a sentence.

        if  word['id'] == lastid: #Finds the final submember of a concatentated morph

            firstid = sentence.index(sentence[cnt-searchlen]) #Gets the id of the first submember of a concatenated morph.
            newword = sentence.pop(badindex) #Removes the wrongly placed concatenated morph from the sentence.
            sentence.insert(firstid, newword) #Reinserts the concatenated into the sentence.

            break #Ends the loop.

        else:

            pass

def changepunct(sent):
    
    punctlist = [('.', 'pp'), (',', 'cp'), ('·', 'rp')]
    
    for w in sent:

        if w['upos'] == 'PUNCT':

            for p in punctlist:
                
                if w['form'] in p[1]:
                    
                    w['form'] = p[0]
                    w['lemma'] = p[0]


#The following function changes ids of morphs in the sentence. This is necessary because sentences might have a newly inserted punctuation mark that messes up the original id numbers.

def changeid(sent):
    #Remember to replace with original punctuation after changings ids.
    
    punctseen=[] #A list of the punctuation marks that have been seen by the loop.
    headseen=[] #remember to remove

    for c, w in enumerate(sent): #Goes through morphs in a sentence.

        if punctseen == []: #Checks whether no punctuation marks have been seen yet.

            if w['upos'] != 'PUNCT': #If the current word is not a punctuation mark

                if isinstance (w['head'], int):
                    currenthead = [w['head'], w['head']]
                    headseen.append(currenthead) #Adds the current head (a pair consisting of the word's head value twice) to the list of heads.
                    
            elif w['upos'] == 'PUNCT': #If the current word is a punctuation mark

                changepunct(sent) 
                punctseen.append(w) #Add the punctuation mark to the list of punctuation marks.

        elif punctseen != []: #Checks if at least one punctuation mark has been seen.

            if len(punctseen) >= 1 and isinstance(w['id'], int): #Consider removing isinstance.
                
                if w['upos'] == 'PUNCT':

                    w['id'] += len(punctseen)
                    changepunct(sent)
                    punctseen.append(w)

                elif w['upos'] != 'PUNCT':
                    
                     w['id'] += len(punctseen)

                     if isinstance(w['head'], int) and w['head'] < punctseen[0]['id']: #Checks to see if the head is before the first punctuation mark.

                        currenthead = [w['head'], w['head']]
                        headseen.append(currenthead)
                        
                     elif isinstance(w['head'], int) and w['head'] >= punctseen[0]['id']: #Checks to see if the head is after the first punctuation mark.

                         for head in headseen:

                             if w['head'] == head[0]: #If the head of the current word is already in the list of heads
                                 
                                 w['head'] = head[1] #Change the head of the current word to the second value in the current head pair, where the head pair = value 1,value2.
                                 break
                                
                             elif w['head'] != head[0] and w['head'] >= headseen[-1][0]: #If the head of the current word is not in the list of heads and it is larger than value of the first member of the last pair in the list of heads.
                                                                                        #This ensures that current word's head value is sequentially after all of the heads in the list of heads.
                                 newhead = [w['head'], w['head'] + len(punctseen)]      #The new head pair is the old head value of the current word and that plus the current length of punctseen.
                                 w['head'] = newhead[1]                                 #The new head value of the current words is the second member of the pair defined in newhead.
                                 headseen.append(newhead)                               #newhead is added to the list of heads.
                                 break

                             elif w['head'] != head[0] and w['head'] < headseen[-1][0]: #This checks to see if the head of the current word is sequentially before all of the heads in the list of heads.

                                 for p in punctseen:                                    #Goes through punctseeen.

                                     if p['id'] >= w['head']:                            #Finds a punctuation mark with an id greater than the head of the current word.

                                        newhead = [w['head'], w['head'] + (punctseen.index(p) + 1)] #Makes the new head a pair
                                        w['head'] = newhead[1]
                                        headseen.append(newhead)
                                        break

                                     elif p['id'] < w['head']:

                                        newhead = [w['head'], w['head'] + len(punctseen)]
                                        w['head'] = newhead[1]
                                        headseen.append(newhead)
                                        break

                                 break
                                 
    return sent, punctseen, headseen #remember to remove headseen

def changechunkids(sent):
    chunks = checkchunkorder(sent)
    for chunk in chunks:
        chunk[0]['id'] = (chunk[1]['id'], '-', chunk[-1]['id'])
        del chunk[0]['interim']

def testing(sent):
    accumulatedlist = insert_chunks(sent)
    reassignids(sent)
    sortsent(sent)
    allchunks=checkchunkorder(sent)
    changechunkorder(allchunks, sent)
    sent,punctseen,headseen=changeid(sent)
    changechunkids(sent)
    return accumulatedlist,allchunks,punctseen,headseen
    
def automate_insertion(list_of_sentences):

    for sent in list_of_sentences:

        accumulatedlist = insert_chunks(sent)
        reassignids(sent)
        sortsent(sent)
        allchunks=checkchunkorder(sent)
        changechunkorder(allchunks, sent)
        sent,punctseen,headseen=changeid(sent)
        changechunkids(sent)

    return list_of_sentences, accumulatedlist


def do_all(fileout, list_of_sentences):

    automate_insertion(list_of_sentences)
    [fill_deps_in(sent) for sent in list_of_sentences]

    with open(fileout, 'w', encoding='utf-8') as file_out:

        conllu_sentences = [item.serialize() for item in list_of_sentences]
        [file_out.write(item) for item in conllu_sentences]

    return list_of_sentences

if __name__ == "__main__":

    do_all(sys.argv[2], new_sentences_list(sys.argv[1])) ### CHANGE!


# ========================================================================================================================================================================================================

# Part 2. Currently Unused Functions.

#Note the following functions assume that the function assign_value_to_definite has already been applied to the data.
#Note too that the functions assume that the head/deprel columns have been tagged.
#Also, it may be possible to tweak this functoin a bit to create a parser that assigns the index of a noun within the sentence list to the head column for a det.
def build_list_of_nouns_and_det_in(a_sentence):
    list_of_nouns = []
    list_of_dets = []
    for word in a_sentence:
        if word['upos'] == 'NOUN':
            list_of_nouns.append(word)
        elif word['upos'] == 'DET':
            list_of_dets.append(word)
    return list_of_nouns, list_of_dets

def assign_def_to_noun_in(list_of_sentences):
    for count, sent in enumerate(list_of_sentences):
        nouns, dets = build_list_of_nouns_and_det_in(sent)
        for noun, det in list(itertools.product(nouns, dets)):
            if det['feats'].get('Definite') and noun['id'] == det['head']:
                print(f"The noun '{noun}' in sentence {count+1} is definite because it is associated with the article '{det}'.")#Replace this with an assignment.

# This function might help to figure out if a word is mutated.

def mutation_finder(sentence_num, a_sentence):
    for word in a_sentence:
        if word['form'].startswith('ch') or word['form'].startswith('th') or word['form'].startswith('ph'):
            print(f"{word} in sentence {sentence_num+1} is lenited!")
        elif word['form'].startswith('ng') or word['form'].startswith('nd') or word['form'].startswith('mb'):
            print(f"{word} in sentence {sentence_num+1} is eclipsed!")
        elif word['form'].startswith('nn') or word['form'].startswith('ll') or word['form'].startswith('rr'):
            print(f"{word} in sentence {sentence_num+1} is geminated!")


# ========================================================================================================================================================================================================
# Part 3: Functions that have already been moved into current_conllu_maker.py


# **********************************
#3.1 Functions to change feats dict.


#This function analyses prepositions and possessives.
#Note that this could be expanded to cover all pronouns.
def analyze_person_in_prepositions_and_possessives_in_(a_sentence):
    for word in a_sentence:
        for key in word["feats"].copy().keys():
            if word["xpos"] == "preposition" or word["xpos"] == "pronoun_possessive" or word["xpos"] == "particle_pronominal":
                if "1" in key:
                    word["feats"]["Person"] = "1"
                elif "2" in key:
                    word["feats"]["Person"] = "2"
                elif "3" in key:
                    word["feats"]["Person"] = "3"

#This function analyses prepositions and possessives.
#Note that this could be expanded to cover all pronouns.
def analyze_number_in_prepositions_and_possessives_in_(a_sentence):
    for word in a_sentence:
        for key in word["feats"].copy().keys():
            if word["xpos"] == "preposition" or word["xpos"] == "pronoun_possessive" or word["xpos"] == "particle_pronominal":
                if "sg." in key:
                    word["feats"]["Number"] = "Sing"
                elif "pl." in key:
                    word["feats"]["Number"] = "Plur"

def analyze_gender_in_prepositions_and_possessives_in_(a_sentence):
    for word in a_sentence:
        for key in word["feats"].copy().keys():
            if word["xpos"] == "preposition" or word["xpos"] == "pronoun_possessive" or word["xpos"] == "particle_pronominal":
                if "masc." in key:
                    word["feats"]["Gender"] = "Masc"
                elif "fem." in key:
                    word["feats"]["Number"] = "Fem"
                elif "neut." in key:
                    word["feats"]["Number"] = "Neut"

def analyze_subcat_in_(a_sentence):
    for word in a_sentence:
        for key in word["feats"].copy().keys():
            if ".trans." in key:
                word["feats"]["Subcat"] = "Trans"
            elif ".intrans." in key:
                word["feats"]["Subcat"] = "Intrans"

def analyze_object_pron_in_(a_sentence):
    for word in a_sentence:
        if word["feats"].copy().get("Person[Obj]"):
            for key in word["feats"].copy().keys():
                if ".A" in key:
                    word["feats"]["PronType"] = "InfA"
                elif ".B" in key:
                    word["feats"]["PronType"] = "InfB"
                elif ".C" in key:
                    word["feats"]["PronType"] = "InfC"

def analyze_augm_in_(a_sentence):
    for word in a_sentence:
        for key in word["feats"].copy().keys():
            if "augm." in key:
                word["feats"]["Aspect"] = "Perf"

def analyze_voice_in_(a_sentence):
    for word in a_sentence:
        for key in word["feats"].copy().keys():
            if word["xpos"] == "verb" and "pass" in key:
                word["feats"]["Voice"] = "Pass"
            elif word["xpos"] == "verb" and "pass" not in next(iter(word["feats"])):
                word["feats"]["Voice"] = "Act"

def analyze_rel_in(a_sentence):
    for word in a_sentence:
        for key in word["feats"].copy().keys():
            if "rel" in key:
                if "len" in key:
                    word["feats"]["RelType"] = "Len"
                elif "nas" in key:
                    word["feats"]["RelType"] = "Nas"
                elif "len" not in next(iter(word["feats"])) or "nas" not in next(iter(word["feats"])):
                    word["feats"]["RelType"] = "Other"

def fix_verbs(list_of_sentences):
    [analyze_subcat_in_(sent) for sent in list_of_sentences]
    [analyze_object_pron_in_(sent) for sent in list_of_sentences]
    [analyze_augm_in_(sent) for sent in list_of_sentences]
    [analyze_voice_in_(sent) for sent in list_of_sentences]
    [analyze_rel_in(sent) for sent in list_of_sentences]

#This function deletes keys with null values in the "feats" dictionary.
#What to do with the "No_Features=_" or the "_" case?
def delete_null_values_in(a_sentence):
    x = "No_Features"
    for word in a_sentence:
        if word["feats"] is not None:
            for key, value in word["feats"].copy().items():
                if x != key and word["feats"][key] is None:
                    del word["feats"][key]


# ************************************
# 3.2 Functions to change assign upos.


#The following functions (assign_upos and upos_finder) assign upos to a word in a sentence in a list of sentences.
def assign_upos(combined_list):
    for count, word in enumerate(combined_list):
        if combined_list[count][0]['xpos'] in combined_list[count][1]:
            for key, value in combined_list[count][1].items():
                combined_list[count][0]['upos'] = value

#Run this after analysing deprel (see next section).
#Note that particle_interrogative has two upos assignments!
def upos_finder(list_of_sentences):
    upos_list = [{'adjective': 'ADJ'}, {'adjective_numeral': 'NUM'}, {'adjective_numeral_noun': 'ADJ'}, {'adective_pronominal': 'DET'},
     {'noun': 'NOUN'}, {'noun_numeral': 'NUM'}, {'numeral': 'NUM'}, {'adverb': 'ADV'}, {'complementizer': 'SCONJ'},
     {'definite_article': 'DET'}, {'focus_particle': 'PART'}, {'interjection': 'INTJ'}, {'pronoun_independent': 'PRON'},
     {'pronoun_infixed': 'PRON'}, {'pronoun_infix': 'PRON'}, {'pronoun_possessive': 'DET'}, {'pronoun_propword': 'PRON'},
     {'pronoun_quantifier': 'PRON'}, {'pronoun_relative': 'PRON'}, {'proper_noun': 'PROPN'}, {'verb': 'VERB'},
     {'verbal_participle': 'ADJ'}, {'particle_anaphoric': 'PRON'}, {'particle_augment': 'PART'}, {'particle_comparative': 'SCONJ'},
     {'particle_demonstrative_distal': 'DET'}, {'particle_demonstrative_proximate': 'DET'}, {'particle_interrogative': 'PART'},
     {'particle_numerative': 'PART'}, {'particle_pronominal': 'PRON'}, {'particle_vocative': 'PART'}, {'preposition': 'ADP'},
     {'pronoun_anaphoric': 'PRON'}, {'pronoun_demonstrative_distal': 'PRON'}, {'particle_interrogative': 'PRON'}, {'particle_negative_main': 'PART'},
     {'particle_negative_subordinate': 'PART'}, {'auxiliary': 'AUX'}, {'pronoun_demonstrative_proximate': 'PRON'}, {'particle_discourse': 'ADV'},
     {'verbal_noun': 'NOUN'}, {'abbreviation': 'CCONJ'}, {'particle_preverb': 'SCONJ'}, {'adjective_quantifier': 'DET'},
     {'pronoun_emphatic': 'PRON'}, {'particle_focus': 'PART'}]
    for sent in list_of_sentences:
        combo = list(itertools.product(sent, upos_list))
        assign_upos(combo)


#The following function checks to see whether a word has been assigned a upos.
def upos_is_x(list_of_sentences):
    for count, a_sentence in enumerate(list_of_sentences):
        for word in a_sentence:
            if word['upos'] == 'X':
                print(f"The word '{word}' which has xpos '{word['xpos']} in sentence number {count+1} has no upos.")


# ********************************************************************
# 3.3. The following functions fill deprel for various function words:


def analyse_copula(a_sentence):
    for word in a_sentence:
        if word["lemma"] == "is 1":
            word["upos"] = "AUX" #Changes the upos of the copula
            word["deprel"] = "cop"

def analyse_article(a_sentence):
    for word in a_sentence:
        if word["lemma"] == "in 1":
            word["deprel"] = 'det'

def analyse_prep(a_sentence):
    for word in a_sentence:
        if word["xpos"] == "preposition" and not word["feats"].copy().get("Person"):
            word["deprel"] = "case" #This assigns case even to potential mark:prt with verbal nouns.

def analyse_number(a_sentence):
    for word in a_sentence:
        if word["xpos"] == "adjective_numeral":
           word["deprel"] = "nummod"

def analyse_abbreviation(a_sentence):
    for word in a_sentence:
        if word["lemma"] == ".i.":
            word["xpos"] = "abbreviation"
            word["upos"] = "CCONJ"
            word["deprel"] = "cc"

def analyse_negation(a_sentence):
    for word in a_sentence:
        if word["xpos"] == "particle_negative_main" or word["xpos"] == "particle_negative_subordinate":
           word["deprel"] = "advmod:neg"

def analyse_complementiser(a_sentence):
    for word in a_sentence:
        if word["xpos"] == "complementiser" or word['lemma'] == 'no·':
            word["deprel"] = "mark:prt"
            word["upos"] = 'SCONJ'

def analyse_coordconj(combined_list):
    for count, word in enumerate(combined_list):
        if combined_list[count][1] in combined_list[count][0]['lemma'] and combined_list[count][0]['xpos'] == "conjunction":
            combined_list[count][0]['deprel'] = 'cc'
            combined_list[count][0]['upos'] = 'CCONJ'

def coordconj_finder(list_of_sentences):
    cconjlist = ["ocus 2", "nó 1", "ná 4", "fa", "nach 6", "rodbo", "et", "uel"]
    for a_sentence in list_of_sentences:
        combo = list(itertools.product(a_sentence, cconjlist))
        analyse_coordconj(combo)

def analyse_subconj(combined_list):
    for count, word in enumerate(combined_list):
        if combined_list[count][1] in combined_list[count][0]['lemma'] and combined_list[count][0]['xpos'] == "conjunction":
            combined_list[count][0]['deprel'] = 'mark'
            combined_list[count][0]['upos'] = 'SCONJ'

def subconj_finder(list_of_sentences):
    sconjlist = ["amail 2", "ar 2", "a 6", "cía 2", "dég 2", "resíu", "úaire", "ma", "ó 2", "ol 2"]
    for a_sentence in list_of_sentences:
        combo = list(itertools.product(a_sentence, sconjlist))
        analyse_subconj(combo)

def do_all_deprel(list_of_sentences):
    [analyse_copula(a_sentence) for a_sentence in list_of_sentences]
    [analyse_article(a_sentence) for a_sentence in list_of_sentences]
    [analyse_prep(a_sentence) for a_sentence in list_of_sentences]
    [analyse_abbreviation(a_sentence) for a_sentence in list_of_sentences]
    [analyse_negation(a_sentence) for a_sentence in list_of_sentences]
    [analyse_number(a_sentence) for a_sentence in list_of_sentences]
    [analyse_copula(a_sentence) for a_sentence in list_of_sentences]
    [analyse_complementiser(a_sentence) for a_sentence in list_of_sentences]
    subconj_finder(list_of_sentences)
    coordconj_finder(list_of_sentences)


# ***********************************************************************
# 3.4. Functions to assign more values to the features in the feats dict.


def assign_value_to_definite(a_sentence):
    for word in a_sentence:
        if word['xpos'] == 'definite_article':
            word['feats']['Definite'] = 'Def'

def assign_value_to_poss(a_sentence):
    for word in a_sentence:
        if word['xpos'] == 'pronoun_possessive':#Remember to also add pronoun_independent here if the analysis is genitive.
            word['feats']['Poss'] = 'Yes'

def assign_value_to_deixis(a_sentence):
    for word in a_sentence:
        if word['xpos'] == 'pronoun_demonstrative_distal' or word['xpos'] == 'particle_demonstrative_distal':
            word['feats']['Deixis'] = 'Remt'
        elif word['xpos'] == 'pronoun_demonstrative_proximate' or word['xpos'] == 'particle_demonstrative_proximate':
            word['feats']['Deixis'] = 'Prox'

def assign_value_to_prontype(a_sentence):
    for word in a_sentence:
        if word['xpos'] == 'pronoun_independent' or word['xpos'] == 'pronoun_possessive' or word['xpos'] == 'pronoun_suffixed' or word['xpos'] == 'pronoun_infixed' or word['xpos'] == 'particle_pronominal':
            word['feats']['PronType'] = 'Prs'
        elif word['xpos'] == 'definite_article':
            word['feats']['PronType'] = 'Art'
        elif word['xpos'] == 'pronoun_relative':
            word['feats']['PronType'] = 'Rel'
        elif word['xpos'] == 'pronoun_emphatic':
            word['feats']['PronType'] = 'Emp'
        elif word['lemma'] == 'cach' or word['lemma'] == 'cách':
            word['feats']['PronType'] = 'Tot'
        elif word['lemma'] == 'nech' or word['lemma'] == 'nach 1':
            word['feats']['PronType'] = 'Ind'
        elif word['xpos'] == 'pronoun_demonstrative_proximate' or word['xpos'] == 'pronoun_demonstrative_distal':
            word['feats']['PronType'] = 'Dem'

def assign_person_to_pronouns(a_sentence):
    for word in a_sentence:
        if 'pron' in word['lemma'] and word['xpos'] == 'pronoun_independent' or word['xpos'] == 'pronoun_possessive':
            if '1' in word['lemma']:
                word['feats']['Person'] = '1'
            elif '2' in word['lemma']:
                word['feats']['Person'] = '2'
            elif '3' in word['lemma']:
                word['feats']['Person'] = '3'

#The following functions assign a value to the feature Case for prepositions:

def case_finder(list_of_sentences):
    prep_list=[{'a 7': 'Dat'}, {'acht 2': 'Acc'}, {'al': 'Acc'}, {'amail 1': 'Acc'}, {'ar 1': 'Acc/Dat'}, {'cen': 'Acc'}, {'cenmothá': 'Acc'}, {'co 1': 'Acc'}, {'co 2': 'Dat'}, {'co·rrici': 'Acc'}, {'co·rrici': 'Acc'}, {'coticci': 'Acc'}, {'di': 'Dat'}, {'do 1': 'Dat'}, {'dochumm': 'Gen'}, {'echtar': 'Acc'}, {'eter': 'Acc'}, {'fíad': 'Dat'}, {'fo': 'Acc/Dat'}, {'for': 'Acc/Dat'}, {'fri': 'Acc'}, {'fri': 'Acc'}, {'íar 1': 'Dat'}, {'íarmithá': 'Dat'}, {'imm': 'Acc'}, {'i': 'Acc/Dat'}, {'ingé 1': 'Acc'}, {'ís 1': 'Dat'}, {'la': 'Acc'}, {'ó 1': 'Dat'}, {'oc': 'Dat'}, {'ós 1': 'Dat'}, {'óthá': 'Dat'}, {'re': 'Dat'}, {'sech 1': 'Acc'}, {'tar 1': 'Acc'}, {'tre': 'Acc'}]
    for sent in list_of_sentences:
        combo = list(itertools.product(sent, prep_list))
        assign_case(combo)

def assign_case(combined_list):
    for count, word in enumerate(combined_list):
        if combined_list[count][0]['upos'] == 'ADP' and combined_list[count][0]['lemma'] in combined_list[count][1]:
            for key, value in combined_list[count][1].items():
                combined_list[count][0]['feats']['Case'] = value


# ********************************************************************
# 3.5. Putting it all together.


def assign_all_values(filename2, list_of_sentences):
    fix_verbs(list_of_sentences)
    upos_finder(list_of_sentences)
    [assign_value_to_definite(sent) for sent in list_of_sentences]
    [assign_value_to_deixis(sent) for sent in list_of_sentences]
    [assign_value_to_poss(sent) for sent in list_of_sentences]
    [assign_value_to_prontype(sent) for sent in list_of_sentences]
    [assign_person_to_pronouns(sent) for sent in list_of_sentences]
    [analyse_copula(sent) for sent in list_of_sentences]
    [analyze_gender_in_prepositions_and_possessives_in_(sent) for sent in list_of_sentences]
    [analyze_number_in_prepositions_and_possessives_in_(sent) for sent in list_of_sentences]
    [analyze_person_in_prepositions_and_possessives_in_(sent) for sent in list_of_sentences]
    [analyse_negation(sent) for sent in list_of_sentences]
    [fill_deps_in(sent) for sent in list_of_sentences]
    case_finder(list_of_sentences)
    [delete_null_values_in(sent) for sent in list_of_sentences] #Add to this something to delete "No_Features".
    with open(filename2, 'w', encoding='utf-8') as file_out:
        conllu_sentences = [item.serialize() for item in list_of_sentences]
        [file_out.write(item) for item in conllu_sentences]


# ========================================================================================================================================================================================================

# Part 4. Outline for this file going forward:
# Essentially the only functions that need to be carried forward are new_sentences_list(), fill_deps_in_(), a modified version of do_all(),
# and a modified version of the assign_def_to_noun() function (along with build_a_list_of_nouns_and_dets_in().
# Functions to change the Case feature of prepositions and to deal with No_Features are probably useful going forward.
