class Parser:
    def __init__(
            self
    ):
        self.trasncript = ['']
        self.last_utter = []

        self.context = ['']

    
    def save(self, text, background, phrase_complete):
        '''
        append transcribed text
        '''
        if phrase_complete: 
            self.trasncript.append(text)
            self.context.append(background)
        
        else: 
            self.trasncript[-1] = text
            self.context[-1] = background

        self.last_utter = [text, background]
    

    def get_transcript(self):
        return [self.trasncript, self.context]
    

    def get_last_utterance(self):
        temp = self.last_utter
        self.last_utter = []

        return temp
    