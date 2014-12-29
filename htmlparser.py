# coding:utf-8
'''
Created on Dec 29, 2014

@author: faner
'''
from HTMLParser import HTMLParser

from collections import deque
from cStringIO import StringIO 

class Element(object):
    def __init__(self, tag, attrs=None, parent=None):
        self._tag = tag
        self._attrs = attrs
        self._parent = parent
        self._deep = 1 if not self._parent else self._parent.deep + 1
        self._end_tag = ''
        self._text = ''
        self._children = []
        if self._parent:
            self._parent.children.append(self)
        self._children_htmls_loaded = False
        self._children_htmls = ''
    
    @property
    def children(self):
        return self._children
    @property
    def tag(self):
        return self._tag
    @property
    def attrs(self):
        return self._attrs
    @property
    def parent(self):
        return self._parent
    @property
    def deep(self):
        return self._deep
    
    @property
    def text(self):
        return self._text
    
    def close(self, end_tag, data):
        match = self._tag == end_tag
        if match :
            self._end_tag = end_tag
            self._text = data
        return match
    @property
    def end_tag(self):
        return self._end_tag
    
    @property
    def html_tag(self):
        attrstr = ' '.join(map(lambda item:'%s="%s"' % (item), self.attrs))
        return '<' + self.tag + ' ' + attrstr + '>'
    
    @property
    def html_end_tag(self):
        return '</' + self.end_tag + '>' if self.end_tag else ''
    
    def reload(self):
        self._load_children_htmls(True)
    
    def _load_children_htmls(self, reload=False):
        if reload:
            print 'load---'
            children_htmls = ''
            if self.children:
                for c in self.children:
                    c._load_children_htmls(reload)
                    children_htmls += c.html
            self._children_htmls = children_htmls
            self._children_htmls_loaded = True
        else:
            if not self._children_htmls_loaded:
                print 'load---'
                children_htmls = ''
                if self.children:
                    for c in self.children:
                        c._load_children_htmls(reload)
                        children_htmls += c.html
                self._children_htmls = children_htmls
                self._children_htmls_loaded = True
        return self._children_htmls
    
    @property
    def innerhtml(self):
        return self._load_children_htmls()
            
    @property
    def html(self):
        return ''.join([self.html_tag, self.text, self._load_children_htmls(), self.html_end_tag])
   
    @property
    def path(self):
        parent = self.parent.path + '->' if self.parent else ''
        return parent + self.tag
    
    def __str__(self):
        return self.path
    
class XpathHtmlParser(HTMLParser):
    
    def __init__(self):
        HTMLParser.__init__(self)
        self._start_queue = deque([])
        self._result_queue = deque([])
        self._data_queue = deque([])
        
    @property
    def start_queue(self):
        return self._start_queue
    
    @property
    def result_queue(self):
        return self._result_queue
    
    @property
    def data_queue(self):
        return self._data_queue
    
    def handle_starttag(self, tag, attrs):
#         print 'encounter start tag' , tag, attrs
        last_start = self.start_queue.pop() if self.start_queue else None
        current_start = Element(tag, attrs, last_start)
        self.start_queue.append(last_start) if last_start else None
        self.start_queue.append(current_start)
        print current_start
    
    def handle_data(self, data):
#         print 'encounter data', data
        self._data_queue.append(data)
        
    def handle_endtag(self, tag):
        if not self.start_queue:
            print 'unfind start tag' % tag
            return 
        close = False
        while not close and self.start_queue:
            current_start = self.start_queue.pop()
            current_data = self.data_queue.pop() if self.data_queue else ''
            if not current_start.close(tag, current_data):
#                 _running_queue.append(current_start)
                self._result_queue.append(current_start)
            else:
                self.result_queue.append(current_start)
                close = True
    
    def get(self, xpath):
        '''
        xpath:
            div->div->div
        '''
        assert xpath
        return filter(lambda e:e.path == xpath, self.result_queue)
    
    @property
    def roots(self):
        return filter(lambda e:e.deep == 1, self.result_queue)
    
    def save(self, stream):
        if self.roots:
            cache = StringIO()
            for r in self.roots:
                cache.write(r.html)
            stream.write(cache.getvalue())
        
