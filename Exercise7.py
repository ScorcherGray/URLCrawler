import urllib, urllib.request, pprint, re
from collections import defaultdict

class HayStack:
    def __init__(self, url, depth = 3):
        #The constructor crawls starting from the given web page, finding and 
        #following all embedded webpage links until it reaches the maximum search depth and
        #computes the following data items
        count = 0
        links = [[] for i in range(depth+1)]
        visited = []
        self.words = []
        graph = defaultdict(list)
        index = defaultdict(list)
        page = urllib.request.urlopen(url)
        visited.append(url)
        stuff = page.read().decode()
        results = re.findall('http.*(?<=html)', stuff)
        graph[url].append(results)
        lines = re.findall("[a-zA-Z\']+(?![^<>]*>)", stuff)
        for line in lines:
            temp = line.split()
            for run in temp:
                run = run.lower()
                if url not in index[run]:
                    index[run].append(url)
        links[count].extend(results)
        while count < depth:
            for link in links[count]:
                if link not in visited:
                    page = urllib.request.urlopen(link)
                    visited.append(link)
                    stuff = page.read().decode()
                    results = re.findall('http.*(?<=html)', stuff)
                    links[count+1].extend(results)
                    for result in results:
                        if result not in graph[link]:
                            graph[link].append(result)
                    lines = re.findall("[a-zA-Z\']+(?![^<>]*>)", stuff)
                    for line in lines:
                        temp = line.split()
                        for run in temp:
                            run = run.lower()
                            if link not in index[run]:
                                index[run].append(link)

            count += 1
        self.graph = graph
        self.index = index
        self.compute_ranks(graph)
        
    def lookup(self, word):
        sorts = []
        output = []
        for key, value in sorted(self.ranks.items(), key=lambda item: item[1], reverse = True):
            sorts.append(key)
        urls = self.index[word.lower()]
        for item in sorts:
            if item in urls:
                output.append(item)
        return output
   
    def compute_ranks(self,graph):
        d = 0.85 # probability that surfer will bail
        numloops = 10
        ranks = {}
        npages = len(graph)
        for page in graph:
            ranks[page] = 1.0 / npages
        for i in range(0, numloops):
            newranks = {}
            for page in graph:
                newrank = (1 - d) / npages
                for url in graph:
                    if page in graph[url]:
                        newrank += d*ranks[url]/len(graph[url])
                newranks[page] = newrank
            ranks = newranks
        self.ranks = ranks
 
if __name__ == '__main__':
    with open('index.txt', 'w') as out:
        engine = HayStack('http://freshsources.com/page1.html', 4)
        for w in ['pages','links','you','have','I']:
            out.write(w + '\n')#print(w, out)
            pprint.pprint(engine.lookup(w), stream = out)
        out.write('\n')
        out.write('index:\n')#print('index:')
        pprint.pprint(dict(engine.index), stream = out)
        out.write('\n')#print()
        out.write('graph:\n')#print('graph:')
        pprint.pprint(dict(engine.graph), stream = out)
        out.write('\n')#print()
        out.write('ranks:\n')#print('ranks:', out)
        pprint.pprint(engine.ranks, stream = out)