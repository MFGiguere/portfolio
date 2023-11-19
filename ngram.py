import re, random
from nltk.lm.preprocessing import pad_both_ends
from nltk import ConditionalFreqDist
from nltk.probability import ConditionalProbDist, ELEProbDist
from nltk.util import pad_sequence
from nltk.lm.preprocessing import pad_both_ends
from functools import reduce

class Ngram():
    def __init__(self, corpus, n):
        self.n = n
        tokenized_corpus = self._tokenize(corpus)
        self._ngrams = self._build_ngrams(tokenized_corpus, n)
        self._cpd = self._build_distribution(self._ngrams, n)        

    def _tokenize(self, corpus):
        # The list of regular expressions and replacements to be applied
        # the order here matters! these replacements will happen in order
        replacements = [
             ["[\n]",                   " "]  # Hyphens to whitespace
            ,[r'[][(){}#$%"]',            ""]
            ,[r'\s([./-]?\d+)+[./-]?\s', " [NUMBER] "] # Standardize numbers
            ,[r'\.{3,}',                 " [ELLIPSIS] "] # remove ellipsis
            ,[r'(\w)([.,?!;:])',         r'\1 \2' ]  # separate punctuation from previous word
        ]
        
        # This is a function that applies a single replacement from the list
        resub = lambda words, repls: re.sub(repls[0], repls[1], words)
        
        # we use the resub function to applea each replacement to the entire corpus,
        normalized_corpus = reduce(resub, replacements, corpus)
        normalized_corpus = normalized_corpus.replace("\x02", "")
        
        sentences = normalized_corpus.split('.')
        
        tokens = []

        for sentence in sentences:
            words = sentence.split() # split on whitespace
            words = [word.lower() for word in words]
            words = list(pad_both_ends(words, n=self.n))
            tokens += words

        return tokens
            
    def _build_ngrams(self, tokenized_corpus, n):
        n_grams = []
        for i in range(n-1, len(tokenized_corpus)): 
            n_grams.append(tuple(tokenized_corpus[i-(n-1):i+1]))    
        return n_grams
    
    def _build_distribution(self, corpus, n):
               
        cfd = ConditionalFreqDist()
        for ngram in self._ngrams:
            condition = tuple(ngram[0:n-1]) 
            outcome = ngram[n-1]
            
            cfd[condition][outcome] += 1
        bins = len(cfd) # we have to pass the number of bins in our freq dist in as a parameter to probability distribution, so we have a bin for every word
        cpd = ConditionalProbDist(cfd, ELEProbDist, bins)
        self.cpd = cpd
        return cpd
    
    def _add_stops(self, string):
        """
        function to convert the stop/start sequence back into periods.
        strips all the sequences of any number of stop tokens followed by the some number of start tokens
        and replaces them with a period.

        then strips any remaining stop and start sequences (which will occur at the beginning and end of our entire generated sequence)
        """
        string = re.sub(r"</s>(?:\s</s>)*\s<s>(?:\s<s>)*", ".", string)

        string = re.sub(r"(<s>\s)+", "", string) # initial tokens
        string = re.sub(r"(</s>)", "", string) # final token

        return string
        
    def generate(self, num_sentences = 1, seed = []):
        """
        There are two cases to deal with here. Either we have a start string, or we don't. 
        If we are given a start string, we'll have to find the last n-1 gram and condition on that
        If we are not, we need to generate the first n-1 gram. For a trigram model, we need a bigram. But how can we use our model to generate new words when we have fewer than two words to condition on?
        We can use a bigram model! But wait. If we have a bigram model, how do we generate the first token without another token to condition on? 
        We can use a unigram model! 
        Recursion will save us here. Turns out the easiest way to do this will be to recursively construct an n-1gram model and store it in the main model.
        And how can we 
        Either way, we need a seed condition to enter into the loop with.
        """

        # place to put generated tokens
        string = []

        if seed:
            string = string + (list(pad_sequence(seed, self.n, pad_left=True, pad_right=False, left_pad_symbol='<s>') ) )
        else:
            string = string + (list(pad_sequence('', self.n, pad_left=True, pad_right=False, left_pad_symbol='<s>') ) )
        
        for i in range(num_sentences):
            next_token = tuple(string[-(self.n-1):])
            
            # keep generating tokens as long as we havent reached the stop sequence
            while next_token != '</s>':
                
                # get the last n-1 tokens to condition on next
                lessgram = tuple(string[-(self.n-1):])

                next_token = self.cpd[lessgram].generate()
                string.append( next_token )

        string = ' '.join(string)
        string = self._add_stops(string)
        text = re.sub(" ([,.!?:;0]) ", r"\1 ", string)
        text = re.sub("[0-9«»<>]", "", text)
        text = re.sub("\s+", " ", text) #remove doubled space
        text = re.sub("(^|[.?!])\s*([a-zA-Z])", lambda p: p.group(0).upper(), text)
        text = re.sub("\[number\]", f"{random.randint(1, 100)}", text)
        text = re.sub("\[ellipsis\]", "", text)
        text = text[:-1]+"."
        return text