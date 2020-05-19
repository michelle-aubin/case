import spacy
from spacy.pipeline import EntityRuler

# creates a model from en_core_sci_sm base with
# entity types from patterns.jsonl (new entity types in CORD-NER paper)
# and from en_core_web_sm (ORG, DATE, GPE, etc)
def main():
    nlp = spacy.load("en_core_sci_sm")
    web_nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser"])
    ruler = EntityRuler(nlp).from_disk("patterns.jsonl")
    nlp.add_pipe(ruler, before="ner")
    nlp.add_pipe(web_nlp.get_pipe("ner"), before="ner", name="web_ner")
    text = """
    A novel infectious disease, caused by severe acute respiratory syndrome coronavirus 2 (SARS-CoV-2), was detected in Wuhan, China, in December 2019. The disease (COVID-19) spread rapidly, reaching epidemic proportions in China, and has been found in 27 other countries. As of February 27, 2020, over 82,000 cases of COVID-19 were reported, with > 2800 deaths.
    """
    doc = nlp(text)

    for ent in doc.ents:
        print("%s: %s" % (ent.text, ent.label_))


    #nlp.to_disk("/custom_model")
main()