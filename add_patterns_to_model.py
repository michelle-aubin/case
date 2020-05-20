import spacy
from spacy.pipeline import EntityRuler

# creates a model from en_core_sci_sm base with
# entity types from patterns.jsonl (new entity types in CORD-NER paper)
# and from en_core_web_sm (ORG, DATE, GPE, etc)
def main():
    nlp = spacy.load("en_core_sci_sm")
    web_nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser"])
    ruler = EntityRuler(nlp).from_disk("patterns.jsonl")
    nlp.add_pipe(web_nlp.get_pipe("ner"), before="ner", name="web_ner")
    nlp.add_pipe(ruler, before="web_ner")

    # could add but doesn't perform very well on the few tests i did 
    #bc5cdr_nlp = spacy.load("en_ner_bc5cdr_md", disable=["tagger", "parser"])
    #nlp.add_pipe(bc5cdr_nlp.get_pipe("ner"), before="ner", name="bc5cdr_ner")

    # save model to disk
    nlp.to_disk("custom_model/")
main()