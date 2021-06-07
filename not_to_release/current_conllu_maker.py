#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Fri May 7 2021
Updated Wed June 4 2021
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
# Section 2. A function to convert the data into a dictionary of key:value pairs consisting of sentence_numbers:list_of_words. 
#
# Section 3. Functions to process the features of one word based on the features of another.
#
#    a. Functions to update the analysis of verbs based on the presence of relative particles.
#    b. Functions to update the analysis of verbs based on the presence of infixed pronouns.
#    c. Functions to remove subelements of compounds. 
#
# Section 4. Functions to remove extraneous information.
#
# Section 5. Functions to convert the data to CONLLU format.
#
# Section 6. Functions to fill in the upos and deprels columns of a CONLLU file.
#
# Section 7. Automating the functions in Sections 1 - 5.
#
#
# ========================================================================================================================================================================================================
# ========================================================================================================================================================================================================

#Section 1: Fuctions to preprocessing the data to change the contents of certain cells in various columns 
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
        if item[6] == "Yes" and ".rel." not in item[5]:
            item[5] = item[5] + "rel."
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
    for item in input_data:
        gloss = "Gloss="
        item[9] = gloss + item[9]


#The following function combines the previous six preprocessing functions into one.
    
def preprocessing(input_data):
    preprocess_1(input_data)
    preprocess_2(input_data)
    preprocess_3(input_data)
    preprocess_4(input_data)
    preprocess_5(input_data)
    preprocess_6(input_data)
    return


# ========================================================================================================================================================================================================


#Section 2: A function to convert the data into a dictionary of key:value pairs consisting of sentence_numbers:list_of_words
#***************************************************************************************************************************


#The following functon makes an ordered dictionary whose values are sentences which consist of a list of dictionaries of word:feature pairs

def make_dictionary_of_sentences_out_of(data):
    sentences_ordered_dict = OrderedDict()
    column_names = data[0] # Gets the column names
    all_rows = data[1:]  # gets the textual unit rows
    for row in all_rows: # Separates them into text_unit_id (id) and other values
        id = str(row[1])
        values = row # print(list(zip(column_names, values)))
        sentence_dict = dict(zip(column_names, values)) # converts them into a dict # print(sentenceDict)
        if id in sentences_ordered_dict: # checks if sentence has been added to the textual unit dictionary before and adds i
            sentences_ordered_dict[id] = sentences_ordered_dict[id] + [sentence_dict]
        else: # otherwise creates a new textual unit dictionary and adds the sentence to the dictionary
            sentences_ordered_dict[id] = [sentence_dict]
    return sentences_ordered_dict


# ========================================================================================================================================================================================================


#Section 3: Functions to process the features of one word based on the features of another
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
                    verb['Analysis'] =  verb['Analysis'] + 'len'
                elif relpart['Lemma'] == 'nas.rel.particle':
                    answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' is a nasalized relative verb.'
                    ans.append(answ)
                    verb['Analysis'] =  verb['Analysis'] + 'nas'
            elif pron['Morph'] not in verb['Morph']:
                if relpart['Lemma'] == 'len.rel.particle':
                    answ = 'The pronoun ' + pron['Morph'] + ' which has ID number ' + pron['ID'] + ' is a lenited class C pronoun.'
                    ans.append(answ)
                    pron['Analysis'] =  pron['Analysis'] + '.len'
                elif relpart['Lemma'] == 'nas.rel.particle':
                    answ = 'The pronoun ' + pron['Morph'] + ' which has ID number ' + pron['ID'] + ' is a nasalized class C pronoun.'
                    ans.append(answ)
                    pron['Analysis'] =  pron['Analysis'] + '.nas'
    return ans


def compare_verbs_and_relative_particles_in(list_of_verbs, list_of_relparts):
    ans = []
    for verb, relpart in list(itertools.product(list_of_verbs, list_of_relparts)):
        if verb['Stressed_Unit'] == relpart['Stressed_Unit']:
            if relpart['Lemma'] == 'len.rel.particle':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' is a lenited relative verb.'
                ans.append(answ)
                verb['Analysis'] =  verb['Analysis'] + 'len'
            elif relpart['Lemma'] == 'nas.rel.particle':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' is a nasalized relative verb.'
                ans.append(answ)
                verb['Analysis'] =  verb['Analysis'] + 'nas'
    return ans


def compare_verbs_and_infixed_pronouns_in(list_of_verbs, list_of_prons):
    ans = []
    for verb, pron in list(itertools.product(list_of_verbs, list_of_prons)): 
        if verb['Stressed_Unit'] == pron['Stressed_Unit'] and pron['Morph'] in verb['Morph']:
            if pron['Lemma'] == '1sg.inf.pron.':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj1sg.' + pron['Analysis'] + ']'
            elif pron['Lemma'] == '2sg.inf.pron.':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj2sg.' + pron['Analysis'] + ']'
            elif pron['Lemma'] == '1pl.inf.pron.':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj1pl.' + pron['Analysis'] + ']'
            elif pron['Lemma'] == '2pl.inf.pron.':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj2pl' + pron['Analysis'] + ']'
            elif pron['Lemma'] == '3sg.masc.inf.pron.':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj3sg.masc.' + pron['Analysis'] + ']'
            elif pron['Lemma'] == '3sg.fem.inf.pron.':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj3sg.fem.' + pron['Analysis'] + ']'
            elif pron['Lemma'] == '3sg.neut.inf.pron.':
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj3sg.neut.' + pron['Analysis'] + ']'
            elif pron['Lemma'] == '3pl.inf.pron.': 
                answ = 'The verb ' + verb['Morph'] + ' which has ID number ' + verb['ID'] + ' has a ' + pron['Lemma'] + ' as direct object.'
                ans.append(answ)
                verb['Analysis'] = verb['Analysis'] + 'obj3pl.' + pron['Analysis'] + ']'
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

# The following function removes subelements of compounds. It works if the rows are in the following order: element 1 > element 2 > compound. 
def compound_detector(list_of_sentences):
    for sent in list_of_sentences.values():
        for count, word in enumerate(sent):
            if count+2 < len(sent):
                if sent[count]['Morph'] in sent[count+2]['Morph'] and 'compos.' in sent[count]['Analysis']:
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
            if word['Morph'] == '∅':
                del sent[i]


# This function combines the above three functions.

def remove_all_extraneous_info_in(list_of_sentences):
    remove_relative_particles_in(list_of_sentences)
    remove_preverbs_in(list_of_sentences)
    remove_null_in(list_of_sentences)

# ========================================================================================================================================================================================================

#Interim Testing Section: Functions to automatically add an index to the "Head" column of a CONLLU file.

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

def head_of_article(current_sentence, list_of_dets, list_of_nouns):
    for det, noun in list(itertools.product(list_of_dets, list_of_nouns)):
        if det['Stressed_Unit'] in noun['Stressed_Unit']:
            det['_'] = str(current_sentence.index(noun) + 1)

def head_of_preposition(current_sentence, list_of_preps, list_of_nouns):
    finished_nouns = []
    finished_preps = []
    ignore_list = []
    combo=list(itertools.product(list_of_preps, list_of_nouns))
    for c in combo:
        if c[0]['Stressed_Unit'] in c[1]['Stressed_Unit']:
            if not ignore_list:
                c[0]['_'] = str(current_sentence.index(c[1]) + 1)
                finished_preps.append(c[0])
                finished_nouns.append(c[1])
                ignore_list.append(c)
            elif c[0] in finished_preps:
                ignore_list.append(c)
            elif c[1] in finished_nouns:
                ignore_list.append(c)
            else:
                c[0]['_'] = str(current_sentence.index(c[1]) + 1)
        
def find_head_in(a_sentence, list_of_dets, list_of_nouns, list_of_preps):
    head_of_article(a_sentence, list_of_dets, list_of_nouns)
    head_of_preposition(a_sentence, list_of_preps, list_of_nouns)

def assign_head_in(list_of_sentences):
    for sent in list_of_sentences.values():
        dets, nouns, preps = list_of_dets_and_nouns_in(sent)
        find_head_in(sent, dets, nouns, preps)
        
# ========================================================================================================================================================================================================


#Section 5: Functions to convert the data to CONLLU format
#*********************************************************


# The following series of functions modifies the "Analysis" column of the csv output from CorPH to create the "Feats" (for "Features") column of a CONLLU file.
# The specific goal is to make sure that the "Feats" column consists of a series of key:value pairs, where key = the name of a feature and value = a value for that feature.


# The function case_analysis checks to see if any key in "Feats" contains "nom/acc/gen/dat" and creates a new key:value pair. 

def case_analysis(input_data):
    for tok in input_data:
        for key in tok["feats"].copy().keys():
            if key[0:3] == "nom":
                tok["feats"]["Case"] = "Nom"
            elif key[0:3] == "acc":
                tok["feats"]["Case"] = "Acc"
            elif key[0:3] == "gen":
                tok["feats"]["Case"] = "Gen"
            elif key[0:3] == "dat":
                tok["feats"]["Case"] = "Dat"


# The function number_analysis checks to see if any key in "Feats" contains "sg" or "pl" and creates a new key:value pair.
				
def number_analysis(input_data):
    for tok in input_data:
        for key in tok["feats"].copy().keys():
            if key[4:6] == "sg":
                tok["feats"]["Number"] = "Sing"
            elif key[4:6] == "pl":
                tok["feats"]["Number"] = "Plur"


# The functiongender_analysis checks to see if any key in "Feats" contains "ma/fe/ne" creates a new key:value pair.
    
def gender_analysis(input_data):
    for tok in input_data:
        for key in tok["feats"].copy().keys():
            if key[7:9] == "ma":
                tok["feats"]["Gender"] = "Masc"
            elif key[7:9] == "fe":
                tok["feats"]["Gender"] = "Fem"
            elif key[7:9] == "ne":
                tok["feats"]["Gender"] = "Neut"


#The following funciton analyses  person in prepositions and possessives.
#Note that this could be expanded to cover all pronouns.
				
def analyze_person_in_prepositions_and_possessives_in_(input_data):
    for tok in input_data:
        for key in tok["feats"].copy().keys():
            if tok["xpos"] == "preposition" or tok["xpos"]== "pronoun_possessive" or tok["xpos"] == "particle_pronominal":
                if "1" in key:
                    tok["feats"]["Person"] = "1" 
                elif "2" in key:
                    tok["feats"]["Person"] = "2"
                elif "3" in key:
                    tok["feats"]["Person"] = "3"


#The following funciton analyses number in prepositions and possessives.
#Note that this could be expanded to cover all pronouns.
                    
def analyze_number_in_prepositions_and_possessives_in_(input_data):
    for tok in input_data:
        for key in tok["feats"].copy().keys():
            if tok["xpos"] == "preposition" or tok["xpos"]== "pronoun_possessive" or tok["xpos"] == "particle_pronominal":
                if "sg." in key:
                    tok["feats"]["Number"] = "Sing"
                elif "pl." in key:
                    tok["feats"]["Number"] = "Plur"


#The following functions (case_finder and assign_case) assign a value to the feature Case for prepositions:
#The function assign_case has the drawback that it assigns Acc/Dat to variable prepositions, rather than the actual case in the context.
#It might be that for ambiguous instances, the case value should only be filled in if the feats has acc. or dat.
# (i.e. if the analysis in CorPH already specifies the case). Another way is to use the feats of an associated noun,
#after tagging head/deprels.

def case_finder(a_sentence):
    prep_list=[{'a 7': 'Dat'}, {'acht 2': 'Acc'}, {'al': 'Acc'}, {'amail 1': 'Acc'}, {'ar 1': 'Acc/Dat'}, {'cen': 'Acc'}, {'cenmothá': 'Acc'}, {'co 1': 'Acc'}, {'co 2': 'Dat'}, {'co·rrici': 'Acc'}, {'co·rrici': 'Acc'}, {'coticci': 'Acc'}, {'di': 'Dat'}, {'do 1': 'Dat'}, {'dochumm': 'Gen'}, {'echtar': 'Acc'}, {'eter': 'Acc'}, {'fíad': 'Dat'}, {'fo': 'Acc/Dat'}, {'for': 'Acc/Dat'}, {'fri': 'Acc'}, {'fri': 'Acc'}, {'íar 1': 'Dat'}, {'íarmithá': 'Dat'}, {'imm': 'Acc'}, {'i': 'Acc/Dat'}, {'ingé 1': 'Acc'}, {'ís 1': 'Dat'}, {'la': 'Acc'}, {'ó 1': 'Dat'}, {'oc': 'Dat'}, {'ós 1': 'Dat'}, {'óthá': 'Dat'}, {'re': 'Dat'}, {'sech 1': 'Acc'}, {'tar 1': 'Acc'}, {'tre': 'Acc'}]
    combo = list(itertools.product(a_sentence, prep_list))
    assign_case(combo)

def assign_case(combined_list):
    for count, word in enumerate(combined_list):
        if combined_list[count][0]['xpos'] == 'preposition' and combined_list[count][0]['lemma'] in combined_list[count][1]:
            for key, value in combined_list[count][1].items():
                combined_list[count][0]['feats']['Case'] = value
                
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
                    
# The functions verbal_infixed_person_analysis and verbal_infixed_number_analysis deal with the features of infixed pronouns.

def verbal_infixed_person_analysis(input_data):
    for tok in input_data:
        for key in tok["feats"].copy().keys():
            if tok["xpos"] == "verb" and "obj1" in key:
                tok["feats"]["Person[Obj]"] = "1"
            elif tok["xpos"] == "verb" and "obj2" in key:
                tok["feats"]["Person[Obj]"] = "2"
            elif tok["xpos"] == "verb" and "obj3" in key:
                tok["feats"]["Person[Obj]"] = "3"

def verbal_infixed_number_analysis(input_data):
    for tok in input_data:
        for key in tok["feats"].copy().keys():
            if tok["xpos"] == "verb" and re.findall("obj[123]sg", key):
                tok["feats"]["Number[Obj]"] = "Sing"
            elif tok["xpos"] == "verb" and re.findall("obj[123]pl", key):
                tok["feats"]["Number[Obj]"] = "Plur"


#The verbal_person_analysis checks to see if for rows whose "xpos" value is "verb" any key in "Feats" contains "1/2/3" and creates a new key:value pair.
# Because the analysis of the verb will contain two instances of 1/2/3 in the case of transitive verbs with infixed pronouns, there may be some functionality issues here!				
		
def verbal_person_analysis(input_data):
    for tok in input_data:
        for key in tok["feats"].copy().keys():
            if tok["xpos"] == "verb" and "1" in key:
                tok["feats"]["Person[Subj]"] = "1"
            elif tok["xpos"] == "verb" and "2" in key:
                tok["feats"]["Person[Subj]"] = "2"
            elif tok["xpos"] == "verb" and "3" in key:
                tok["feats"]["Person[Subj]"] = "3"


# The function verbal_number_analysis checks to see if for rows whose "xpos" value is "verb" any key in "Feats" contains "sg" or "pl" and creates a new key:value pair.
				
def verbal_number_analysis(input_data):
    for tok in input_data:
        for key in tok["feats"].copy().keys():
            if tok["xpos"] == "verb" and "sg" in key:
                tok["feats"]["Number[Subj]"] = "Sing"
            elif tok["xpos"] == "verb" and "pl" in key:
                tok["feats"]["Number[Subj]"] = "Plur"


# The function tense_analysis checks to see if any key in "Feats" contains a tag for a tense or the imperative mood ("impv") and creates a new key:value pair.
				
def tense_analysis(input_data):
    for tok in input_data:
        for key in tok["feats"].copy().keys():
            if "pres" in key:
                tok["feats"]["Tense"] = "Pres"
            elif "past" in key:
                tok["feats"]["Tense"] = "Past"
            elif "pret" in key:
                tok["feats"]["Tense"] = "Pret"
            elif "cond" in key:
                tok["feats"]["Tense"] = "Cond"
            elif "impf" in key:
                tok["feats"]["Tense"] = "Impf"
            elif "fut" in key:
                tok["feats"]["Tense"] = "Fut"
            elif "hab" in key:
                tok["feats"]["Tense"] = "Hab"
            elif "impv" in key:
                tok["feats"]["Tense"] = "Pres"


# The function verbal_voice_analysis checks to see whether or not for rows whose "xpos" value is "verb" any key in "Feats" contains "pass" and creates a new key:value pair. 

def voice_analysis(input_data):
    for tok in input_data:
        for key in tok["feats"].copy().keys():
            if tok["xpos"] == "verb" and "pass" in key:
                tok["feats"]["Voice"] = "Pass"
            elif tok["xpos"] == "verb" and "pass" not in key:
                tok["feats"]["Voice"] = "Act"


# The function mood_voice_analysis checks to see whether or not for rows whose "xpos" value is "verb" any key in "Feats" contains ".impv./.subj." or, in the case of the first key in the dictionary,
# neither of them and creates a new key:value pair.
    
def mood_analysis(input_data):
    for tok in input_data:
        for key in tok["feats"].copy().keys():
            if tok["xpos"] == "verb":
                if ".impv." in key:
                        tok["feats"]["Mood"] = "Impv"
                elif ".subj." in key:
                        tok["feats"]["Mood"] = "Subj"
                elif (".impv." not in next(iter(tok["feats"]))) and (".subj." not in next(iter(tok["feats"]))):
                                tok["feats"]["Mood"] = "Ind"
                                

# The function finitness_analysis checks to see if there is a key called "Tense" in "Feats". If so, it creates a new key:value pair.

def finiteness_analysis(input_data):
    for tok in input_data:
        if tok["feats"].copy().get("Tense"):
            tok["feats"]["VerbForm"] = "Fin"

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
                

#The following function applies some of the above functions to the data to change the analysis of substantives (i.e. nouns and adjectives).

def change_substantive_analysis(input_data):
    case_analysis(input_data)
    number_analysis(input_data)
    gender_analysis(input_data)
    return input_data


#The following function applies some of the above functions to the data to change the analysis of verbs.

def change_verb_analysis(input_data):
    verbal_infixed_person_analysis(input_data)
    verbal_infixed_number_analysis(input_data)
    verbal_person_analysis(input_data)
    verbal_number_analysis(input_data)
    tense_analysis(input_data)
    voice_analysis(input_data)
    mood_analysis(input_data)
    finiteness_analysis(input_data)
    analyze_subcat_in_(input_data)
    analyze_object_pron_in_(input_data)
    analyze_augm_in_(input_data)
    analyze_voice_in_(input_data)
    analyze_rel_in(input_data)
    return input_data

#The following function applies some of the above functions to the data to change the analysis of prepositions and possessives.

def change_preposition_analysis(input_data):
    analyze_person_in_prepositions_and_possessives_in_(input_data)
    analyze_number_in_prepositions_and_possessives_in_(input_data)
    analyze_gender_in_prepositions_and_possessives_in_(input_data)
    return input_data

def change_other_analyses(input_data):
    assign_value_to_definite(input_data)
    assign_value_to_poss(input_data)
    assign_value_to_deixis(input_data)
    assign_value_to_prontype(input_data)
    assign_person_to_pronouns(input_data)


#This deletes keys with null values in the "feats" dictionary.
            
def delete_null_values_in(a_sentence):
    x = "No_Features"
    for word in a_sentence:
        if word["feats"] is not None:
            for key, value in word["feats"].copy().items():
                if x != key and word["feats"][key] == "":
                    del word["feats"][key]
                    
#The following function combines the functions change_substantive_analysis, change_verb_analysis, change_preposition_and_possessive_analysis, change_other_analyses, and delete_null_values_in.
    
def change_all_analyses(input_data):
    [change_substantive_analysis(item) for item in input_data]
    [change_verb_analysis(item) for item in input_data]
    [change_preposition_analysis(item) for item in input_data]
    [case_finder(item) for item in input_data]
    [change_other_analyses(item) for item in input_data]
    [delete_null_values_in(item) for item in input_data]
    output_data = [item.serialize() for item in input_data]
    return output_data

# ========================================================================================================================================================================================================

#Section 6: Functions to fill in upos and deprel columns in a conllu file.
#*************************************************************************

#The following functions (assign_upos and upos_finder) assign upos to a word in a sentence in a list of sentences.

def assign_upos(combined_list):
    for count, word in enumerate(combined_list):
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
            word["deprel"] = "case" #This assigns 'case' even to potential mark:prt with verbal nouns.
                                    #It also assigns 'case' to relative prepositiosn before verbs, even though in this instance
                                    #the proper deprel is obl:prep.
           
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
    
# ========================================================================================================================================================================================================


#Section 7: Automating the functions in Sections 1 - 6.
#******************************************************


#The following function opens a csv file, does some preprocessing (see section 1), and returns the data as a list.

def read_in_with_columns(filename):
    with open(filename, encoding ='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter =',', skipinitialspace=True)
        output_data = [row for row in csv_reader]
        [row.pop(0) for row in output_data]
        preprocessing(output_data)
    return output_data


#The following function combines the function read_in_with_columns and the functions in sections 2 - 4.

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

def write_out(filename, sentences):
    with open(filename, 'w',encoding='utf-8') as file_out:
        tuid = ""
        cnt = 1
        for sent in list(sentences.values()):
            for word in sent:
                if word['Text_Unit_ID'] != tuid:
                    file_out.write('\n'+'# sent_id = {}'.format(word['Text_Unit_ID'])+'\n') #First line of the header for each sentence. ###Try this: subholder.append(xxx)?
                    file_out.write('# text = {}'.format(word['Textual_Unit'])+'\n') # Second line of the header for each sentence.
                    file_out.write('# text_en = {}'.format(word['Translation'])+'\n') # Third line of the header for each sentence.
                    tuid = word['Text_Unit_ID']
                    cnt = 1
                file_out.write(str(cnt)+"\t"+"\t".join([word['Morph']]+[word['Lemma']]+["X"]+[word['Part_Of_Speech']]+[word['Analysis']]+[word['_']]+['_']+["X"]+[word['Gloss=Meaning']])+'\n') # This creates the correct order of the ten CONLLU columns for each word in a sentence.
                cnt += 1
            file_out.write('\n')
    return                    


#The following function opens the CONLLU file and applies the change_all_analyses function to it.
#It writes the rearranged data to a new file (in the intro to this script called "name_of_final_output_file").

def conlluit(filename1, filename2):
    with open(filename1, "r", encoding="utf-8") as conllu_file:
        read_file = conllu_file.read()
        parsed_data = parse(read_file)
        conllu_sentences = [item for item in parsed_data]
        change_all_analyses(conllu_sentences)
        upos_finder(conllu_sentences)
        do_all_deprel(conllu_sentences)
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
May 7 update below
Remember to continue to incorporate post-conllu file editing functions.
Also remember that csv files downloaded from CorPH will be in the wrong order if they contain more than 9 sentences. This is because the sentence portion of
Text_Unit_ID has no leading zeroes so that S000X-1 is followed by S000X-10. S000X-10 will also be followed by S000X-100 in texts with more than 99 sentences.
There is a rather laborious workaround for this in libreoffice. Perhaps, sorting can occur during the conllu editing process.
Remeber to delete Index!
Fix the compounding issue with prefixes.
Rembember that the remove dummy preverb function currently assumes that it always starts the verbal morph. Hopefully that is true.
"""
