#!/usr/bin/python
# Copyright 2012 James Vasile <james@jamesvasile.com>
# Distributed under the terms of the GNU General Public License v3 or
# later.

import string, re, os, sys, textwrap

try:
    package = sys.argv[1]
except IndexError:
    package = os.path.split(os.getcwd())[1]

class Commit():
    package = ''
    author = ''
    date = ''
    raw = []
    version = "0.1.1"

    def __init__(self, raw_line):
        self.raw = [raw_line]
        self.package = package

    def append(self, raw_line):
        self.raw.append(raw_line)

    def parse_commit_id(self):
        self.commit_id = self.raw[0].strip().split(" ")[1]

    def get_version(self):
        INF = os.popen('git show %s:VERSION' % self.commit_id, 'r')
        v = INF.read().strip()
        if v:
            self.version = v
        
    def parse_author(self):
        for line in self.raw:
            # Match the author line and extract the part we want
            if re.match('Author:', line) >=0:
                self.authorList = re.split(': ', line, 1)
                self.author = self.authorList[1].strip()
                return self.author

    def parse_date(self):
        for line in self.raw:
            # Match the date line
            if re.match('Date:', line) >= 0:
                self.dateList = re.split(': ', line, 1)
                self.date = self.dateList[1].strip()
                return self.date

    def parse_commit(self):
        date = False
        files = []
        commit = ''
        for line in self.raw:
            if line.startswith("Date:"):
                date = True
            elif date:
                if line.startswith("  "):
                    commit += line.lstrip()
                elif line.startswith(" ") and '|' in line:
                    files.append(line.split('|')[0].strip())

        commit = "%s: %s\n" % (', '.join(files), commit)
        wrapper = textwrap.TextWrapper(initial_indent=" * ", subsequent_indent="   ", break_on_hyphens=False, break_long_words=False)
        self.commit = wrapper.fill(commit).rstrip()
            
    def parse(self):
        self.parse_commit_id()
        self.get_version()
        self.parse_author()
        self.parse_date()
        self.parse_commit()
        self.package_line = "%s (%s) unstable; urgency=low\n\n" % (self.package, self.version)
        self.author_line = " -- " + self.author + "  " + self.date + "\n"

    def render(self, last=None):
        ret = ''

        if last:
            if last.author_line != self.author_line:
                ret += last.author_line + "\n"
                ret += self.package_line
        else:
            ret += self.package_line
        ret += self.commit + "\n"
        return ret

class Commits(list):
    """List of commits"""
    def __init__(self):
        INF = os.popen('git log --summary --no-merges --stat --date=short', 'r')
        for line in INF:
            if line.startswith("commit "):
                self.append(Commit(line))
            else:
                self.__getitem__(-1).append(line)
        for c in self:
            c.parse()
    def render(self):
        last = None
        for c in self:
            print c.render(last=last)
            last = c
        print self.__getitem__(-1).author_line

c = Commits()
c.render()
