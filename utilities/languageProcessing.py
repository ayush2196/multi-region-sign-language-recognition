import stanza 
from nltk.parse.stanford import StanfordParser
from nltk.stem import WordNetLemmatizer
from nltk.tree import *
import utilities.stanfordParser as sp
import pprint 
import os
import time
import sys

# Pipeline for stanza (calls spacy for tokenizer)
en_nlp = stanza.Pipeline('en',processors={'tokenize':'spacy'})	
# print(stopwords.words('english'))

# stop words that are not to be included in ISL
stop_words = set(["am","are","is","was","were","be","being","been","have","has","had",
					"does","did","could","should","would","can","shall","will","may","might","must","let"]);

# sentences array
sent_list = [];
# sentences array with details provided by stanza
sent_list_detailed=[];

# word array
word_list=[];

# word array with details provided by stanza 
word_list_detailed=[];

# converts to detailed list of sentences ex. {"text":"word","lemma":""}
def convert_to_sentence_list(text):
	for sentence in text.sentences:
		sent_list.append(sentence.text)
		sent_list_detailed.append(sentence)


# converts to words array for each sentence. ex=[ ["This","is","a","test","sentence"]];
def convert_to_word_list(sentences):
	temp_list=[]
	temp_list_detailed=[]
	for sentence in sentences:
		for word in sentence.words:
			temp_list.append(word.text)
			temp_list_detailed.append(word)
		word_list.append(temp_list.copy())
		word_list_detailed.append(temp_list_detailed.copy())
		temp_list.clear();
		temp_list_detailed.clear();

# removes stop words
def filter_words(word_list):
	temp_list=[];
	final_words=[];
	# removing stop words from word_list
	for words in word_list:
		temp_list.clear();
		for word in words:
			if word not in stop_words:
				temp_list.append(word);
		final_words.append(temp_list.copy());
	# removes stop words from word_list_detailed 
	for words in word_list_detailed:
		for i,word in enumerate(words):
			if(words[i].text in stop_words):
				del words[i];
				break;
	
	return final_words;

# removes punctutation 
def remove_punct(word_list):
	# removes punctutation from word_list_detailed
	for words,words_detailed in zip(word_list,word_list_detailed):
		for i,(word,word_detailed) in enumerate(zip(words,words_detailed)):
			if(word_detailed.upos=='PUNCT'):
				del words_detailed[i];
				words.remove(word_detailed.text);
				break;

# lemmatizes words
def lemmatize(final_word_list):
	for words,final in zip(word_list_detailed,final_word_list):
		for i,(word,fin) in enumerate(zip(words,final)):
			if fin in word.text:
				if(len(fin)==1):
					final[i]=fin;
				else:
					final[i]=word.lemma;					
	for word in final_word_list:
		print("final_words",word);

def label_parse_subtrees(parent_tree):
    tree_traversal_flag = {}

    for sub_tree in parent_tree.subtrees():
        tree_traversal_flag[sub_tree.treeposition()] = 0
    return tree_traversal_flag

# handles if noun is in the tree
def handle_noun_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree):
    # if clause is Noun clause and not traversed then insert them in new tree first
    if tree_traversal_flag[sub_tree.treeposition()] == 0 and tree_traversal_flag[sub_tree.parent().treeposition()] == 0:
        tree_traversal_flag[sub_tree.treeposition()] = 1
        modified_parse_tree.insert(i, sub_tree)
        i = i + 1
    return i, modified_parse_tree

# handles if verb/proposition is in the tree followed by nouns
def handle_verb_prop_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree):
    # if clause is Verb clause or Proportion clause recursively check for Noun clause
    for child_sub_tree in sub_tree.subtrees():
        if child_sub_tree.label() == "NP" or child_sub_tree.label() == 'PRP':
            if tree_traversal_flag[child_sub_tree.treeposition()] == 0 and tree_traversal_flag[child_sub_tree.parent().treeposition()] == 0:
                tree_traversal_flag[child_sub_tree.treeposition()] = 1
                modified_parse_tree.insert(i, child_sub_tree)
                i = i + 1
    return i, modified_parse_tree

# modifies the tree according to POS
def modify_tree_structure(parent_tree):
    # Mark all subtrees position as 0
    tree_traversal_flag = label_parse_subtrees(parent_tree)
    # Initialize new parse tree
    modified_parse_tree = Tree('ROOT', [])
    i = 0
    for sub_tree in parent_tree.subtrees():
        if sub_tree.label() == "NP":
            i, modified_parse_tree = handle_noun_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree)
        if sub_tree.label() == "VP" or sub_tree.label() == "PRP":
            i, modified_parse_tree = handle_verb_prop_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree)

    # recursively check for omitted clauses to be inserted in tree
    for sub_tree in parent_tree.subtrees():
        for child_sub_tree in sub_tree.subtrees():
            if len(child_sub_tree.leaves()) == 1:  #check if subtree leads to some word
                if tree_traversal_flag[child_sub_tree.treeposition()] == 0 and tree_traversal_flag[child_sub_tree.parent().treeposition()] == 0:
                    tree_traversal_flag[child_sub_tree.treeposition()] = 1
                    modified_parse_tree.insert(i, child_sub_tree)
                    i = i + 1

    return modified_parse_tree

# converts the text in parse trees
def reorder_eng_to_isl(input_string):
	sp.download_required_packages();
	# check if all the words entered are alphabets.
	count=0
	for word in input_string:
		if(len(word)==1):
			count+=1;

	if(count==len(input_string)):
		return input_string;
	
	parser = StanfordParser()
	# Generates all possible parse trees sort by probability for the sentence
	possible_parse_tree_list = [tree for tree in parser.parse(input_string)]
	print("i am testing this",possible_parse_tree_list)
	# Get most probable parse tree
	parse_tree = possible_parse_tree_list[0]
	# print(parse_tree)
	# Convert into tree data structure
	parent_tree = ParentedTree.convert(parse_tree)
	
	modified_parse_tree = modify_tree_structure(parent_tree)
	
	parsed_sent = modified_parse_tree.leaves()
	return parsed_sent

# final word list
final_words= [];
# final word list that is detailed(dict)
final_words_detailed=[];

# pre processing text
def pre_process_text(text):
	remove_punct(word_list)
	final_words.extend(filter_words(word_list));
	lemmatize(final_words)

# checks if sigml file exists of the word if not use letters for the words
def final_output(input):
	final_string=""
	valid_words=open("words.txt",'r').read();
	valid_words=valid_words.split('\n')
	fin_words=[]
	for word in input:
		word=word.lower()
		if(word not in valid_words):
			for letter in word:
				# final_string+=" "+letter
				fin_words.append(letter);
		else:
			fin_words.append(word);

	return fin_words

final_output_in_sent=[];

# converts the final list of words in a final list with letters seperated if needed
def convert_to_final():
	for words in final_words:
		final_output_in_sent.append(final_output(words));

# takes input from the user
def take_input(text):
	test_input=text.strip().replace("\n","").replace("\t","")
	test_input2=""
	if(len(test_input)==1):
		test_input2=test_input;
	else:
		for word in test_input.split("."):
			test_input2+= word.capitalize()+" .";

	# pass the text through stanza
	some_text= en_nlp(test_input2);
	convert(some_text);


def convert(some_text):
	convert_to_sentence_list(some_text);
	convert_to_word_list(sent_list_detailed)

	# reorders the words in input
	for i,words in enumerate(word_list):
		word_list[i]=reorder_eng_to_isl(words)

	# removes punctuation and lemmatizes words
	pre_process_text(some_text);
	convert_to_final();
	remove_punct(final_output_in_sent)
	print_lists();
	

def print_lists():
	print("--------------------Word List------------------------");
	pprint.pprint(word_list)
	print("--------------------Final Words------------------------");
	pprint.pprint(final_words);
	print("---------------Final sentence with letters--------------");
	pprint.pprint(final_output_in_sent)

# clears all the list after completing the work
def clear_all():
	sent_list.clear();
	sent_list_detailed.clear();
	word_list.clear();
	word_list_detailed.clear();
	final_words.clear();
	final_words_detailed.clear();
	final_output_in_sent.clear();
	final_words_dict.clear();


# dict for sending data to front end in json
final_words_dict = {};

#for speech------------

def filter_stop_words(words):
    stopwords_set = set(['a', 'an', 'the', 'is'])
    words = list(filter(lambda x: x not in stopwords_set, words))
    return words


def lemmatize_tokens(token_list):
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = []
    for token in token_list:
        lemmatized_words.append(lemmatizer.lemmatize(token))

    return lemmatized_words


def label_parse_subtrees(parent_tree):
    tree_traversal_flag = {}

    for sub_tree in parent_tree.subtrees():
        tree_traversal_flag[sub_tree.treeposition()] = 0
    return tree_traversal_flag


def handle_noun_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree):
    # if clause is Noun clause and not traversed then insert them in new tree first
    if tree_traversal_flag[sub_tree.treeposition()] == 0 and tree_traversal_flag[sub_tree.parent().treeposition()] == 0:
        tree_traversal_flag[sub_tree.treeposition()] = 1
        modified_parse_tree.insert(i, sub_tree)
        i = i + 1
    return i, modified_parse_tree


def handle_verb_prop_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree):
    # if clause is Verb clause or Proportion clause recursively check for Noun clause
    for child_sub_tree in sub_tree.subtrees():
        if child_sub_tree.label() == "NP" or child_sub_tree.label() == 'PRP':
            if tree_traversal_flag[child_sub_tree.treeposition()] == 0 and tree_traversal_flag[child_sub_tree.parent().treeposition()] == 0:
                tree_traversal_flag[child_sub_tree.treeposition()] = 1
                modified_parse_tree.insert(i, child_sub_tree)
                i = i + 1
    return i, modified_parse_tree


def modify_tree_structure(parent_tree):
    # Mark all subtrees position as 0
    tree_traversal_flag = label_parse_subtrees(parent_tree)
    # Initialize new parse tree
    modified_parse_tree = Tree('ROOT', [])
    i = 0
    for sub_tree in parent_tree.subtrees():
        if sub_tree.label() == "NP":
            i, modified_parse_tree = handle_noun_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree)
        if sub_tree.label() == "VP" or sub_tree.label() == "PRP":
            i, modified_parse_tree = handle_verb_prop_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree)

    # recursively check for omitted clauses to be inserted in tree
    for sub_tree in parent_tree.subtrees():
        for child_sub_tree in sub_tree.subtrees():
            if len(child_sub_tree.leaves()) == 1:  #check if subtree leads to some word
                if tree_traversal_flag[child_sub_tree.treeposition()] == 0 and tree_traversal_flag[child_sub_tree.parent().treeposition()] == 0:
                    tree_traversal_flag[child_sub_tree.treeposition()] = 1
                    modified_parse_tree.insert(i, child_sub_tree)
                    i = i + 1

    return modified_parse_tree


def convert_eng_to_isl(input_string):

    if len(list(input_string.split(' '))) == 1:
        return list(input_string.split(' '))

    # Initializing stanford parser
    parser = StanfordParser()

    # Generates all possible parse trees sort by probability for the sentence
    possible_parse_tree_list = [tree for tree in parser.parse(input_string.split())]

    # Get most probable parse tree
    parse_tree = possible_parse_tree_list[0]
    print(parse_tree)
    # Convert into tree data structure
    parent_tree = ParentedTree.convert(parse_tree)

    modified_parse_tree = modify_tree_structure(parent_tree)

    parsed_sent = modified_parse_tree.leaves()
    return parsed_sent


def pre_process(sentence):
    words = list(sentence.split())
    f = open('words.txt', 'r')
    eligible_words = f.read()
    f.close()
    final_string = ""

    for word in words:
        if word not in eligible_words:
            for letter in word:
                final_string += " " + letter
        else:
            final_string += " " + word

    return final_string