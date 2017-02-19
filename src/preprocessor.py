import logging
import ConfigParser
import sys, os
import htmllib
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from utils.html_utils import HTMLTagsStripper
import argparse

OUTPUT_DIR = "/tmp"
if 'NLTK_DIR' not in os.environ:
    print "Environment variable NLTK_DIR must be set"
    sys.exit(1)

if "SRCDIR" not in os.environ:
    print "Environment variable SRCDIR must be set"
    sys.exit(1)


SRCDIR = os.getenv("SRCDIR")
nltk.data.path.append(os.environ['NLTK_DIR'])


class PreProcessor:
    def __init__(self, input_filename, output_filename, logger, num_to_process):
        self.input_filename = input_filename
        self.output_filename = os.path.join(OUTPUT_DIR, output_filename)
        self.logger = logger
        self.num_to_process = num_to_process

    @staticmethod
    def remove_html_tags(text):
        """
        Returns a text without any of the HTML tags from tet
        :param text:
        :return: cleaned text
        """
        return HTMLTagsStripper.strip_tags_(text)

    @staticmethod
    def convert_to_ascii(text):
        """
        Returns a text converted to ASCII
        :param text:
        :return:
        """
        p = htmllib.HTMLParser(None)
        p.save_bgn()
        p.feed(text)
        return p.save_end()

    @staticmethod
    def remove_urls(text):
        """
        Returns the url filtered out text
        :param text:
        :return:
        """
        return re.sub(r"(\s?(http|www|ftp|sftp)[^\s\\]+\s)", "", text + "\n")

    @staticmethod
    def split_sentences(text):
        """
        Returns a list of Strings each is a sentence within the text
        :param text:
        :return:
        """
        try:
            return sent_tokenize(text)
        except UnicodeDecodeError:
            return sent_tokenize(text.decode("utf-8"))

    @staticmethod
    def remove_hashtag_user_symbols(text):
        text = text.strip()
        if len(text) > 0 and text[0] in ["@", "#"]:
            return text[1:]
        return text

    @staticmethod
    def reconstruct_ellipsis(sent_list):
        """
        Returns the reconstructed list of sentences without spliting the ellipsis
        :param sent_list:
        :return:
        """
        prev_sent = ''
        new_list_of_sentences = []
        for sent in sent_list:
            if len(prev_sent) > 0 and sent[0] == prev_sent[-1]:
                new_list_of_sentences.remove(prev_sent)
                ellipsis, index = PreProcessor.find_longest_sequence_from_beginning(sent)
                prev_sent += ellipsis
                new_list_of_sentences.append(prev_sent)
                sent = sent[index+1:]
                new_list_of_sentences.append(sent)
            else:
                new_list_of_sentences.append(sent)
            prev_sent = sent
        return new_list_of_sentences

    @staticmethod
    def find_longest_sequence_from_beginning(text):
        longest_sequence = ""
        index = 0
        if len(text) > 0:
            c = text[0]
            if not re.match(r"[a-z0-9A-Z]", c):
                longest_sequence += c
                for c1 in text[1:]:
                    if c1 == c:
                        longest_sequence += c1
                        index += 1
                    else:
                        break
        return longest_sequence, index

    @staticmethod
    def separate_tokens(text):
        return word_tokenize(text)

    @staticmethod
    def pos_tagging(text):
        return nltk.pos_tag(text)

    @staticmethod
    def reconstruct_line(text_list):
        line = ""
        for text in text_list:
            line += text[0] + "/" +text[1] + " "
        return line

    def demarc_text(self, text_list, mark):
        return [("<A={}>".format(mark), )] + text_list


    def output_file_(self, line_lists):
        with open(self.output_filename, 'wb+') as f:
            for line in line_lists:
                if type(line) == list:
                    line = self.reconstruct_line(line)
                else:
                    line = line[0]
                try:
                    f.write(line + "\n")
                except UnicodeEncodeError:
                    f.write(line.encode("utf-8") + "\n")

    def read_from_file(self):
        with open(self.input_filename, 'r') as f:
            num_read = 0
            for line in f.readlines():
                if num_read < self.num_to_process:
                    num_read += 1
                    yield self.parse_csv_line(line)
                else:
                    break;

    @staticmethod
    def parse_csv_line(text):
        return text.split(",", 5)

    def pre_process_and_tag_text(self, text , mark):
        text = self.remove_html_tags(text)
        self.logger.debug("removed_html_tags from text ...... {}".format(text))

        text = self.convert_to_ascii(text)
        self.logger.debug("converted text to ASCII ..... {}".format(text))

        text = self.remove_urls(text)
        self.logger.debug("removed URLs from text ...... {}".format(text))

        text_list = self.split_sentences(text)

        text_list = self.reconstruct_ellipsis(text_list)

        new_text_list = []
        for sentence in text_list:
            new_text_list += [self.separate_tokens(sentence)]

        text_list = []
        for sent_lists in new_text_list:
            text_list += [self.pos_tagging(sent_lists)]
        lines_list = self.demarc_text(text_list, mark)
        self.output_file_(lines_list)

    def pre_process_file(self):
        for line in self.read_from_file():
            pre_porcessor.pre_process_and_tag_text(pre_porcessor.remove_surrounding_quotes_and_spaces(line[5]),
                                                   int(pre_porcessor.remove_surrounding_quotes_and_spaces(line[0])))


    @staticmethod
    def remove_surrounding_quotes_and_spaces(text):
        return (text[1:-1]).strip()


if __name__ == "__main__":
    configs = ConfigParser.ConfigParser()
    configs.read(os.path.join(SRCDIR, "conf/log_settings.cnf"))
    logging.basicConfig(format="%(asctime)-15s  %(message)s",
                        filename=configs.get("LOGGING", "logFile"))
    logger = logging.getLogger('preprocessor')
    logger.setLevel(configs.get("LOGGING", "logLevel"))

    argparser = argparse.ArgumentParser(description="PreProcessor for Tweets in CSV file")
    argparser.add_argument("input_file", type=str)
    argparser.add_argument("output_file", type=str)
    args = argparser.parse_args()

    pre_porcessor = PreProcessor(args.input_file, args.output_file, logger, 20000)
    pre_porcessor.pre_process_file()
