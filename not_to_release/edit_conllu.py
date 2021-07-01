#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Updated Mon June 28 2021
@author elliottlash
DFG project
Georg-August-Universität Göttingen
Sprachwissenschaftliches Seminar

"""

import itertools
import os
import sys
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

# Part 1. Editing the deps column in conllu file.

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
        word['deps'] = f"{word['head']}:{word['deprel']}"


#The following function combines the main editing functions and creates a new conllu file.
def do_all(fileout, list_of_sentences):
    [fill_deps_in(item) for item in list_of_sentences]
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
