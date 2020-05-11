import json 
import pickle
import sys

# pass desired training set size (as num of documents) 
# as command line argument
# pass 'full' to use the full dataset
def main():
    data_list = []
    fi = open('../CORD-NER/CORD-NER-full.json', 'r')
    i = 0
    max = sys.argv[1]
    str = 'training-data' + '-' + max
    if max != 'full':
        max = int(max)
    for line in fi:
       data = json.loads(line)
       body = data.get('body')
       ents = []
       for ent in data.get('entities'):
           ents.append((ent.get('start'), ent.get('end'), ent.get('type')))
       data_list.append((body, {'entities': ents}))
       i += 1
       if i >= max:
           break


    fo = open(str, 'wb')
    pickle.dump(data_list, fo)
 
    fo.close()
    fi.close()
main()