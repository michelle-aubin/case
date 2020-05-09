import json 
import pickle

def main():
    data_list = []
    fi = open('CORD-NER/CORD-NER-full.json', 'r')
    i = 0
    for line in fi:
       data = json.loads(line)
       body = data.get('body')
       ents = []
       for ent in data.get('entities'):
           ents.append((ent.get('start'), ent.get('end'), ent.get('type')))
       data_list.append((body, {'entities': ents}))
   
    fo = open('summer2020-research/training_data', 'wb')
    pickle.dump(data_list, fo)
 
    fo.close()
    fi.close()
main()