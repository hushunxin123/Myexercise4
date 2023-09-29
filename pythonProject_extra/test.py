import nltk
from nltk.corpus import gutenberg
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from gensim import corpora, models
import pyLDAvis.gensim_models as gensimvis
import pyLDAvis

# Load the Alice's Adventures in Wonderland text
alice = gutenberg.sents('carroll-alice.txt')

# Tokenize and lemmatize the text
lemmatizer = WordNetLemmatizer()
texts = [[lemmatizer.lemmatize(word.lower()) for word in word_tokenize(' '.join(sent)) if word.isalpha()] for sent in alice]
# Create a dictionary and corpus
dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]

# Train the LDA model
lda_model = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary, num_topics=10, passes=10)

# Visualize the topics
vis_data = gensimvis.prepare(lda_model, corpus, dictionary)
pyLDAvis.save_html( vis_data, 'test.html')