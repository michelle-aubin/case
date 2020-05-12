import spacy
import json

def handle_title(title, ents_data, ents, data_list, char_count):
    length = len(title)
    for ent in ents_data:
        if ent.get('start') < length:
            ents.append((ent.get('start'), ent.get('end'), ent.get('type')))
        else:
            print("entity is ", ent)
            ents_data = ents_data[ents_data.index(ent):]
            break
    data_list.append((title, {'entities': ents}))
    char_count += length

def handle_abstract(abstract, ents_data, ents, data_list, char_count):
    for sent in abstract.sents:
        print(sent)

def handle_body(body, ents_data, ents, data_list, char_count):
    for sent in body.sents:
        length = len(sent)
        

def main():
    nlp = spacy.load("en_core_sci_sm")
    data_list = []
    with open('../CORD-NER/CORD-NER-full.json', 'r') as data_file:
        for data_line in data_file:
            char_count = 0
            data = json.loads(data_line)
           
            title = data.get('title')
            ents_data = data.get('entities') # list of {'text', 'start', 'end', 'type'} for entities
            ents = []
            abstract = data.get('abstract')
            body = data.get('body')
            abs_doc = nlp(abstract)
            body_doc = nlp(body)
            handle_title(title, ents_data, ents, data_list, char_count)
            handle_abstract(abs_doc, ents_data, ents, data_list, char_count)
            handle_body(body_doc, ents_data, ents, data_list, char_count)


            print(data_list)
            break

main()

"""
    char count = 0
    for each sentence:
        len = num of chars in sentence
        if its the first sentence:
            store sentence and entities with offsets in data list
            char count += len
        else:    
            find entities that have a start offset between 
            char count and char count + len (its in the sentence)
            new offset for each entity is offset - char count
            store sentence and entities with new offsets in data list

        

"""