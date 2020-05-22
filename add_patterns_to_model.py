import spacy
from spacy.pipeline import EntityRuler

# creates a model from en_core_sci_sm base with
# entity types from patterns.jsonl (new entity types in CORD-NER paper)
# and from en_core_web_sm (ORG, DATE, GPE, etc)
def main():
    nlp = spacy.load("en_core_sci_md", disable=["ner"])
    ruler = EntityRuler(nlp).from_disk("patterns_wo_disease_or_syndrome.jsonl")
    web_nlp = spacy.load("en_core_web_sm", disable=["tagger","parser"])
    nlp.add_pipe(web_nlp.get_pipe("ner"), after="parser", name="web_ner")
    nlp.add_pipe(ruler, before="web_ner")
 
    bc5cdr_nlp = spacy.load("en_ner_bc5cdr_md", disable=["tagger", "parser"])
    nlp.add_pipe(bc5cdr_nlp.get_pipe("ner"), after="web_ner", name="bc5cdr_ner")

    bionlp13cg_nlp = spacy.load("en_ner_bionlp13cg_md", disable=["tagger", "parser"])
    nlp.add_pipe(bionlp13cg_nlp.get_pipe("ner"), after="bc5cdr_ner", name="bionlp13cg_ner")
    labels = ["CANCER", "ORGAN", "TISSUE", "ORGANISM", "CELL", "AMINO_ACID", "GENE_OR_GENE_PRODUCT", "SIMPLE_CHEMICAL", "ANATOMICAL_SYSTEM", "IMMATERIAL_ANATOMICAL_ENTITY", "MULTI-TISSUE_STRUCTURE", "DEVELOPING_ANATOMICAL_STRUCTURE", "ORGANISM_SUBDIVISION", "CELLULAR_COMPONENT"]

    for label in labels:
        nlp.vocab.strings.add(label)


    # save model to disk
    nlp.to_disk("custom_model3/")
main()