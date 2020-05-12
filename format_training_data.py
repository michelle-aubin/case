import spacy
import json

def handle_title(title, ents_data, data_list, char_count):
    ents = []
    length = len(title)
    print("Title is: %s" % title)
    print("Length of title is: %d" % length)
    for ent in ents_data:
        if ent.get('start') < length:
            ents.append((ent.get('start'), ent.get('end'), ent.get('type')))
            print("Added %s with start %d and end %d" % (ent.get('text'), ent.get('start') - char_count, ent.get('end') - char_count))
        else:
        #    print("entity is ", ent)
            ents_data = ents_data[ents_data.index(ent):]
            break
    data_list.append((title, {'entities': ents}))
    return char_count + length + 2, ents_data

def handle_abstract(abstract, ents_data, data_list, char_count):
    for sent in abstract.sents:
        print(sent)

def handle_body(body, ents_data, data_list, char_count):
    for s in body.sents:
        ents = []
        sent = s.text
        length = len(sent)
    #    print("Sentence is: %s" % sent)
       # print("Sentence is %d chars long" % length)
       # print("Num of chars before sentence is: %d" % char_count)
        start_ind = 0
        for ent in ents_data:
            ent_text = ent.get('text')
       #     print("Looking for %s starting at %d" % (ent_text, start_ind))
            ind = sent.find(ent.get('text'), start_ind)
            end = ind + len(ent_text)
            # entity is in the sentence
            if ind != -1:
                ents.append((ind, end, ent.get('type')))
                start_ind = end
     #           print("Added %s with start %d and end %d" % (ent_text, ind, end))
            else:
                #print("entity is ", ent)
                ents_data = ents_data[ents_data.index(ent):]
                break
        #char_count += length + 1
        data_list.append((sent, {'entities': ents}))
    for data in data_list:
        print(data)
    

def main():
    nlp = spacy.load("en_core_sci_sm")
    data_list = []
    with open('../CORD-NER/CORD-NER-full.json', 'r') as data_file:
        for data_line in data_file:
            char_count = 0
            data = json.loads(data_line)
           
            title = data.get('title')
            ents_data = data.get('entities') # list of {'text', 'start', 'end', 'type'} for entities
            abstract = data.get('abstract')
            body = data.get('body')
            abs_doc = nlp(abstract)
            body_doc = nlp(body)
            char_count, ents_data = handle_title(title, ents_data, data_list, char_count)
            handle_abstract(abs_doc, ents_data, data_list, char_count)
            handle_body(body_doc, ents_data, data_list, char_count)


            # for data in data_list:
            #     print(data)
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