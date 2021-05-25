#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Fri May 7 2021

@author elliottlash

DFG project
Georg-August-Universität Göttingen
Sprachwissenschaftliches Seminar
"""

import csv
import itertools
import os
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
# At the command line type first os.chdir('/path to file/') and then data_file='name_of_csv_file'. The variable name "data_file" can be used in the functions in section 6 to read this file.
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
# Section 6. Automating the functions in Sections 1 - 5. 
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
	sentencesOD = OrderedDict()
	column_names = data[0] # Gets the column names
	all_rows = data[1:]  # gets the textual unit rows
	for row in all_rows: # Separates them into text_unit_id (id) and other values
		id = str(row[1])
		values = row # print(list(zip(column_names, values)))
		sentenceDict = dict(zip(column_names, values)) # converts them into a dict # print(sentenceDict)
		if id in sentencesOD: # checks if sentence has been added to the textual unit dictionary before and adds i
			sentencesOD[id] = sentencesOD[id] + [sentenceDict]
		else: # otherwise creates a new textual unit dictionary and adds the sentence to the dictionary
			sentencesOD[id] = [sentenceDict]
	return sentencesOD


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

def remove_true_infixed_pronouns_in(sentence, list_of_verbs, list_of_pronouns):
    for verb, pron in list(itertools.product(list_of_verbs, list_of_pronouns)):
        if pron['Stressed_Unit'] == verb['Stressed_Unit']:
            if pron['Morph'] in verb['Morph']:
                sentence.remove(pron)
	    #elif pron['Morph'] not in verb['Morph']:   >>> Only in interactive session
            #    print(f"{pron['Morph']} not deleted.") >>> Only in interactive session
    
# This function combines the above three functions.

def remove_all_extraneous_info_in(list_of_sentences):
    remove_relative_particles_in(list_of_sentences)
    remove_preverbs_in(list_of_sentences)
    remove_null_in(list_of_sentences)


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
				
def analyze_person_in_prepositions(input_data):
    for tok in input_data:
        for key in tok["feats"].copy().keys():
            if tok["xpos"] == "preposition":
                if "1" in key:
                    tok["feats"]["Person"] = "1"
                elif "2" in key:
                    tok["feats"]["Person"] = "2"
                elif "3" in key:
                    tok["feats"]["Person"] = "3"


#The following funciton analyses number in prepositions and possessives.
#Note that this could be expanded to cover all pronouns.
                    
def analyze_number_in_prepositions(input_data):
    for tok in input_data:
        for key in tok["feats"].copy().keys():
            if tok["xpos"] == "preposition":
                if "sg." in key:
                    tok["feats"]["Number"] = "Sing"
                elif "pl." in key:
                    tok["feats"]["Number"] = "Plur"

                    
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

#This deletes keys with null values in the "feats" dictionary.
            
def delete_null_values_in(input_data):
	x = "No_Features"
	for tok in input_data:
		for key, value in tok["feats"].copy().items():
			if x != key and tok["feats"][key] == None:
				del word["feats"][key]

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
    return input_data

#The following function applies some of the above functions to the data to change the analysis of prepositions and possessives.

def change_preposition_analysis(input_data):
    analyze_person_in_prepositions(input_data)
    analyze_number_in_prepositions(input_data)
    return input_data


#The following function combines the functions change_substantive_analysis, change_verb_analysis, change_preposition_and_possessive_analysis, and delete_null_values_in.
    
def change_all_analyses(input_data):
    new_substantives = [change_substantive_analysis(item) for item in input_data]
    new_verbs = [change_verb_analysis(item) for item in input_data]
    new_preps_and_poss = [change_preposition_analysis(item) for item in input_data]
    null_feats = [delete_null_values_in(item) for item in input_data]
    output_data = [item.serialize() for item in input_data]
    return output_data


# ========================================================================================================================================================================================================


#Section 6: Automating the functions in Sections 1 - 5.
#******************************************************


#The following function opens a csv file, does some preprocessing (see section 1), and returns the data as a list.

def read_in_with_columns(filename):
    with open(filename, encoding ='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter =',', skipinitialspace=True)
        output_data = [row for row in csv_reader]
        new_output = [row.pop(0) for row in output_data]
        preprocessing(output_data)
    return output_data


#The following function combines the function read_in_with_columns and the functions in sections 2 - 4.

def automation(filename):
    data = read_in_with_columns(filename)
    sentences = make_dictionary_of_sentences_out_of(data)
    look_for_relative_or_infixed_verbs_in_all(sentences)
    remove_all_extraneous_info_in(sentences)
    compound_detector(sentences)
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
                file_out.write(str(cnt)+"\t"+"\t".join([word['Morph']]+[word['Lemma']]+["X"]+[word['Part_Of_Speech']]+[word['Analysis']]+['_']+['_']+["X"]+[word['Gloss=Meaning']])+'\n') # This creates the correct order of the ten CONLLU columns for each word in a sentence.
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
        conllu_sentences_with_feats = [item.serialize() for item in conllu_sentences]
        file_out = open(filename2, 'w', encoding='utf-8')
        [file_out.write(item) for item in conllu_sentences_with_feats]
    return


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
