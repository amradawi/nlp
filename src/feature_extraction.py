import nltk
import os, sys
import argparse
import copy
import re

OUTPUT_DIR = "/tmp"
if 'NLTK_DIR' not in os.environ:
    print "Environment variable NLTK_DIR must be set"
    sys.exit(1)

if "SRCDIR" not in os.environ:
    print "Environment variable SRCDIR must be set"
    sys.exit(1)


SRCDIR = os.getenv("SRCDIR")
nltk.data.path.append(os.environ['NLTK_DIR'])

features_template = {
    "fpp": 0,  # first person pronouns
    "spp": 0,  # second person pronouns
    "tpp": 0,  # third person pronouns
    "cc": 0,  # Coordinating conjunctions
    "ptv": 0,  # past tense verbs
    "c": 0,  # commas
    "cas": 0,  # colons and semi colons
    "d": 0,  # dashes
    "p": 0,  # parentheses
    "e": 0,  # ellipses
    "cn": 0,  # common nouns
    "pn": 0,  # proper nouns
    "ad": 0,  # adverbs
    "wh": 0,  # wh-words
    "msa": 0,  # modern slang acronyms
    "upp": 0  # Words all in upper case
    }
ordered_features_list = ["fpp", "spp", "tpp", "cc", "ptv", "c", "cas", "d", "p", "e", "cn", "pn", "ad", "wh", "msa", "upp"]

fpp_words = ["me", "my", "mine", "we", "our", "ours"]
spp_words = ["you", "your", "yours", "u", "ur", "urs"]
tpp_words = ["he", "him", "his", "she", "her", "hers", "it", "its", "they", "them", "their", "theirs"]
ft_wrods = ["'ll", "will", "gonna", "going to"]
msa_words = ["smh","fwb","lmfao","lmao","lms","tbh","rofl","wtf","bff","wyd","lylc","brb","atm","imao","sml","btw",
            "bw","imho","fyi","ppl","sob","ttyl","imo","ltr","thx","kk","omg","ttys","afn","bbs","cya","ez","f2f","gtr",
            "ic","jk","k","ly","ya","nm","np","plz","ru","so","tc","tmi","ym","ur","u","sol"]
commas_words =  [","]
csc_words = [";", ":"]
dashes_words = ["-", "_"]
parentheses_words=["(", ")"]

cn_tags = ["NN", "NNS"]
pn_tags = ["NNP", "NNPS"]
adv_tags = ["RB", "RBR", "RBS"]
wh_tags = ["WDT", "WP", "WP$", "WRB"]
cc_tags = ["CC"]
pt_tags = ["VBD"]
dashes_tags = ["--"]
ellipsis_colons_tags = [":"]
open_parentheses_tag = ["("]
closed_parentheses_tag = [")"]


class FeatureExtractor:

    def __init__(self, data_file, output_file):
        self.data_file = data_file
        self.features = copy.deepcopy(features_template)
        self.output_file = output_file
        self.words_len_list = []

    def _word_fe_based(self, word, feature):
        f_dict = {"fpp": fpp_words, "spp": spp_words, "tpp": tpp_words, "ft": ft_wrods, "msa": msa_words,
                  "c": commas_words}
        if feature in f_dict and word.split("/")[0].lower() in f_dict[feature]:
            self.features[feature] += 1

    def _tag_fe_based(self, word, feature):
        f_dict = {"cn": cn_tags, "pn": pn_tags, "ad": adv_tags, "wh": wh_tags, "CC": cc_tags,
                  "d": dashes_tags}
        word_list = word.split("/")
        if len(word_list) > 1 and feature in f_dict and word_list[1] in f_dict[feature]:
            self.features[feature] += 1

    def _syntax_fe_based(self, word, feature):
        word_list = word.split("/")
        if feature == "upp":
            word = word.split("/")[0]
            if len(word) > 1 and word.isupper():
                self.features[feature] += 1
        elif len(word_list) > 1 :
            if feature == "p":
                if word_list[1] in open_parentheses_tag+closed_parentheses_tag:
                    self.features[feature] += 1
            elif feature == "e":
                if word_list[1] in ellipsis_colons_tags:
                    if word_list[0] not in csc_words:
                        self.features[feature] += 1
            elif feature == "cas":
                if word_list[1] in ellipsis_colons_tags:
                    if word.split("/")[0] in csc_words:
                        self.features[feature] += 1

    def _process_one_pos_text(self, sentence):
        if len(sentence) > 0:
            for word in sentence.split(" "):
                if re.match("[A-Za-z0-9]+/.+", word):
                    self.words_len_list.append(len(word.split("/")[0]))
                for key in self.features.keys():
                    self._syntax_fe_based(word, key)
                    self._tag_fe_based(word, key)
                    self._word_fe_based(word, key)

    @staticmethod
    def _avg_len_of_sentences(sent_len_list):
        if len(sent_len_list) > 0:
            return reduce(lambda x, y: x + y, sent_len_list) / float(len(sent_len_list))
        return 0

    def _output_to_file(self, sent_class, sentences_len_list):
        if sent_class != "":
            avg_len = self._avg_len_of_sentences(sentences_len_list)
            with open(self.output_file, 'a+') as f:
                constructed_line = ""
                for key in ordered_features_list:
                    constructed_line += str(self.features[key]) + ","
                constructed_line += (str(avg_len) + "," + str(len(sentences_len_list)) + "," +
                                     str(self._avg_len_of_sentences(self.words_len_list)) + "," + sent_class)
                f.write(constructed_line + "\n")

    def process_file(self):
        with open(self.data_file) as f:
            one_sent = ""
            sent_class = ""
            len_of_sents = []
            for line in f:
                if line.startswith("<A="):
                    sent_class = line[3]
                    self._process_one_pos_text(one_sent)
                    self._output_to_file(sent_class,  len_of_sents)
                    self.features = copy.deepcopy(features_template)
                    self.words_len_list = []
                    one_sent = ""
                    len_of_sents = []
                else:
                    one_sent += line.strip() + " "
                    len_of_sents.append(len(line.strip().split(" ")))
            # output the last one
            self._output_to_file(sent_class, len_of_sents)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="features extractor for tweets")
    parser.add_argument("input_file")
    parser.add_argument("output_file")
    args = parser.parse_args()
    f = FeatureExtractor(args.input_file, args.output_file)
    f.process_file()