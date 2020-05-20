import spacy
import json
import pickle
import plac
from spacy.gold import biluo_tags_from_offsets, spans_from_biluo_tags, docs_to_json

def handle_title(title_doc, ents_data, data_list):
    ents = []
    title = title_doc.text
    start_ind = 0
    for ent in ents_data:
        ent_text = ent.get('text')
        ind = title.find(ent.get('text'), start_ind)
        end = ind + len(ent_text)
        # entity is in the sentence
        if ind != -1:
            ents.append((ind, end, ent.get('type')))
            start_ind = end
        # entity is not in the sentence
        # take all found entities out and return
        else:
            tags = biluo_tags_from_offsets(title_doc, ents)
            entities = spans_from_biluo_tags(title_doc, tags)
            title_doc.ents = entities
            # add to training data
            data_list.append(title_doc)
            return ents_data[ents_data.index(ent):]


def handle_abstract(abstract, ents_data, data_list):
    if ents_data == None:
        return None
    for s in abstract.sents:
        ents = []
        sent = s.text
        start_ind = 0
        for ent in ents_data:
            ent_text = ent.get('text')
            ind = sent.find(ent.get('text'), start_ind)
            end = ind + len(ent_text)
            # entity is in the sentence
            if ind != -1:
                ents.append((ind, end, ent.get('type')))
                start_ind = end
            # entity is not in the sentence
            # take all found entities out and search next sentence
            else:
                ents_data = ents_data[ents_data.index(ent):]
                break
        tags = biluo_tags_from_offsets(abstract, ents)
        entities = spans_from_biluo_tags(abstract, tags)
        abstract.ents = entities
        # add to training data
        data_list.append(abstract)
    return ents_data


def handle_body(body, ents_data, data_list):
    if ents_data == None:
        return None
    for s in body.sents:
        ents = []
        sent = s.text
        start_ind = 0
        for ent in ents_data:
            ent_text = ent.get('text')
            ind = sent.find(ent.get('text'), start_ind)
            end = ind + len(ent_text)
            # entity is in the sentence
            if ind != -1:
                ents.append((ind, end, ent.get('type')))
                start_ind = end
            # entity is not in the sentence
            # take all found entities out and search next sentence
            else:
                ents_data = ents_data[ents_data.index(ent):]
                break
        tags = biluo_tags_from_offsets(body, ents)
        entities = spans_from_biluo_tags(body, tags)
        body.ents = entities
        # add to training data
        data_list.append(body)

    
@plac.annotations(
    type=("Type of data to create", "positional", None, str, ["training", "evaluation"]),
    start=("ID of the first document to use as training/evaluation data. Defaults to 0 (first doc in corpus)", "option", "s", int),
    end=("ID of the last document to use as training/evaluation data. Defaults to 29499 (last doc in corpus)", "option", "e", int),
)
def main(type, start=0, end=29499):
    nlp = spacy.load("en_core_web_sm", disable=["ner"])
    data_list = []
    i = 0
    with open('CORD-NER/CORD-NER-full.json', 'r') as data_file:
        for data_line in data_file:
            if i < start:
                i += 1
                continue
            if i > end:
                break
            print("Doc %d" % i)
            char_count = 0
            data = json.loads(data_line)
           
            title = data.get('title')
            ents_data = data.get('entities') # list of {'text', 'start', 'end', 'type'} for entities
            abstract = data.get('abstract')
            body = data.get('body')
            abs_doc = nlp(abstract)
            body_doc = nlp(body)
            title_doc = nlp(title)
            ents_data = handle_title(title_doc, ents_data, data_list)
            ents_data = handle_abstract(abs_doc, ents_data, data_list)
            handle_body(body_doc, ents_data, data_list)
            i += 1
    file_name = 'data/' + type + '-data' + '-' + str(start) + '-' + str(end) + '.json'
    # convert list of docs into json format used by spacy train command
    json_data = docs_to_json(data_list)
    with open(file_name, 'w') as json_file:
        json.dump([json_data], json_file)
    

if __name__ == "__main__":
    plac.call(main)
