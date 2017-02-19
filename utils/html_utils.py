from HTMLParser import HTMLParser


class HTMLTagsStripper(HTMLParser):

    def __init__(self):
        HTMLParser()
        HTMLParser.reset(self)
        # a list of the data within a text
        self.fed = []

    def handle_data(self, d):
        # we only care about the data inside not the tags
        self.fed.append(d)

    def strip_tags(self):
        return ''.join(self.fed)

    @staticmethod
    def strip_tags_(html):
        s = HTMLTagsStripper()
        s.feed(html)
        return s.strip_tags()


if __name__ == "__main__":
    print HTMLTagsStripper.strip_tags_("some text before <html><head><title>Test</title></head><body><h1>Parse me!</h1></body></html> some text after")
