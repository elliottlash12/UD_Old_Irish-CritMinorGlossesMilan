#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

This will fix previously made conllu files.

"""

import itertools
import os
from conllu import parse

os.chdir('/Users/elliottlash/Documents/GitHub/UD_Old_Irish-CritMinorGlosses/')

#This function opens a file and creates a list of sentences. To run, write: f = 'x', new_sentences_list(f).
def new_sentences_list(filename):
    conllu_file = open(filename, "r", encoding="utf-8")
    data = conllu_file.read()
    parsed_data = parse(data)
    sentences = [a_sentence for a_sentence in parsed_data]
    return sentences


# ========================================================================================================================================================================================================
# ========================================================================================================================================================================================================
# Part 1: These functions will eventually be part of "current_conllu_maker.py".
# At the moment, they are only really relevant for files that are only partially complete after "current_conllu_maker.py" runs.


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
                    
#This function deletes keys with null values in the "feats" dictionary.
#What to do with the "No_Features=_" or the "_" case?
def delete_null_values_in(a_sentence):
    x = "No_Features"
    for word in a_sentence:
        if word["feats"] is not None:
            for key, value in word["feats"].copy().items():
                if x != key and word["feats"][key] is None:
                    del word["feats"][key]


#This function fills the deps column in the conllu file.
def fill_deps_in(a_sentence):
    for count, word in enumerate(a_sentence):
        a_sentence[count]["deps"] = f'{a_sentence[count]["head"]}:{a_sentence[count]["deprel"]}'


#The following function combines the main editing functions and creates a new conllu file.  
def do_all(list_of_sentences, fileout):
#    [analyze_person_in_prepositions_and_possessives_in_(item) for item in list_of_sentences]
#    [analyze_number_in_prepositions_and_possessives_in_(item) for item in list_of_sentences]
    [delete_null_values_in(item) for item in list_of_sentences] #Right now this deletes too much info.
    [fill_deps_in(item) for item in list_of_sentences]
    new_conllu = [item.serialize() for item in list_of_sentences]
    file_out = open(fileout, 'w', encoding='utf-8')
    [file_out.write(item) for item in new_conllu]
    return list_of_sentences


# ========================================================================================================================================================================================================
# ========================================================================================================================================================================================================


# Part 2
# The following functions should be used after "current_conllu_maker.py" has created a conllu_file.

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
			

# ========================================================================================================================================================================================================

# Part 3
#The following functions fill deprel for various function words:

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

# ========================================================================================================================================================================================================

# Part 4
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

# Part 5
# Functions to assign values to the features in the feats column.

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

#Note the following functions assume that the function assign_value_to_definite has already been applied to the data.
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

def assign_person_to_pronouns(a_sentence):
    for word in a_sentence:
        if 'pron' in word['lemma'] and word['xpos'] == 'pronoun_independent' or word['xpos'] == 'pronoun_possessive':
            if '1' in word['lemma']:
                word['feats']['Person'] = '1'
            elif '2' in word['lemma']:
                word['feats']['Person'] = '2'
            elif '3' in word['lemma']:
                word['feats']['Person'] = '3'
