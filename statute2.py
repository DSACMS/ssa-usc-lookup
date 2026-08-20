from bs4 import BeautifulSoup as bs
import requests
import textwrap
import os
import re
from colorama import init,Fore

class Section:

    def __init__(self,title,section):

        self.name = str(title)+" U.S.C. "+str(section)
        self.title = title
        self.section = section

        self.subsections = {}
        self.components = []

        self.url = 'https://www.law.cornell.edu/uscode/text/'+str(title)+'/'+str(section)
        
        requests.packages.urllib3.disable_warnings()
        html = requests.get(self.url,verify=False).content
        soup = bs(html,'html5lib')

        self.head = soup.find('h1').text

        main = soup.find('div',class_='section')
        if main.findNext().name == 'span' and 'chapeau' in main.findNext()['class']:
            self.components.append(main.findNext())

        divs = [main.find('div')]
        divs += main.find('div').findNextSiblings()

        for div in divs:
            if 'content' in div['class']:
                self.components.append(div)
            elif not 'sourceCredit' in div['class']:
                loc = div.find('a')['name'].replace('_','')
                self.components.append(loc)
                self.subsections[loc] = Subpart(self.name,1,div)
    
    def print_section(self):

        print(self.head+'\n')

        screen_width = os.get_terminal_size()[0]
        wrapper = textwrap.TextWrapper(initial_indent='',width=screen_width-10,subsequent_indent='')

        for i in range(len(self.components)):
            if type(self.components[i]) != type('s'):
                print(wrapper.fill(self.components[i].text))
            else:
                self.subsections[self.components[i]].print_part()
    

class Subpart:

    def __init__(self,name,depth,start_div):

        self.depth = depth
        
        self.components = []
        self.subparts = {}

        self.head = None

        a = start_div.find('a')
        if not '_' in a['name'] or a['name'][-1]=='_':
            self.loc = a['name'].replace('_','')
        else:
            pos = a['name'].rindex('_')+1
            self.loc = a['name'][pos:]
        
        self.name = name + '(' + self.loc + ')'
        #print(self.name)

        next_tag = start_div.find('span').findNext()
        if next_tag.name == 'span':
            if 'heading' in next_tag['class']:
                self.head = next_tag.text
                chapeau_test = next_tag.findNext()
                if chapeau_test.name == 'span':
                    if 'class' in chapeau_test.attrs and 'chapeau' in chapeau_test['class']:
                        self.components.append(chapeau_test)
            if 'chapeau' in next_tag['class']:
                self.components.append(next_tag)

        divs = [start_div.find('div')]
        divs += start_div.find('div').findNextSiblings()

        for div in divs:
            #print(div['class'])
            if 'content' in div['class'] or 'continuation' in div['class'] or 'level' in div['class']:
                self.components.append(div)
            else:
                a = div.find('a')
                pos = a['name'].rindex('_')+1
                loc = a['name'][pos:]
                if loc in self.components:
                    loc = loc+'+'
                self.components.append(loc)
                self.subparts[loc] = Subpart(self.name,self.depth+1,div)

    def print_part(self):

        indent = '\t'*(self.depth-1)
        screen_width = os.get_terminal_size()[0]
        wrapper = textwrap.TextWrapper(initial_indent=indent,width=screen_width-30,subsequent_indent=indent+' '*(len(self.loc)+3))
        flush_wrapper = textwrap.TextWrapper(initial_indent = indent+' '*(len(self.loc)+3),width=screen_width-30,subsequent_indent=indent+' '*(len(self.loc)+3))

        current = 0
        init = '(' + self.loc +')'
    
        if self.head:
            init += self.head.upper() + '--'
        if type(self.components[0]) != type('s'):
            init += self.components[0].text
            current += 1
        
        print(wrapper.fill(init))

        for i in range(current,len(self.components)):
            if type(self.components[i]) != type('s') and i == 0 and current == 0:
                print(wrapper.fill(self.components[i].text))
            elif type(self.components[i]) != type('s'):
                print(flush_wrapper.fill(self.components[i].text))
            else:
                self.subparts[self.components[i]].print_part()
        
def display(title,part):

    if not '(' in str(part):
        s = Section(title,part)
        s.print_section()
        return
    
    pos = part.index('(')
    section = part[:pos]
    s = Section(title,section)

    components = re.findall(r'\(.*?\)',part)
    components = [c[1:c.rindex(')')] for c in components]

    subsection = s.subsections[components[0]]

    if len(components) == 1:
        subsection.print_part()
        return
    
    target = subsection

    for c in components[1:]:
        target = target.subparts[c]
    
    target.print_part()
