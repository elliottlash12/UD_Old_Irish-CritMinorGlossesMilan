#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Fri May 7 2021
Updated Mon Sep 7 2021
@author elliottlash
DFG project
Georg-August-Universität Göttingen
Sprachwissenschaftliches Seminar
"""

import csv
import itertools
import re
import sys
from collections import OrderedDict
from conllu import parse
from io import open

# ========================================================================================================================================================================================================
# ========================================================================================================================================================================================================
#
#
#****************** About the project ******************
#*******************************************************
#
#
# This python script takes a csv file which is the result of a search on the CorPH database (https://chronhib.maynoothuniversity.ie/chronhibWebsite/dashboard) and creates a CONLLU file which can be
# parsed using the Universal Dependencies tagging system (https://universaldependencies.org/#language-).
#
#
# The csv file draws data from the Morphology, Lemmata, and Sentences tables of CorPH. The following columns in these tables are used:
#
#                       |                       Morphology Table Columns                      |   Lemmata Table Columns |  Sentences Table Columns  |
#                       | ID, Text_Unit_ID, Stressed_Unit, Morph, Lemma, Analysis, Rel, Trans | Part_Of_Speech, Meaning | Textual_Unit, Translation |
#
#
# To run this script put it in a folder with the csv file and use Terminal (on a Mac). Navigate to the directory with the python script and the csv file.
# Then type the following at the commandline:
#
#                       python3 name_of_py_script name_of_csv_file name_of_interim_output_file name_of_final_output_file
#
#
# If an interactive python session is required in order to test any function in this script, run this script in a python shell compatible with python 3.
# At the command line type first os.chdir('/path to file/') and then data_file='name_of_csv_file'. The variable name "data_file" can be used in the functions in Section 7 to read this file.
# Note that all of the libraries in the import statements above need to be installed.
#
# ========================================================================================================================================================================================================
# ========================================================================================================================================================================================================
#
#
#****************** Table of Contents *******************
#********************************************************
#
#
# Section 1. Functions to preprocess the data to change the contents of certain cells in various columns.
#
## Section 2. Functions to process the features of one word based on the features of another.
#
#    a. Functions to update the analysis of verbs based on the presence of relative particles.
#    b. Functions to update the analysis of verbs based on the presence of infixed pronouns.
#    c. Functions to remove sub-elements of compounds.
#
# Section 3. Functions to remove extraneous information.
#
# Section 4. Functions to convert the data to CONLLU format.
#
# Section 5. Functions to fill in the upos and deprels columns of a CONLLU file.
#
# Section 6. Automating the functions in Sections 1 - 5.
#
#
# ========================================================================================================================================================================================================
# ========================================================================================================================================================================================================

#Section 1: Functions to pre-processing the data to change the contents of certain cells in various columns
#********************************************************************************************************

# The function preprocess_1 replaces any null cells in the "Analysis" in CorPH with "No_Features".

def preprocess_1(input_data):
    for item in input_data:
        if item[5] == "":
            item[5] = "No_Features"


# The function preprocess_2 replaces Null or "No" in any column with "_".

def preprocess_2(input_data):
    for item in input_data:
        for i in range(len(item)):
            if item[i] == "" or item[i] == "No":
                item[i] = "_"


# The function preprocess_3 checks a cell in the "Rel" column of CorPH to see if it contains "Yes" and then modifies cells in the Analysis column by adding "rel."
# The function also replaces the contents of the cell in the "Rel" column with "_".

def preprocess_3(input_data):
    for item in input_data:
        if item[6] == "Yes" and ".rel." not in item[5]: #Perhaps also "Maybe" should trigger something like rel?
            item[5] += "rel."
        item[6] = "_"


# The function preprocess_4 checks a cell in the "Transitivity" column of CorPH to see if it contains either "trans." or "intrans." and then modifies cells in the Analysis column accordingly.
# The function also replaces the contents of the cell in the "Transitivity" column with "_".

def preprocess_4(input_data):
    for item in input_data:
        if item[7] == "trans." or item[7] == "intrans.":
            item[5] = item[5] + item[7]
        item[7] = "_"


# The function preprocess_5 removes redundant or ambiguous information from the "Meaning" column.

def preprocess_5(input_data):
    for item in input_data:
        for i in range(len(item)):
            if 'definite article' in item[i]:
                item[i] = item[i].replace(', definite article', '', 1)
            elif 'that ; substantivizing particle' in item[i]:
                item[i] = item[i].replace('that ; ', '', 1)
            elif '; perfective augment' in item[i]:
                item[i] = item[i].replace('; perfective augment', '', 1)
            elif  'the copula' in item[i]:
                item[i] = item[i].replace(', the copula', '', 1)


# The function preprocess_6 puts "Gloss=" before strings in the "Meaning" column.
#It is possible that what really needs to happen here is to make the string in the "Meaning" column into a value in a key:value pair with the key "Gloss".

def preprocess_6(input_data):
    for item in itertools.islice(input_data, 1, None):
        analysis = "Analysis="
        gloss = "Gloss="
        item[5] = analysis + item[5]
        item[9] = gloss + item[9]


#The following function combines the previous six pre-processing functions into one.
    
def preprocessing(input_data):
    preprocess_1(input_data)
    preprocess_2(input_data)
    preprocess_3(input_data)
    preprocess_4(input_data)
    preprocess_5(input_data)
    preprocess_6(input_data)
    return


#Section 2: Functions to process the features of one word based on the features of another
#*****************************************************************************************


# This function builds three lists for each sentence: one of verbs, one of relative particles, and one of infixed pronouns.

def build_list_of_verbs_and_associated_particles_in(a_sentence):
    list_of_verbs = []
    list_of_relparts = []
    list_of_prons = []
    list_of_dummy_preverbs = []
    for count, word in enumerate(a_sentence): #goes through each word in the sentence.
        if word['Part_Of_Speech'] == 'verb': #checks if the POS of the word is a verb.
            list_of_verbs.append(word) #adds the word to the list of verbs
        elif word['Part_Of_Speech'] == 'particle_relative': #checks if the POS of the word is a relative particle.
            list_of_relparts.append(word) #adds the word to the list of relative particles.
        elif word['Part_Of_Speech'] == 'pronoun_infixed': #checks if the POS of the word is a pronoun_infixed
            list_of_prons.append(word) #adds the word to the list of infixed pronouns.
        elif word['Part_Of_Speech'] == 'particle_preverb' and word['Lemma'] == 'no·':
            list_of_dummy_preverbs.append(word)
    return list_of_verbs, list_of_relparts, list_of_prons, list_of_dummy_preverbs

    
# The following functions compare a list of verbs to either a list of relative particles or a list of infixed pronouns.
# The analysis of the verb or pronoun is updated according to features of the relative particle/pronoun.
   

def compare_verbs_relative_particles_and_infixed_pronouns_in(list_of_verbs, list_of_relparts, list_of_prons):
    ans = []
    for verb, relpart, pron in list(itertools.product(list_of_verbs, list_of_relparts, list_of_prons)):
        if verb['Stressed_Unit'] == relpart['Stressed_Unit'] and relpart['Stressed_Unit'] == pron['Stressed_Unit']:
            if pron['Morph'] in verb['Morph']:
                if relpart['Lemma'] == 'len.rel.particle':
                    answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' is a lenited relative verb.'
                    ans.append(answ)
                    verb['Analysis'] += 'len'
                elif relpart['Lemma'] == 'nas.rel.particle':
                    answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' is a nasalized relative verb.'
                    ans.append(answ)
                    verb['Analysis'] += 'nas'
            elif pron['Morph'] not in verb['Morph']:
                if relpart['Lemma'] == 'len.rel.particle':
                    answ = 'The pronoun ' + pron['Morph'] + ' which has ID number ' + pron['ID'] + ' is a lenited class C pronoun.'
                    ans.append(answ)
                    pron['Analysis'] += '.len'
                elif relpart['Lemma'] == 'nas.rel.particle':
                    answ = 'The pronoun ' + pron['Morph'] + ' which has ID number ' + pron['ID'] + ' is a nasalized class C pronoun.'
                    ans.append(answ)
                    pron['Analysis'] += '.nas'
    return ans


def compare_verbs_and_relative_particles_in(list_of_verbs, list_of_relparts):
    ans = []
    for verb, relpart in list(itertools.product(list_of_verbs, list_of_relparts)):
        if verb['Stressed_Unit'] == relpart['Stressed_Unit']:
            if relpart['Lemma'] == 'len.rel.particle':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' is a lenited relative verb.'
                ans.append(answ)
                verb['Analysis'] += 'len'
            elif relpart['Lemma'] == 'nas.rel.particle':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' is a nasalized relative verb.'
                ans.append(answ)
                verb['Analysis'] += 'nas'
    return ans


def compare_verbs_and_infixed_pronouns_in(list_of_verbs, list_of_prons):
    ans = []
    for verb, pron in list(itertools.product(list_of_verbs, list_of_prons)): 
        if verb['Stressed_Unit'] == pron['Stressed_Unit'] and pron['Morph'] in verb['Morph']: #The second conjunct of this statement excludes cases where pron['Morph'] == '∅'!
            pronanalysis = pron['Analysis'].split('=')
            if pron['Lemma'] == '1sg.inf.pron.':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj1sg.' + pronanalysis[1] + '.'
            elif pron['Lemma'] == '2sg.inf.pron.':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj2sg.' + pronanalysis[1] + '.'
            elif pron['Lemma'] == '1pl.inf.pron.':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj1pl.' + pronanalysis[1] + '.'
            elif pron['Lemma'] == '2pl.inf.pron.':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj2pl' + pronanalysis[1] + '.'
            elif pron['Lemma'] == '3sg.masc.inf.pron.':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj3sg.masc.' + pronanalysis[1] + '.'
            elif pron['Lemma'] == '3sg.fem.inf.pron.':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj3sg.fem.' + pronanalysis[1] + '.'
            elif pron['Lemma'] == '3sg.neut.inf.pron.':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj3sg.neut.' + pronanalysis[1] + '.'
            elif pron['Lemma'] == '3pl.inf.pron.': 
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj3pl.' + pronanalysis[1] + '.'
    return ans


#This function deletes pronouns that are infixed between the first lexical preverb and the rest of the verb in compound verbs.
 
def remove_true_infixed_pronouns_in(sentence, list_of_verbs, list_of_pronouns):
    for verb, pron in list(itertools.product(list_of_verbs, list_of_pronouns)):
        if pron['Stressed_Unit'] == verb['Stressed_Unit']:
            if pron['Morph'] in verb['Morph']:
                sentence.remove(pron)
        #elif pron['Morph'] not in verb['Morph']:   >>> Only in interactive session
        #    print(f"{pron['Morph']} not deleted.") >>> Only in interactive session


#This function deletes the dummy preverb when it is not an intrinsic part of a compound verb in secondary tenses.

def remove_dummy_preverb_in(sentence, list_of_verbs, list_of_dummy_preverbs):
    for verb, prev in list(itertools.product(list_of_verbs, list_of_dummy_preverbs)):
        if prev['Stressed_Unit'] == verb['Stressed_Unit']:
            if verb['Morph'].startswith(prev['Morph']):
                sentence.remove(prev)
        #else:   >>> Only in interactive session
        #    print(f"{prev['Morph']} not deleted.") >>> Only in interactive session


#This function combines the function to build lists of verbs, relative particles and pronoun with the functions to compare these lists.
        
def look_for_relative_or_infixed_verbs_in_all(list_of_sentences):
    rel_answers = []
    pron_answers = []
    for count, sent in enumerate(list_of_sentences.values()): #Goes through each sentence.
        verbs, relparts, prons, prevs = build_list_of_verbs_and_associated_particles_in(sent) #Builds lists of verbs, relative particles, and pronouns.
        pron_answer = compare_verbs_and_infixed_pronouns_in(verbs, prons)
        if not prons:
            rel_answer = compare_verbs_and_relative_particles_in(verbs, relparts)
        else:
            rel_answer = compare_verbs_relative_particles_and_infixed_pronouns_in(verbs, relparts, prons) 
        remove_true_infixed_pronouns_in(sent, verbs, prons)
        remove_dummy_preverb_in(sent, verbs, prevs)
        rel_answers.append([count, rel_answer])
        pron_answers.append([count, pron_answer])
#    return rel_answers, pron_answers >>> Only in interactive sessions


# The following function removes sub-elements of compounds. It works if the rows are in the following order: element 1 > element 2 > compound.
def compound_detector(list_of_sentences):
    for sent in list_of_sentences.values():
        for count, word in enumerate(sent):
            if count+2 < len(sent):
                if sent[count]['Morph'] in sent[count+2]['Morph'] and ('compos.' in sent[count]['Analysis'] or sent[count]['Part_Of_Speech'] == 'particle_prefix'):
                    if sent[count+1]['Morph'] in sent[count+2]['Morph']:
                        sent.pop(count+1)
                    sent.pop(count)
                    
# ========================================================================================================================================================================================================


#Section 4: Functions to remove extraneous information
#*****************************************************


# This function removes relative particles and infixed pronouns since their information has now been incorporated into the analysis of the verb.

def remove_relative_particles_in(list_of_sentences):
    for sent in list_of_sentences.values():
        for i in reversed(range(len(sent))):
            word = sent[i]
            if word['Part_Of_Speech'] == 'particle_relative':
                del sent[i]

                
# This function removes preverbs and augments since this information is almost always incorporated into the verbal morph.

def remove_preverbs_in(list_of_sentences):
    for sent in list_of_sentences.values():
        for i in reversed(range(len(sent))):
            word = sent[i] 
            if word['Part_Of_Speech'] == 'particle_augment':
               del sent[i]
            elif word['Part_Of_Speech'] == 'particle_preverb' and word['Lemma'] != 'no·': 
               del sent[i] #This may remove too few preverbs. Specifically, some instances of no· should be removed.


# This function removes any word whose morph is '∅'. This is necessary for Univeral Dependencies tagging since only overt words are parsable.

def remove_null_in(list_of_sentences):
    for sent in list_of_sentences.values():
        for i in reversed(range(len(sent))):
            word = sent[i]
            if '∅' in word['Morph']:
                del sent[i]


# This function combines the above three functions.

def remove_all_extraneous_info_in(list_of_sentences):
    remove_relative_particles_in(list_of_sentences)
    remove_preverbs_in(list_of_sentences)
    remove_null_in(list_of_sentences)

# ========================================================================================================================================================================================================


#Section 5: Functions to automatically add an index to the "Head" column of a CONLLU file.
#*****************************************************************************************


def list_of_dets_and_nouns_in(a_sentence):
    list_of_dets = []
    list_of_nouns = []
    list_of_preps = []
    list_of_nominal_pos = ['noun', 'pronoun_demonstrative_distal', 'pronoun_demonstrative_proximate', 'verbal_noun', 'proper_noun', 'adjective_pronominal', 'pronoun_propword']
    list_of_determiner_pos = ['definite_article', 'adjective_quantifier', 'adjective_numeral', 'pronoun_possessive']
    for word in a_sentence:
        if word['Part_Of_Speech'] in list_of_nominal_pos:
            list_of_nouns.append(word)
        elif word['Part_Of_Speech'] in list_of_determiner_pos:
            list_of_dets.append(word)
        elif word['Part_Of_Speech'] == 'preposition':
            list_of_preps.append(word)
    return list_of_dets, list_of_nouns, list_of_preps


#def head_of_article(current_sentence, list_of_dets, list_of_nouns):
#    for det, noun in list(itertools.product(list_of_dets, list_of_nouns)):
#        if det['Stressed_Unit'] in noun['Stressed_Unit']:
#            det['_'] = str(current_sentence.index(noun) + 1)
#            if det['Part_Of_Speech'] == 'definite_article':
#                noun['Analysis'] = noun['Analysis'] + 'Def'

def head_of_article2(current_sentence, list_of_dets, list_of_nouns):
    finished_nouns = []
    finished_dets = []
    ignore_list = []
    combo=list(itertools.product(list_of_dets, list_of_nouns))
    for c in combo:
        if c[0]['Stressed_Unit'] in c[1]['Stressed_Unit']: #If the stressed units of the determiner and the noun are the same,
            if not ignore_list: #If ignore_list is empty,
                c[0]['_'] = str(current_sentence.index(c[1]) + 1) #the head of the determiner is the same as the index associated with the noun plus 1.
                finished_dets.append(c[0]) #add the determiner to the finished_dets list
                finished_nouns.append(c[1]) #add the noun to the finished_nouns list
                ignore_list.append(c) #append the combo to the ignore_list
            elif c[0] in finished_dets: #If ignore_list has something in it and the determiner is in the finished_dets list,
                ignore_list.append(c) #add the combo to the ignore_list
            elif c[1] in finished_nouns: #If ignore_list has something in it and the noun is in the list of finished_nouns,
                ignore_list.append(c) #add the combo to the ignore_list
            else: #otherwise - if the ignore_list is not empty but neither the determiner nor the noun has been seen before,
                c[0]['_'] = str(current_sentence.index(c[1]) + 1) #do all the stuff mentioned above in the if not statement
                finished_dets.append(c[0])
                finished_nouns.append(c[1])
                ignore_list.append(c)
        else: #if the stressed units don't match
            pass #go on to the next combo.

#The function head_of_preposition assigns the index of a noun that shares its stressed unit with a preposition to the head column of the preposition.
#It attempts to prohibit erroneous assignment by ignoring already seen items. Hopefully the numbere of "elif" and "else" statements will be enough
#to cover all possible cases. It might be prudent to add this kind of functionality to head_of_article as well.

def case_check(prep, noun):
    if 'acc.' in noun['Analysis'] and 'No_Features' in prep['Analysis']:
        prep['Analysis'] += 'acc.'
    elif 'dat.' in noun['Analysis'] and 'No_Features' in prep['Analysis']:
        prep['Analysis'] += 'dat.'
    elif 'gen.' in noun['Analysis'] and 'No_Features' in prep['Analysis']:
        prep['Analysis'] += 'gen.'


def head_of_preposition(current_sentence, list_of_preps, list_of_nouns):
    finished_nouns = []
    finished_preps = []
    ignore_list = []
    combo=list(itertools.product(list_of_preps, list_of_nouns))
    for c in combo:
        if c[0]['Stressed_Unit'] in c[1]['Stressed_Unit']:
            if not ignore_list:
                c[0]['_'] = str(current_sentence.index(c[1]) + 1)
                case_check(c[0], c[1])
                finished_preps.append(c[0])
                finished_nouns.append(c[1])
                ignore_list.append(c)
            elif c[0] in finished_preps:
                ignore_list.append(c)
            elif c[1] in finished_nouns:
                ignore_list.append(c)
            else:
                c[0]['_'] = str(current_sentence.index(c[1]) + 1)
                case_check(c[0], c[1])


def find_head_in(a_sentence, list_of_dets, list_of_nouns, list_of_preps):
    head_of_article2(a_sentence, list_of_dets, list_of_nouns) #testing head_of_article2
    head_of_preposition(a_sentence, list_of_preps, list_of_nouns)


def assign_head_in(list_of_sentences):
    for sent in list_of_sentences.values():
        dets, nouns, preps = list_of_dets_and_nouns_in(sent)
        find_head_in(sent, dets, nouns, preps)


# ========================================================================================================================================================================================================


#Section 6: Functions to convert the data to CONLLU format
#*********************************************************


# The following series of functions modifies the "Analysis" column of the csv output from CorPH to create the "Feats" (for "Features") column of a CONLLU file.
# The specific goal is to make sure that the "Feats" column consists of a series of key:value pairs, where key = the name of a feature and value = a value for that feature.


#Section 6.1. Analysis of Substantives (Nouns and Adjectives)

# The function case_analysis checks to see if any key in "Feats" contains "nom/acc/gen/dat" and creates a new key:value pair. 

def analyze_case_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if 'nom' in word['feats']['Analysis'][0:3]:
                word['feats']['Case'] = 'Nom'
            elif 'acc' in word['feats']['Analysis'][0:3]:
                word['feats']['Case'] = 'Acc'
            elif 'gen' in word['feats']['Analysis'][0:3]:
                word['feats']['Case'] = 'Gen'
            elif 'dat' in word['feats']['Analysis'][0:3]:
                word['feats']["Case"] = 'Dat'


# The function number_analysis checks to see if any key in "Feats" contains "sg" or "pl" and creates a new key:value pair.
				
def analyze_number_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if 'sg' in word['feats']['Analysis'][4:6]:
                word['feats']['Number'] = 'Sing'
            elif 'pl' in word['feats']['Analysis'][4:6]:
                word['feats']['Number'] = 'Plur'


# The following functions checks to see if the key 'Analysis' in "Feats" contains "ma/fe/ne" creates a new key:value pair.
    
def analyze_gender_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if 'ma' in word['feats']['Analysis'][7:9]:
                word['feats']['Gender'] = 'Masc'
            elif 'fe' in word['feats']['Analysis'][7:9]:
                word['feats']['Gender'] = 'Fem'
            elif 'ne' in word['feats']['Analysis'][7:9]:
                word['feats']['Gender'] = 'Neut'


#The following function analyzes definiteness in nouns and the definite article.

def analyze_definiteness_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if 'Def' in word['feats']['Analysis']:
                word['feats']['Definite'] = 'Def'
            elif word['xpos'] == 'definite_article':
                word['feats']['Definite'] = 'Def'


#Section 6.2. Analysis of Prepositions

#The following function analyses  person in prepositions and possessives.
#Note that this could be expanded to cover all pronouns.
				
def analyze_person_in_prepositions_and_possessives_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'preposition' or word['xpos']== 'pronoun_possessive' or word['xpos'] == 'particle_pronominal':
                if '1' in word['feats']['Analysis']:
                    word['feats']['Person'] = '1'
                elif '2' in word['feats']['Analysis']:
                    word['feats']['Person'] = '2'
                elif '3' in word['feats']['Analysis']:
                    word['feats']['Person'] = '3'


#The following function analyses number in prepositions and possessives.
#Note that this could be expanded to cover all pronouns.
                    
def analyze_number_in_prepositions_and_possessives_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'preposition' or word['xpos']== 'pronoun_possessive' or word['xpos'] == 'particle_pronominal':
                if 'sg.' in word['feats']['Analysis']:
                    word['feats']['Number'] = 'Sing'
                elif 'pl.' in word['feats']['Analysis']:
                    word['feats']['Number'] = 'Plur'
                elif 'du.' in word['feats']['Analysis']:
                    word['feats']['Number'] = 'Dual'


#The following function analyses gender in prepositions and possessives.

def analyze_gender_in_prepositions_and_possessives_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'preposition' or word['xpos']== 'pronoun_possessive' or word['xpos'] == 'particle_pronominal':
                if 'masc.' in word['feats']['Analysis']:
                    word['feats']['Gender'] = 'Masc'
                elif 'fem.' in word['feats']['Analysis']:
                    word['feats']['Gender'] = 'Fem'
                elif 'neut.' in word['feats']['Analysis']:
                    word['feats']['Gender'] = 'Neut'


#The following three functions assign a value to the feature Case for prepositions.
#The function assign_case has the drawback that it assigns Acc/Dat to variable prepositions, rather than the actual case in the context.
#It might be that for ambiguous instances, the case value should only be filled in if the feats has acc. or dat.
# (i.e. if the analysis in CorPH already specifies the case). Another way is to use the feats of an associated noun,
#after tagging head/deprels.

def case_finder(a_sentence):
    prep_list=[{'a 7': 'Dat'}, {'acht 2': 'Acc'}, {'al': 'Acc'}, {'amail 1': 'Acc'}, {'ar 1': 'Acc/Dat'}, {'cen': 'Acc'}, {'cenmothá': 'Acc'}, {'co 1': 'Acc'}, {'co 2': 'Dat'}, {'co·rrici': 'Acc'}, {'co·rrici': 'Acc'}, {'coticci': 'Acc'}, {'di': 'Dat'}, {'do 1': 'Dat'}, {'dochumm': 'Gen'}, {'echtar': 'Acc'}, {'eter': 'Acc'}, {'fíad': 'Dat'}, {'fo': 'Acc/Dat'}, {'for': 'Acc/Dat'}, {'fri': 'Acc'}, {'fri': 'Acc'}, {'íar 1': 'Dat'}, {'íarmithá': 'Dat'}, {'imm': 'Acc'}, {'i': 'Acc/Dat'}, {'ingé 1': 'Acc'}, {'ís 1': 'Dat'}, {'la': 'Acc'}, {'ó 1': 'Dat'}, {'oc': 'Dat'}, {'ós 1': 'Dat'}, {'óthá': 'Dat'}, {'re': 'Dat'}, {'sech 1': 'Acc'}, {'tar 1': 'Acc'}, {'tre': 'Acc'}]
    combo = list(itertools.product(a_sentence, prep_list))
    assign_case(combo)

def assign_case(combined_list):
    for word in combined_list:
        if isinstance(word[0]['id'], int) and word[0]['upos'] != 'PUNCT':
            if word[0]['xpos'] == 'preposition' and not word[0]['feats'].copy().get('Case'):
                if word[0]['lemma'] in word[1].keys():
                    value = list(word[1].values())
                    word[0]['feats']['Case'] = value[0]
                    break
            

def analyze_case_in_prepositions_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'preposition':
                if 'acc.' in word['feats']['Analysis']:
                    word['feats']['Case'] = 'Acc'
                elif 'dat.' in word['feats']['Analysis']:
                    word['feats']['Case'] = 'Dat'
                elif 'gen.' in word['feats']['Analysis']:
                    word['feats']['Case'] = 'Gen'
                elif not word['feats'].copy().get('Case'):
                    case_finder(a_sentence)

def latin_check(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'preposition':
                if not word['feats'].copy().get('Case'):
                    word['feats']['Case'] = 'Unk'


#Section 6.3. Analysis of Verbs

# The function verbal_infixed_analysis deals with the features of infixed pronouns. gender_finder and define_number are sub-functions found in the main function.

def gender_finder(matched_obj):
    if len(matched_obj.group()) > 7:
        if 'm' in matched_obj.group()[7:9]:
            return 'Masc'
        elif 'f' in matched_obj.group()[7:9]:
            return 'Fem'
        elif 'n' in matched_obj.group()[7:9]:
            return 'Neut'
    elif len(matched_obj.group()) == 7:
            pass

def define_number(string):
    if 'sg' in string:
        return 'Sing'
    elif 'pl' in string:
        return 'Plur'
    else:
        pass

def verbal_infixed_analysis(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'verb':

                m = re.search('(obj)[123]((sg.)|(pl.))((masc)|(fem)|(neut)|())', word['feats']['Analysis'])

                if m:
                    word['feats']['Person[Obj]'] = m.group()[3]

                    number = define_number(m.group()[4:7])
                    gender = gender_finder(m)

                    if number or gender:
                        word['feats']['Number[Obj]'] = number
                        word['feats']['Gender[Obj]'] = gender
                        if None == word['feats']['Gender[Obj]']:
                            del word['feats']['Gender[Obj]']

#The verbal_person_analysis checks deals with the features of the subject.

def verbal_person_number_analysis(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'verb':
                m = re.search('(?<!obj)[123]((sg)|(pl))', word['feats']['Analysis'])
                if m:
                    word['feats']['Person[Subj]'] = m.group()[0]
                    number = m.group()[1:3]
                    if 'sg' in number:
                        word['feats']['Number[Subj]'] = 'Sing'
                    elif 'pl' in number:
                        word['feats']['Number[Subj]'] = 'Plur'
                    else:
                        pass

# The function tense_analysis checks to see if any key in "Feats" contains a tag for a tense or the imperative mood ("impv") and creates a new key:value pair.
				
def tense_analysis(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if 'pres' in word['feats']['Analysis']:
                word['feats']['Tense'] = 'Pres'
            elif 'past' in word['feats']['Analysis']:
                word['feats']['Tense'] = 'Past'
            elif 'pret' in word['feats']['Analysis']:
                word['feats']['Tense'] = 'Pret'
            elif 'cond' in word['feats']['Analysis']:
                word['feats']['Tense'] = 'Cond'
            elif 'impf' in word['feats']['Analysis']:
                word['feats']['Tense'] = 'Impf'
            elif 'fut' in word['feats']['Analysis']:
                word['feats']['Tense'] = 'Fut'
            elif 'hab' in word['feats']['Analysis']:
                word['feats']['Tense'] = 'Hab'
            elif 'impv' in word['feats']['Analysis']:
                word['feats']['Tense'] = 'Pres'


# The function verbal_voice_analysis checks to see whether or not for rows whose "xpos" value is "verb" the "Analysis" key
# in the "Feats" contains "pass" and creates a new key:value pair.

def voice_analysis(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'verb':
                if 'pass' in word['feats']['Analysis']:
                    word['feats']['Voice'] = 'Pass'
                elif 'pass' not in word['feats']['Analysis']:
                    word['feats']['Voice'] = 'Act'


# The function mood_voice_analysis checks to see whether or not for rows whose "xpos" value is "verb" the "Analysis" key
# in "Feats" contains ".impv./.subj." or, in the case of the first key in the dictionary,
# neither of them and creates a new key:value pair. ##Return to this.
    
def mood_analysis(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'verb':
                if '.impv.' in word['feats']['Analysis']:
                    word['feats']['Mood'] = 'Impv'
                elif '.subj.' in word['feats']['Analysis']:
                    word['feats']['Mood'] = 'Subj'
                elif ('.impv.' not in word['feats']['Analysis']) and ('.subj.' not in word['feats']['Analysis']):
                    word['feats']['Mood'] = 'Ind'
                                

# The following function checks to see if there is a key called "Tense" in "Feats". If so, it creates a new key:value pair.

def finiteness_analysis(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['feats'].copy().get('Tense'):
                word['feats']['VerbForm'] = 'Fin'


# The following function creates the key:value pair "Subcat:Trans/Intrans" in "Feats".

def analyze_subcat_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if '.trans.' in word['feats']['Analysis']:
                word['feats']['Subcat'] = 'Trans'
            elif '.intrans.' in word['feats']['Analysis'] or '.pass.' in word['feats']['Analysis']:
                word['feats']['Subcat'] = 'Intrans'
            elif 'unclear' in word['feats']['Analysis']:
                word['feats']['Subcat'] = 'Unk'


# The following function analyzes the classification of infixed pronouns in compound verbs.

def analyze_object_pron_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['feats'].copy().get('Person[Obj]'):
                if '.A' in word['feats']['Analysis']:
                    word['feats']['PronType'] = 'InfA'
                elif '.B' in word['feats']['Analysis']:
                    word['feats']['PronType'] = 'InfB'
                elif '.C' in word['feats']['Analysis']:
                    word['feats']['PronType'] = 'InfC'


# The following function analyzes augmented verbs.

def analyze_augm_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if 'augm.' in word['feats']['Analysis']:
                word['feats']['Aspect'] = 'Perf'


# The following function analyzes relative verbs.

def analyze_rel_in(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['xpos'] == 'verb':
            if 'len' in word['feats']['Analysis']:
                word['feats']['RelType'] = 'Len'
            elif 'nas' in word['feats']['Analysis']:
                word['feats']['RelType'] = 'Nas'
            elif 'rel' in word['feats']['Analysis'] and 'nas' not in word['feats']['Analysis'] and 'len' not in word['feats']['Analysis']:
                word['feats']['RelType'] = 'Other'
            else:
                pass

#def analyze_rel_in(a_sentence):
#    for word in a_sentence:
#        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
#            if 'rel' in word['feats']['Analysis']: ###Why shouldn't 'nas' or 'len' also be referred to at this level? !!!! Basically, 'rel' should be confined to the final elif statement.
#                if 'len' in word['feats']['Analysis']:
#                    word['feats']['RelType'] = 'Len'
#                elif 'nas' in word['feats']['Analysis']:
#                    word['feats']['RelType'] = 'Nas'
#                elif 'len' not in word['feats']['Analysis'] or 'nas' not in word['feats']['Analysis']: #the or here maybe problematic
#                    word['feats']['RelType'] = 'Other'


#Section 6.4. Analysis of other items

#The following function creates the feature value pair Poss:Yes for possessive pronouns.

def analyze_value_of_poss(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'pronoun_possessive':#Remember to also add pronoun_independent here if the analysis is genitive.
                word['feats']['Poss'] = 'Yes'


#The following function analyzes the demonstrative pronouns.

def analyze_value_of_deixis(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'pronoun_demonstrative_distal' or word['xpos'] == 'particle_demonstrative_distal':
                word['feats']['Deixis'] = 'Remt'
            elif word['xpos'] == 'pronoun_demonstrative_proximate' or word['xpos'] == 'particle_demonstrative_proximate':
                word['feats']['Deixis'] = 'Prox'


#The following function analyzes various types of pronouns, quantifiers, and the article.

def analyze_value_of_prontype(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
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


#The following function analyzes the person of pronouns.

def analyze_person_of_pronouns(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if 'pron' in word['lemma'] and word['xpos'] == 'pronoun_independent' or word['xpos'] == 'pronoun_possessive':
                if '1' in word['lemma']:
                    word['feats']['Person'] = '1'
                elif '2' in word['lemma']:
                    word['feats']['Person'] = '2'
                elif '3' in word['lemma']:
                    word['feats']['Person'] = '3'


#Section 6.5. Adjective Degree Analysis
                    
def analyze_adjective_degree_analysis(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['feats']['Analysis'] == 'comp.':
                word['feats']['Degree'] = 'Cmp'
            elif word['feats']['Analysis'] == 'sup.':
                word['feats']['Degree'] = 'Sup'
            elif word['feats']['Analysis'] == 'equ.':
                word['feats']['Degree'] = 'Equ'
            elif word['xpos'] == 'adjective' and word['feats']['Analysis'] != 'comp.' and word['feats']['Analysis'] != 'sup.' and word['feats']['Analysis'] != 'equ.':
                word['feats']['Degree'] = 'Pos'


#Section 6.6. Verbal Noun Analysis

def verbal_noun_analysis(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'verbal_noun':
                word['feats']['VerbForm'] = 'VNoun'

#Section 6.7. Putting it all together.

#The following function groups all of the functions that apply to substantives (i.e. nouns and adjectives) together.

def change_substantive_analysis(input_data):
    analyze_case_in_(input_data)
    analyze_number_in_(input_data)
    analyze_gender_in_(input_data)
    analyze_definiteness_in_(input_data)
    return input_data


#The following function groups all of the functions that apply to verbs together.

def change_verb_analysis(input_data):
    verbal_infixed_analysis(input_data)
    verbal_person_number_analysis(input_data)
    tense_analysis(input_data)
    voice_analysis(input_data)
    mood_analysis(input_data)
    finiteness_analysis(input_data)
    analyze_subcat_in_(input_data)
    analyze_object_pron_in_(input_data)
    analyze_augm_in_(input_data)
    analyze_rel_in(input_data)
    verbal_noun_analysis(input_data)
    return input_data


#The following function groups all of the functions that apply to prepositions and possessives together.

def change_preposition_analysis(input_data):
    analyze_person_in_prepositions_and_possessives_in_(input_data)
    analyze_number_in_prepositions_and_possessives_in_(input_data)
    analyze_gender_in_prepositions_and_possessives_in_(input_data)
    analyze_case_in_prepositions_in_(input_data)
    latin_check(input_data)
    return input_data

# The following function groups all the functions that apply to other items together.

def change_other_analyses(input_data):
    analyze_value_of_poss(input_data)
    analyze_value_of_deixis(input_data)
    analyze_value_of_prontype(input_data)
    analyze_person_of_pronouns(input_data)
    analyze_adjective_degree_analysis(input_data)

#This deletes keys with null values in the "feats" dictionary.
            
def delete_null_values_in(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if 'No_Features' in word['feats']['Analysis'] and len(word['feats'].keys()) == 1:
                word['feats'] = '_'
            else:
                del word['feats']['Analysis']


#The following function combines the functions change_substantive_analysis, change_verb_analysis, change_preposition_and_possessive_analysis, change_other_analyses, and delete_null_values_in.
    
def change_all_analyses(list_of_sentences):

    for sent in list_of_sentences:

        for word in sent:

            if word['upos'] != 'PUNCT' and word.get('misc', {}).get('tuple'): #this finds chunks which are tagged with 'tuple' in 'misc' column

                x = word['misc']['tuple'].split('-') #splits up the tuple in the chunk's 'misc' column
                word['id'] = (int(x[0]), '-', int(x[1])) #creates an id for chunks using the numbers in the tuple

    [change_substantive_analysis(item) for item in list_of_sentences] #Since there is already a loop through the list of sentences, the following statements could probably be simplified to "function(sent)".
    [change_verb_analysis(item) for item in list_of_sentences]
    [change_preposition_analysis(item) for item in list_of_sentences]
    [change_other_analyses(item) for item in list_of_sentences]
    [delete_null_values_in(item) for item in list_of_sentences]
    output_data = [item.serialize() for item in list_of_sentences]

    return output_data


# ========================================================================================================================================================================================================


#Section 7: Functions to fill in upos and deprel columns in a conllu file.
#*************************************************************************

#The following functions (assign_upos and upos_finder) assign upos to a word in a sentence in a list of sentences.

def assign_upos(combined_list):
    for count, word in enumerate(combined_list):
        if isinstance(word[0]['id'], int) and word[0]['upos'] != 'PUNCT':
            if combined_list[count][0]['xpos'] in combined_list[count][1]:
                for key, value in combined_list[count][1].items():
                    combined_list[count][0]['upos'] = value
                
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


# This function assigns a deprel and upos to the copula.

def assign_deprel_to_copula_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['lemma'] == 'is 1':
                word['upos'] = 'AUX'
                word['deprel'] = 'cop'


# This function assigns a deprel to the article.

def assign_deprel_to_article_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['lemma'] == 'in 1' or word['xpos'] == 'adjective_quantifier':
                word['deprel'] = 'det'


# This function fixes the deprel and upos associated with the item 'tantum'.

def tantum_fix(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['form'] == 'tantum':
                word['upos'] = 'PART'
                word['deprel'] = 'advmod:emph'


def uile_fix(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['lemma'] == 'uile':
                word['upos'] = 'ADJ'
                word['deprel'] = '_' #It is probably best to have this blank rather than 'amod', because there will be some cases when the word is not a modifier.

# This function assigns a deprel to the prepositions.

def assign_deprel_to_preposition_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'preposition' and not word['feats'].copy().get('Person'):
                word['deprel'] = 'case' #This assigns 'case' even to potential mark:prt with verbal nouns. It also assigns 'case' to relative prepositiosn before verbs, even though in this instance. the proper deprel is obl:prep.


# This function assigns a deprel to numerals that modify nouns.

def assign_deprel_to_numeral_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'adjective_numeral':
                word['deprel'] = 'nummod'


# This function assigns a deprel, upos, and xpos to the abbreviation .i..

def assign_deprel_to_abbreviation_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['lemma'] == '.i.':
                word['xpos'] = 'abbreviation'
                word['upos'] = 'CCONJ'
                word['deprel'] = 'cc'


# This function assigns a deprel to negative particles.

def assign_deprel_to_negation_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'particle_negative_main' or word['xpos'] == 'particle_negative_subordinate':
                word['deprel'] = 'advmod:neg'


# This function assigns a deprel complementizers and the particle "no", when the latter is not incorporated into a verb.

def assign_deprel_to_complementizer_in_(a_sentence):
    for word in a_sentence:
        if isinstance(word['id'], int) and word['upos'] != 'PUNCT':
            if word['xpos'] == 'complementiser' or word['lemma'] == 'no·':
                word['deprel'] = 'mark:prt'
                word['upos'] = 'SCONJ'


# This following two functions assigns a deprel and upos to coordinate conjunctions.

def assign_deprel_to_coordinate_conjunction_in_(combined_list):
    for count, word in enumerate(combined_list):
        if isinstance(word[0]['id'], int) and word[0]['upos'] != 'PUNCT':
            if combined_list[count][1] in combined_list[count][0]['lemma'] and combined_list[count][0]['xpos'] == 'conjunction':
                combined_list[count][0]['deprel'] = 'cc'
                combined_list[count][0]['upos'] = 'CCONJ'

def coordconj_finder(list_of_sentences):
    cconjlist = ['ocus 2', 'nó 1', 'ná 4', 'fa', 'nach 6', 'rodbo', 'et', 'uel', 'quam']
    for a_sentence in list_of_sentences:
        combo = list(itertools.product(a_sentence, cconjlist))
        assign_deprel_to_coordinate_conjunction_in_(combo)


# This following two functions assigns a deprel and upos to subordinate conjunctions.

def assign_deprel_to_subordinate_conjunction_in_(combined_list):
    for count, word in enumerate(combined_list):
        if isinstance(word[0]['id'], int) and word[0]['upos'] != 'PUNCT':
            if combined_list[count][1] in combined_list[count][0]['lemma'] and combined_list[count][0]['xpos'] == 'conjunction':
                combined_list[count][0]['deprel'] = 'mark'
                combined_list[count][0]['upos'] = 'SCONJ'
    
def subconj_finder(list_of_sentences):
    sconjlist = ['amail 2', 'ar 2', 'a 6', 'cía 2', 'dég 2', 'resíu', 'úaire', 'ma', 'ó 2', 'ol 2']
    for a_sentence in list_of_sentences:
        combo = list(itertools.product(a_sentence, sconjlist))
        assign_deprel_to_subordinate_conjunction_in_(combo)


# This following two functions assigns a deprel and upos to coordinate conjunctions.

def do_all_deprel(list_of_sentences):
    [assign_deprel_to_copula_in_(a_sentence) for a_sentence in list_of_sentences]
    [assign_deprel_to_article_in_(a_sentence) for a_sentence in list_of_sentences]
    [assign_deprel_to_preposition_in_(a_sentence) for a_sentence in list_of_sentences]
    [assign_deprel_to_abbreviation_in_(a_sentence) for a_sentence in list_of_sentences]
    [assign_deprel_to_negation_in_(a_sentence) for a_sentence in list_of_sentences]
    [assign_deprel_to_numeral_in_(a_sentence) for a_sentence in list_of_sentences]
    [assign_deprel_to_complementizer_in_(a_sentence) for a_sentence in list_of_sentences]
    [tantum_fix(a_sentence) for a_sentence in list_of_sentences]
    [uile_fix(a_sentence) for a_sentence in list_of_sentences]
    subconj_finder(list_of_sentences)
    coordconj_finder(list_of_sentences)
    
# ========================================================================================================================================================================================================


#Section 8: Functions to add in chunks and punctuation and rearrange ID/head numbers.
#************************************************************************************


def iteratorformorphs(morph_y, word_y, j, acc, accalt=None):

    morph_y = j+1
    accalt=''
    acc=''
    word_y += 1

    return morph_y, word_y, acc


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


def check_concatenations3(list_of_words, list_of_morphs, sentence):

    words = [re.sub("[^0-9a-zA-Z_À-ÿ]+", '', x) for x in list_of_words] # uses the regex library to remove all non-alphanumeric characters before comparison
    morphs = [re.sub("[^0-9a-zA-Z_À-ÿ]+", '', x[0]) for x in list_of_morphs] # "
    (tuid, ) = set([x[1] for x in list_of_morphs])
    (translation, ) = set([x[2] for x in list_of_morphs])
    (textualunit, ) = set([x[3] for x in list_of_morphs])
    word_y = 0 # iterator
    morph_y = 0 # "
    tij = [] # initialization
    accumulated = '' # empty accumulated string
    currentact = []

    for j in range(len(morphs)): # loops over every morph

        accumulated += morphs[j]
        currentact.append(({'accumulated':accumulated, 'current_morph':morphs[j], 'currentword':words[word_y], 'word_y':word_y, 'morph_y':morph_y, 'j':j})) #This keeps track of all the morphs and words that pass through the iterator.
        #Insert currentact for testing.

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

            elif words[word_y] == 'rp' or words[word_y] == 'pp' or words[word_y] == 'cp':#Tests to see if the current word is a punctuation mark.

                tij.append((word_y, morph_y+1, morph_y+1))

                if accumulated == words[word_y+1]: #Tests whether the accumulated morphs are the same as the next word. This is necessary because the accumulated morph will never correspond to the current word, which is the punctuation mark.
                    morph_y = j+1
                    word_y += 2
                    accumulated = ''
                elif accumulated != words[word_y+1]: #Tests whether the accumulated morph is not the same as the next word. This might happen if the next word is a new chunk (a concatenated string of words).
                    morph_y = j+1
                    word_y += 1

    return tij, currentact #insert currentact for testing


#The following function finds punctuation marks in a text string.

def getpunct(word):

    sentencestring = word['Textual_Unit'] #Gets the text string.
    punctlist = [('.', 'p'), (',', 'c'), ('·', 'r')] #The list of main punctuation marks and their alphanumeric "equivalent".
    newstring = re.sub(' ([.,·]) ', r' \1punct ', sentencestring) #Substitutes the punctuation marks in a string with interim alphanumeric characters for search purposes.
    finallist = []

    for word in newstring.split(): #Iterates through a string

        if word.endswith('punct'): #Finds punctuation marks

            wordstart = word[:-5] #Gets rid of the interim marker of punctuation (i.e. "punct")

            for punct in punctlist: #Goes through the list of punctuation marks

                if punct[0] == wordstart: #Checks if the current punctuation mark in the text string is the same as the current item in the list of punctuation marks.

                    word = punct[1] + 'p' #Creates a alphanumeric version of the punctuation mark.

        finallist.append(word) #Creates a list of words which includes the alphanumeric versions of punctuation marks.

    return finallist


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

def checkchunkorder(sent): #There's a big issue with this: if the concatenated morph is second to last, then dif will never reach -1.

    chunk=[] #This will be a list consisting of the concatenated morph and its supposed sub-elements.
    allchunks=[] #This will be a list consisting of all the concatenated morphs and their sub-elements in a sentence.
    dif = None #A counter.

    for word in sent:

        if word.get('interim'): #Gets morphs that are concatenated morphs - only concatenated morphs have the key "interim" because of the reassignids function.

            dif = abs(word['interim'][2] - word['interim'][0]) #Assigns the difference between the two parts of interim to the counter. The two parts of interim define a range of elements that ought to be sub-parts of the concatenated morphs. The difference between the two can be used to tell the iterator how many words to add to the chunk list.
            chunk.append(word) #Adds the concatenate morph to the chunk list.

        elif isinstance(dif, int) and dif >= 0 and not word.get('interim'): #Checks whether the counter is an integer and if it is larger than or equal to 0 and if the current word is a normal morph.
            #elif isinstance(dif, int) replaces elif dif != None

            dif -= 1 #Decreases the counter
            chunk.append(word) #Appends the word to the chunk list.

            if dif < 0: #Checks if the counter is less than 0. This means that the range of words for a given chunk has already been looked at.

                allchunks.append(chunk) #Appends the chunk list (consisting of the concatenated morph and its sub-element) to the list of all chunks in a sentence.
                chunk = [] #Empties the current chunk. #consider also adding dif == None here?

        elif not dif: #If an integer has not been assigned to the counter, then there is no need to add anything to a chunk list. This happens if there are no chunks in a given stretch of the list.
            #note that elif not dif should be equivalent to elif dif == None

            pass

    return allchunks


#The following function will use the information gathered in the previous function to change the order of stray concatenated morphs.

def changechunkorder(allchunks, sentence):

    lastid = None #The id of the last subelement of a chunk.
    searchlen = None
    badindex = None

    for chunk in allchunks:  #Iterates through the list of all the chunks in a sentence

        accumulated, firstword, *_, lastword = chunk #Assigns the subelements of a chunk to various variables.

        accumulated_string = re.sub("[^0-9a-zA-Z_À-ÿ]+", '', str(accumulated['form'])) #Makes an alphanumeric test string out of the various variables
        firstword_string = re.sub("[^0-9a-zA-Z_À-ÿ]+", '', str(firstword['form']))
        lastword_string = re.sub("[^0-9a-zA-Z_À-ÿ]+", '', str(lastword['form']))

        if firstword_string not in accumulated_string or lastword_string not in accumulated_string: #Finds chunks that are not really chunks; basically if the first morph in the chunk is not in the accumulated string (the concatenated morph) and the last morph in the chunk is not in the accumulated string, this is a false chunk. The accumulated string will need to be shifted to the position where its subelements actually are in the sentence.

            lastid = chunk[0]['interim'][2] #Assigns the final element of the interim id to lastid. #consider changing to "accumulated".
            badindex = sentence.index(chunk[0]) #Gets the current location of the accumulated string in the sentence — Note that this is the wrong location. #consider changing to "accumulated".
            searchlen = len(chunk)-2 #Sets a search length. Basically this will be used to find the first sub-member of a concatenated morph.

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


#The following function replaces placeholder punctuation marks with actual punctuation marks.

def changepunct(sent):

    punctlist = [('.', 'pp'), (',', 'cp'), ('·', 'rp')]

    for word in sent:

        if word['upos'] == 'PUNCT':

            for punct in punctlist:

                if word['form'] in punct[1]:

                    word['form'] = punct[0]
                    word['lemma'] = punct[0]


#The following function inserts 'old_head' and 'old_id' dictionary pairs.

def assign_old_stuff(word):

    if not word.get('interim'):

        word['old_head'] = word['head']
        word['old_id'] = word['id']

    else:

        pass


#The following function changes ids of morphs in the sentence. This is necessary because sentences might have a newly inserted punctuation mark that messes up the original id numbers.

def changeid2(sent):
    #Remember to replace with original punctuation after changings ids.

    punctseen=[] #A list of the punctuation marks that have been seen by the loop.

    for word in sent: #Goes through morphs in a sentence.

        if not punctseen: #Checks whether no punctuation marks have been seen yet.
        #if not punctseen should be the same as if punctseen == [1]
            if word['upos'] != 'PUNCT': #If the current word is not a punctuation mark

                assign_old_stuff(word)

            elif word['upos'] == 'PUNCT': #If the current word is a punctuation mark

                changepunct(sent)
                punctseen.append(word) #Add the punctuation mark to the list of punctuation marks.

        elif punctseen: #Checks if at least one punctuation mark has been seen.
        #elif punctseen should be the same as punctseen != []

            if len(punctseen) >= 1 and isinstance(word['id'], int): #Consider removing isinstance.

                if word['upos'] == 'PUNCT':

                    word['id'] += len(punctseen)
                    changepunct(sent)
                    punctseen.append(word)

                elif word['upos'] != 'PUNCT':

                    assign_old_stuff(word)
                    word['id'] += len(punctseen)

    return #insert sent and punctseen for testing


#The following function changes the head dictionary pair.

def change_head(sent):

    words = []
    ignore_list = []

    for word in sent:

        if isinstance(word['head'], int):

            words.append(word)

    combo=list(itertools.combinations(words, 2))

    for c in combo:

        if c[0] in ignore_list:

            pass

        elif c[0] not in ignore_list:

            if c[0]['old_head'] == c[1]['old_id']:

                c[0]['head'] = c[1]['id']
                ignore_list.append(c[0])

#                print(c[0], c[1], '*****ab')

            elif c[0]['old_id'] == c[1]['old_head']:

                c[1]['head'] = c[0]['id']

#                print(c[0], c[1], '*****ba')


#The following function removes 'old_id' and 'old_head' dictionary pairs

def del_old_stuff(sent):

    for word in sent:

        if word.get('old_id') or word.get('old_head'):

            del word['old_id']
            del word['old_head']


#The following function removes the 'interim' dictionary pair from inserted chunks.

def changechunkids(sent):

    chunks = checkchunkorder(sent)

    for chunk in chunks:

        chunk[0]['id'] = (chunk[1]['id'], '-', chunk[-1]['id'])
        del chunk[0]['interim']
        chunk[0]['misc'] = '_'


# ========================================================================================================================================================================================================


#Section 9: Automating the functions in Sections 1 - 8.
#******************************************************


#The following functions opens a csv file, does some pre-processing (see section 1), and returns the data as a list.
def proper_sort(data):
    for row in data:
        if '-' in row[3]: #row[3] is the 'Text Unit Id column'
            new=re.split('-', row[3]) #Splits Text Unit ID into Text Unit (e.g. 0050) and sentence number (e.g. 1)
            row[0]=int(new[1]) #Puts the sentence number into the first position in the row so that the data can be sorted on by sentence number
            row[1]=int(row[1]) #After creating row[0], row[1] is the Sort ID.
    headings=data.pop(0) #Pops out the first row, which consists of column headings
    data = sorted(data) #Sorts the data by sentence number.
    return data, headings

def read_in_with_columns(filename):
    with open(filename, encoding ='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter =',', skipinitialspace=True)
        output_data = [row for row in csv_reader]
        output_data, headings = proper_sort(output_data)
        output_data.insert(0, headings)
        [row.pop(0) for row in output_data]
        [row.pop(0) for row in output_data]
        preprocessing(output_data)
    return output_data


#The following functon makes an ordered dictionary whose values are sentences which consist of a list of dictionaries of word:feature pairs

def make_dictionary_of_sentences_out_of(data):
    sentences_ordered_dict = OrderedDict()
    column_names = data[0] # Gets the column names
    all_rows = data[1:]  # gets the textual unit rows
    for row in all_rows: # Separates them into text_unit_id (idn) and other values
        idn = str(row[1])
        values = row # print(list(zip(column_names, values)))
        sentence_dict = dict(zip(column_names, values)) # converts them into a dict # print(sentenceDict)
        if idn in sentences_ordered_dict: # checks if sentence has been added to the textual unit dictionary before and adds it
            sentences_ordered_dict[idn] = sentences_ordered_dict[idn] + [sentence_dict]
        else: # otherwise creates a new textual unit dictionary and adds the sentence to the dictionary
            sentences_ordered_dict[idn] = [sentence_dict]
    return sentences_ordered_dict


#The following function combines the function read_in_with_columns and make_dictionary_of_sentences_out_of with the functions in sections XXX.

def automation(filename):
    data = read_in_with_columns(filename)
    sentences = make_dictionary_of_sentences_out_of(data)
    look_for_relative_or_infixed_verbs_in_all(sentences)
    remove_all_extraneous_info_in(sentences)
    compound_detector(sentences)
    assign_head_in(sentences)
    return sentences


#The following function takes the processed output and rearranges the data into a CONLLU-style format.
#The data is written to a file (in the intro to this script called "name_of_interim_output_file").

# def write_out(filename, sentences):
#     with open(filename, 'w', encoding='utf-8') as file_out:
#         tuid = ""
#         cnt = 1
#         for sent in list(sentences.values()):
#             print(sent)
#             for word in sent:
#                 if word['Text_Unit_ID'] != tuid:
#                     file_out.write('\n'+'# sent_id = {}'.format(word['Text_Unit_ID'])+'\n') #First line of the header for each sentence. ###Try this: subholder.append(xxx)?
#                     file_out.write('# text = {}'.format(word['Textual_Unit'])+'\n') # Second line of the header for each sentence.
#                     file_out.write('# text_en = {}'.format(word['Translation'])+'\n') # Third line of the header for each sentence.
#                     tuid = word['Text_Unit_ID']
#                     cnt = 1
#                 file_out.write(str(cnt)+"\t"+"\t".join([word['Morph']]+[word['Lemma']]+["X"]+[word['Part_Of_Speech']]+[word['Analysis']]+[word['_']]+['_']+["X"]+[word['Meaning']])+'\n') # This creates the correct order of the ten CONLLU columns for each word in a sentence.
#                 cnt += 1
#             file_out.write('\n')
#     return


# The following function removes all non-alphanumeric characters before comparison
# and checks if a word in list_of_words can be formed by concatenating some of the morphs in list_of_morphs.
# e.g.
# Given list_of_words = abc def ghijk lmn
# Given list_of_morphs = ab c d ef g hi jk lmn
# Output: [(1, 1, 2), (2, 3, 4), (3, 5, 7)] #the index 'tij' below indicates that the t-th word in the sentence is concatenated by the the i-th to j-th morphs in list_of_words.

#def check_concatenations(list_of_words, list_of_morphs):
#    words = [re.sub("[^0-9a-zA-Z]+", '', x) for x in list_of_words] # uses the regex library to remove all non-alphanumeric characters before comparison
#    morphs = [re.sub("[^0-9a-zA-Z]+", '', x) for x in list_of_morphs] # "
#    word_y = 0 # iterator
#    morph_y = 0 # "
#    tij = [] # initialization
#    accumulated = '' # empty accumulated string
#    for j in range(len(morphs)): # loops over every morph
#        accumulated += morphs[j]
#        if accumulated == words[word_y]: # A concatenated string matches a word in a sentence.
#            if morph_y != j:
#                tij.append((word_y, morph_y+1, j+1)) # a concatentated string is formed
#            morph_y = j + 1 # moves on to the next morph
#            accumulated = '' # resets the accumulated string
#            word_y += 1 # moves on to the next word
#    return tij


def write_out(filename, sentences):
    with open(filename, 'w', encoding='utf-8') as file_out:
        tuid = ""
        cnt = 1
        allactlists = []
        for sent in list(sentences.values()):

            # The following function splits the sentence (second line of the header) into words and gets their morphs in preparation for generating concatenated results.

            list_of_words = None
            list_of_morphs = []
            for word in sent:
                if word['Text_Unit_ID'] != tuid:
                    list_of_words = getpunct(word)
                list_of_morphs.append((word['Morph'],word['Text_Unit_ID'],word['Translation'],word['Textual_Unit']))
            tij, aclist = check_concatenations3(list_of_words, list_of_morphs, sent)

            # The following function rearranges the data into a CONLLU-style format, and if concatenated strings are found, prints the results (**currently only to the interim file**).

            for word in sent:
                if word['Text_Unit_ID'] != tuid:
                    file_out.write('\n'+'# sent_id = {}'.format(word['Text_Unit_ID'])+'\n') #First line of the header for each sentence. ###Try this: subholder.append(xxx)?
                    file_out.write('# text = {}'.format(word['Textual_Unit'])+'\n') # Second line of the header for each sentence.
                    file_out.write('# text_en = {}'.format(word['Translation'])+'\n') # Third line of the header for each sentence.
                    #file_out.write('# text_aclist ={}'.format(str(aclist)+'\n'))
                    tuid = word['Text_Unit_ID']
                    cnt = 1
                if tij != []:
                    t, i, j = tij[0]
                    if cnt == i and i != j:
                        interimid = (str(i)+'-'+str(j))
                        file_out.write(str(i)+'\t'+list_of_words[t]+f'	_	_	_	_	_	_	_	tuple={interimid}\n')
                        tij.pop(0)
                    elif cnt == i and i == j:
                        file_out.write(str(i)+'\t'+list_of_words[t]+f'	{list_of_words[t]}	PUNCT	punctuation	_	_	_	_	_\n')
                        tij.pop(0)
                file_out.write(str(cnt)+"\t"+"\t".join([word['Morph']]+[word['Lemma']]+["X"]+[word['Part_Of_Speech']]+[word['Analysis']]+[word['_']]+['_']+["X"]+[word['Meaning']])+'\n') # This creates the correct order of the ten CONLLU columns for each word in a sentence.
                cnt += 1
            file_out.write('\n')
            allactlists.append(aclist)
    return allactlists

def automate_rearrangement(list_of_sentences):

    for sent in list_of_sentences:

        reassignids(sent)
        sortsent(sent)
        allchunks = checkchunkorder(sent)
        changechunkorder(allchunks, sent)
        changeid2(sent) #insert sent,punctseen for testing
        changechunkids(sent)
        change_head(sent)
        del_old_stuff(sent)

    return list_of_sentences


#The following function adds final punctuation.

def insert_sentence_final_punctuation(list_of_sentences):

    for sent in list_of_sentences:

        if sent.metadata['text'].endswith('. . -'):
            suffix = '. . -'
        if sent.metadata['text'].endswith('. .'):
            suffix = '. .'
        elif sent.metadata['text'].endswith('.'):
            suffix = '.'
        elif sent.metadata['text'].endswith('·'):
            suffix = '·'
        else:
            return

        punct = {'id': '_', 'form': suffix, 'lemma': suffix, 'upos': 'PUNCT', 'xpos': 'punctuation', 'feats': '_', 'head': '_', 'deprel': '_', 'deps': '_', 'misc': '_'}

        sent.append(punct)

        for count, word in enumerate(sent):
            if word['id'] == '_':
                word['id'] = sent[count-1]['id'] + 1

#The following function opens the CONLLU file and applies the change_all_analyses function to it.
#It writes the rearranged data to a new file (in the intro to this script called "name_of_final_output_file").

def conlluit(filename1, filename2):
    with open(filename1, 'r', encoding='utf-8') as conllu_file:
        read_file = conllu_file.read()
        parsed_data = parse(read_file)
        conllu_sentences = [item for item in parsed_data]
        change_all_analyses(conllu_sentences)
        upos_finder(conllu_sentences)
        do_all_deprel(conllu_sentences)
        automate_rearrangement(conllu_sentences)
        insert_sentence_final_punctuation(conllu_sentences)
        conllu_sentences_with_feats = [item.serialize() for item in conllu_sentences]
        file_out = open(filename2, 'w', encoding='utf-8')
        [file_out.write(item) for item in conllu_sentences_with_feats]
    return conllu_sentences


#The following statement enables the python script to be run at the command line.

if __name__ == "__main__":
    write_out(sys.argv[2], automation(sys.argv[1]))
    conlluit(sys.argv[2], sys.argv[3])


# ========================================================================================================================================================================================================
# ========================================================================================================================================================================================================
# ========================================================================================================================================================================================================
# ========================================================================================================================================================================================================

"""

Aug 10 update below

Fix the compounding issue with prefixes. > This is basically done, but problems remain if the elements of a compound aren't in the proper order.

Rembember that the remove dummy preverb function currently assumes that it always starts the verbal morph. Hopefully that is true.

Remember to fix the relative function so that it doesn't necessarily assume that "rel" is in analysis. > Remember to fix this see comment in analyze_rel_in

Remember to add a function to make verbal nouns have the feature VerbForm=Vnoun

Remember to recheck act and pass assignment.

Remember to figure out how to fix the problem relating to the deletion of the features of the subordinate negative. Also, add a version of the adjective degree function to edit_conllu to
add degrees to previously seen texts.
"""
