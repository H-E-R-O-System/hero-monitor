import pickle
import whisper
from transformers import AutoTokenizer
import torch

class NLP:
    def __init__(self):
        self.transcription_model = whisper.load_model('base')

        nlp_model_file = 'consultation/modules/nlp_model.pkl'
        with open(nlp_model_file, 'rb') as file:
            self.bert_tuned = pickle.load(file)
        
        self.tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased')

        self.labels2symptom = {
            1: 'confusion, disorientation and getting lost in familiar places',
            2: 'difficulty planning or making decisions',
            3: 'problems with speech and language',
            4: 'problems moving around without assistance or performing self-care tasks',
            5: 'personality changes, such as becoming aggressive, demanding and suspicious of others',
            6: 'hallucinations (seeing or hearing things that are not there) and delusions (believing things that are untrue)',
            7: 'low mood or anxiety',
            8: 'balance problems (this may increase the chances of a fall)',
            9: 'loss of sense of smell (anosmia)',
            10: 'problems sleeping (insomnia)',
            11: 'memory problems'
        }

    def transcribe_audio(self, audio_file_path):
        transcription = self.transcription_model.transcribe(audio_file_path)
        return transcription['text']
    
    def classify_text(self, text):

        '''
        Returns a list of labels that meet the threshold.
        '''

        encoding = self.tokenizer(text, return_tensors="pt")
        encoding = {k: v.to(self.bert_tuned.device) for k,v in encoding.items()}

        outputs = self.bert_tuned(**encoding)

        logits = outputs.logits
        logits.shape

        # apply sigmoid + threshold condition of > 0.5
        sigmoid = torch.nn.Sigmoid()
        probs = sigmoid(logits.squeeze().cpu())
        for i in range(len(probs)):
            if probs[i] > 0.5:
                return(self.labels2symptom[i+1])

nlp = NLP()
print(nlp.classify_text('I am feeling sad'))
