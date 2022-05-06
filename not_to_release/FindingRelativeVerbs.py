
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Updated Fri May 6 2022
@author elliottlash
DFG project
Georg-August-Universität Göttingen
Sprachwissenschaftliches Seminar

"""

# ========================================================================================================================================================================================================
#
# This python script finds relative verbs with the RelType Other and splits creates two lists: 
# one with sentences containing verbs where Other is the correct designation, and one where Other may be wrong. The latter list saved in a text file for reference.
#
# ========================================================================================================================================================================================================

import os
from conllu import parse

os.chdir('/Users/elliottlash/Documents/GitHub/UD_Old_Irish-CritMinorGlosses/') #Change this to the directory where the corpus is.
output_file = open("verbs_to_ceck.txt", "w")
check_other = []
other_good = []

def open_conllu(filename):
	sentences = [item for item in parse(open(filename, 'r', encoding='utf-8').read())]
	return sentences

sentence_list = open_conllu('sga_critminorglosses-ud-test.conllu')

for sentence in sentence_list:
	for count, word in enumerate(sentence):
		if word['upos'] == 'VERB' and "ō" not in word['lemma'] and word['feats'].get('RelType') and word['feats']['RelType'] == 'Other':
			if count >= 1 and sentence[count-1]['upos'] == 'ADP' or (sentence[count-1]['xpos'] == 'pronoun_relative'
                                                                         and sentence[count-1]['feats'].get('PronType')
                                                                         and sentence[count-1]['feats']['PronType'] == 'Rel'):
				other_good.append(sentence.metadata['sent_id'])
			else:
				check_other.append(sentence.metadata['sent_id'])

for sentence_id in check_other:
    output_file.write(sentence_id + "\n")
    output_file.close
