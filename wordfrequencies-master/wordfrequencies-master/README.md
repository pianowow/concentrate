wordfrequencies
===============

Simple table of word frequencies, derived from Google Ngram corpora.

words-all.txt is a tab-separated file, one word per line, followed by the total
number of times the word was seen in Google's scanned books from the past century. Any word
with a capital letter was ignored.

words.txt is a subset of words-all.txt, corresponding to words found in /usr/share/dict/words 
on Mac OS X 10.7. Note that the words containing capital letters will not be found in this file.
The program selecter.pl can be used to compile similar subsets.

These files were based on the 1-gram files in the 20120701 release[1] of Google Ngram's corpora.
Individual files for each letter were created with the freqaz script, which calls the freq.pl
script. Then these individual files were sorted, and then merged with sort -m into words-all.txt.


[1] http://storage.googleapis.com/books/ngrams/books/datasetsv2.html


