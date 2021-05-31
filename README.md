# UD_Old_Irish-CritMinorGlosses

# Summary

UD Old Irish-CritMinor Glosses is conversion of the Old Irish "Minor Glosses", originally published as part of the Corpus Palaeohibernicum (CorPH) (https://chronhib.maynoothuniversity.ie/chronhibWebsite).

# Introduction

The  from the Old Irish "Minor Glosses" are a heterogenous collection of glosses from Latin manuscripts written between the 7th and the 10th centuries. The Latin texts, which have not been parsed,include a number of important Medieval genres: computistics, New and Old testament commentary as well as the Bible itself, patristic works, classical Roman literature (esp. Virgil), canon law, grammatical treatises etc. 

The following texts are currently available: \
S0023: Laon Cassiodorus Minor Glosses (16 sentences). \
S0050: Turin Mark Commentary Minor Glosses (sentences 1—50).

Tokenization, Lemmatization and morphological annotation is derived from the CorPH annotation (Stifter et al. 2021) and conversion to UD CONLLU format was designed by Elliott Lash (Georg-August-Universität Göttingen). Data from Corpus Palaeohibernicum was downloaded as csv files and then reformatted as CONLLU with two python scripts. The syntactic annotation is wholly new. Except for certain modifiers which were tagged automatically, the head and deprel columns for each word were added manually by Elliott Lash and Wai Ying (Ruby) Ku. The deps column was filled in automatically.

# Acknowledgments

The work for this database was funded by the Deutsche Forschungsgemeinschaft.

Thanks are due to Prof. David Stifter (Maynooth University) and the rest of the ChronHib team (https://chronhib.maynoothuniversity.ie/chronhibWebsite/meet-the-team) for creating CorPH, which has allowed easy conversion of the data to UD. Special acknowledgements are due to Godstime Osorobo (Maynooth University) for helping to develop some of the python code used in reformatting the data to CONLLU format, and Dustin Bowers (University of Arizona) for providing further input in the python code. The inspiration for converting the data to UD comes from Prof. Stavros Skopeteas (Georg-August-Universität Göttingen). Wai Ying (Ruby) Ku's work to the data has been of immense help.

<pre>
=== Machine-readable metadata (DO NOT REMOVE!) ================================
Data available since: UD ?
License: ?
Includes text: yes
Genre: nonfiction bible
Lemma: converted from manual
UPOS: converted from manual
XPOS: converted from manual
Feature: converted from manual
Relations: manual native
Contributors: Lash, Elliott; Ku, Wai Ying (Ruby)
Contributing: here
Contact: elliottjamesfrick.lash@uni-goettingen.de
===============================================================================
<pre>
