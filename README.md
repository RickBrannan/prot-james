# prot-james
An effort at creating an openly available, morphologically annotated edition of the _Protevangelium of James_.

## License
This work (data) is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License
([CC-BY-SA-4.0](http://creativecommons.org/licenses/by-sa/4.0/)).

The code (python scripts) are licensed under the MIT License.

## Protevangelium of James Greek Morphology

This project uses the OpenText.org edition of the _Protevangelium of James_ as its basis, which OpenText.org have 
licensed as [CC-BY-SA-4.0](http://creativecommons.org/licenses/by-sa/4.0/). Regarding source and original license 
of the Greek text, the following note is in the data provided by OpenText.org:

> This text is freeware. Originally transcribed by Rolf Mainz in Bremen, Germany on an Atari computer (!). Transferred 
> to PC formate by Wieland Willker. The text is basically a mixture of codex C (Paris 1454, 10th CE, considered by 
> Tischendorf as the best) and the text of Papyrus Bodmer 5, which was unknown to Tischendorf. It is not really a 
> critical text, but it is nevertheless a good text and can be used for classroom purposes. Editions used include 
> E. Strycker _La forme la plus ancienne du Protevangile de Jaques_, Bruxelles 1961; H. R. Smid _Protevangelium Jacobi_,
> Groningen 1965

Note that the OpenText.org edition indicates one variant in the text at 15.2, where αρχιερυς is noted as a variant to 
ιερυς. 

In typical Rick fashion, I'm starting with the stupidest thing that might work, and that means mooching off of Tauber's 
other project, [MorphGNT](https://github.com/MorphGNT), also licensed CC-BY-SA 4.0. Like it is so stupid. I'm just 
taking forms that happen in the Greek NT (SBLGNT) and migrating the morph data over to the _Protevangelium of James_ 
based on (normalized) word matches.

The output currently mimicks the record style of MorphGNT. If I haven't got the value yet, I just insert `??` as 
appropriate. Note that I've also added a column for "language" to the record. 

## Current Status

For the Greek, I'm using [this model from HuggingFace](https://huggingface.co/Jacobo/grc_proiel_lg), which
I've dabbled with before for lemma generation. I'm going to initially use the lemma and morph capabilities,
but it has some named entity recognition capabilities as well that I'd like to play around with.

For Greek words unknown by Tauber's MorphGNT, I am now using the `grc_proiel_lg` form of the model to 
include lemmas and morph. These are untested and not reviewed. I've done some comparisons of words known
by MorphGNT against the morph generated for them and found agreement, but it isn't perfect. Some known areas
of trouble include:

* **Crasis.** The model splits a crasis like καγω into two tokens, whereas MorphGNT treats it as one. These are 
currently causing some problems.
* **Morph mismatches.** The model doesn't emit morphology as traditionally thought of by most Koine/Hellenistic 
Greek Grammars. For example, the model has tense values of past, present, and future along with Aspect values of 
perfective and imperfective. I'm unsure how well this data can be combined to map over to include as 'tense' stuff 
like aorist, perfect, imperfect, and pluperfect. But we'll see.

All that said, there is data now available that has some sort of (unproven, untested, and wrong in spots) morphology for
almost every available Greek token.

## Codes and Fields

### Columns

 * book/chapter/verse
   * unlike MorphGNT, I use `BJ.chap.verse` where `chap` is the chapter number and `verse` is the verse number.
 * part of speech
 * parsing code
 * text (including punctuation)
 * word (with punctuation stripped)
 * normalized word (using Tauber's `greek_normalisation` Python library
 * lemma
 * language (`grc`)
 * source (`MorphGNT` or `grc_proiel_lg`). This is source for both lemma and morphology string.

### Part of Speech Code (Greek)

* A- adjective  
* C- conjunction  
* D- adverb  
* I- interjection  
* N- noun
* NP noun, proper (not in Tauber)
* NU number (not in Tauber)
* P- preposition  
* RA definite article  
* RD demonstrative pronoun  
* RI interrogative/indefinite pronoun  
* RP personal pronoun  
* RR relative pronoun  
* TL transliterated (not in Tauber)
* V- verb  
* X- particle  

### Parsing Code (Greek)

 * person (1=1st, 2=2nd, 3=3rd)
 * tense (P=present, I=imperfect, F=future, A=aorist, X=perfect, Y=pluperfect)
 * voice (A=active, M=middle, P=passive)
 * mood (I=indicative, D=imperative, S=subjunctive, O=optative, N=infinitive, P=participle)
 * case (N=nominative, G=genitive, D=dative, A=accusative, V=vocative)
 * number (S=singular, P=plural)
 * gender (M=masculine, F=feminine, N=neuter)
 * degree (C=comparative, S=superlative)
 
## Disclaimer
*Disclaimer:* This is _totally_ an in-my-spare-time and as-I-feel-inspired kind of project. And I don't have a lot of 
spare time. No promises about status and finishing, use at your own risk, etc.
