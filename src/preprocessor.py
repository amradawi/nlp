import logging
import ConfigParser
import sys, os
import htmllib
import re

import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

SRCDIR = "/Users/amradawi/csc401"
OUTPUT_DIR = "/tmp"
if 'NLTK_DIR' not in os.environ:
    print "Environment variable NLTK_DIR must be set"
    sys.exit(1)

nltk.data.path.append(os.environ['NLTK_DIR'])


class PreProcessor:
    def __init__(self, input_filename, output_filename):
        self.input_filename = input_filename
        self.output_filename = os.path.join(OUTPUT_DIR, output_filename)
        self.configs = ConfigParser.ConfigParser()
        self.configs.read(os.path.join(SRCDIR, "conf/log_settings.cnf"))
        logging.basicConfig(format="%(asctime)-15s %(clientip)s %(user)-8s %(message)s", filename=self.configs.get("LOGGING", "logFile"))
        self.logger = logging.getLogger('preprocessor')
        self.logger.setLevel(self.configs.get("LOGGING", "logLevel"))

    def remove_html_tags(self, text):
        raise NotImplementedError()

    @staticmethod
    def convert_to_ascii(text):
        p = htmllib.HTMLParser(None)
        p.save_bgn()
        p.feed(text)
        return p.save_end()

    @staticmethod
    def remove_urls(text):
        return re.sub(r"(\s?(http|www|ftp|sftp)[^\s\\]+\s)", "", text + "\n")

    @staticmethod
    def split_sentences(text):
        return sent_tokenize(text)

    @staticmethod
    def reconstruct_ellipsis(sent_list):
        prev_sent = ''
        new_list_of_sentences = []
        for sent in sent_list:
            if len(prev_sent) > 0 and sent[0] == prev_sent[-1]:
                new_list_of_sentences.append(prev_sent + sent)
            else:
                new_list_of_sentences.append(sent)
            prev_sent = sent
        return new_list_of_sentences

    @staticmethod
    def separate_tokens(text):
        raise word_tokenize(text)

    @staticmethod
    def pos_tagging(text):
        raise nltk.pos_tag(text)

    def demarc_text(self, text_list):
        raise NotImplementedError()

    def output_to_csv(self, line_lists):
        with open(self.output_filename, 'wb+') as f:
            f.write(line_lists)

    def read_from_file(self):
        with open(self.input_filename, 'r') as f:
            yield f.readline()

    def pre_process_and_tag_text(self, text):
        text = self.remove_html_tags(text)
        self.logger.debug("removed_html_tags from text %s" % text)

        text = self.convert_to_ascii(text)
        self.logger.debug("converted text to ASCII %s" % text)

        text = self.remove_urls(text)
        self.logger.debug("removed URLs from text %s" % text)

        text_list = self.split_sentences(text)

        text_list = self.reconstruct_ellipsis(text_list)

        new_text_list = []
        for sentence in text_list:
            new_text_list += self.separate_tokens(sentence)

        text_list = []
        for sentence in new_text_list:
            text_list += self.pos_tagging(sentence)

        lines_list = self.demarc_text(text_list)
        self.output_to_csv(lines_list)




if __name__ == "__main__":
    preporcessor = PreProcessor("a", "b")
    print PreProcessor.split_sentences("Edit the Expression & Text to see matches. Roll over matches or the expression for details. Undo mistakes with cmd-z. Save Favorites & Share expressions with friends or the Community. Explore your results with  http://regexr.com/foo.html?q=bar Tools. A full Reference & Help is available in the Library, or watch the video Tutorial. https://mediatemple.net")
    print PreProcessor.remove_urls("Edit the Expression & Text to see matches. Roll over matches or the expression for details. Undo mistakes with cmd-z. Save Favorites & Share expressions with friends or the Community. Explore your results with  http://regexr.com/foo.html?q=bar Tools. A full Reference & Help is available in the Library, or watch the video Tutorial. https://mediatemple.net")