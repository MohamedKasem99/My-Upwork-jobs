import spacy


class NER:
    def __init__(self):
        self.nlp = spacy.load('en_core_web_md')

    def extract_entities(self, text):
        entities = []
        doc = self.nlp(text)
        for ent in doc.ents:
            entities.append((ent.text, ent.label_))
        return entities
    
    def extract_entities_dict(self, text):        
        doc = self.nlp(text)
        entities_dict = {}
        for ent in doc.ents:
            key = ent.label_.lower()
            value = str(ent.text)
            value = value.replace('$', '').strip()
            if key in entities_dict:
                entities_dict[key] += str(', ' + value)
            else:
                entities_dict[key] = value
        return entities_dict
