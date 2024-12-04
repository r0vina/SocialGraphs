# Necessary imports
import json
import string

# These are for LDA itself
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamulticore import LdaMulticore as LdaModel # this is the multicore version, supposed to be faster
from sklearn.feature_extraction.text import TfidfVectorizer

# This is to clean up the text
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import nltk

# Download necessary NLTK resources if not already available
try:
    stop_words = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords')
    stop_words = set(stopwords.words('english'))

try:
    word_tokenize('test')
except LookupError:
    nltk.download('punkt')

try:
    nltk.pos_tag(['test'])
except LookupError:
    nltk.download('averaged_perceptron_tagger')

# Download wordnet as indicated in the error message
try:
    lemmatizer = WordNetLemmatizer()
    lemmatizer.lemmatize('test')
except LookupError:
    nltk.download('wordnet')

# load json data and convert to python dictionary
with open('dictionary.json') as f:
    data = json.load(f)

# create new dictionary with only keys where value is not None
def remove_empty_episodes(data):
    new_dict = {}
    for key in data:
        if data[key] is not None:
            new_dict[key] = data[key]
    return new_dict

cleaned_dict = remove_empty_episodes(data)

custom_stopwords = {"yeah", "__", "'s", "'re", "'m", "n't", "uh", "um", "like", "know", "right", "people", "think", "bro", "cuz", "ta"}
all_stopwords = stop_words.union(custom_stopwords)

# Defining processing and cleaning tools.
def preprocess(text):
    tokens = word_tokenize(text.lower())  # Tokenize and lowercase
    tokens = [t for t in tokens if t not in all_stopwords and t not in string.punctuation]
    return tokens

tfidf = TfidfVectorizer(
    min_df=2,  # Minimum document frequency, change if you think it should be higher or lower
    max_df=0.5,  # Maximum document frequency (as a proportion), change if you think it should be higher or lower
    stop_words=list(all_stopwords)
)

lemmatizer = WordNetLemmatizer()


documents = list(cleaned_dict.values())  # Corpus: concatenated texts by IDs
processed_docs = [preprocess(doc) for doc in documents]

tfidf.fit([" ".join(doc) for doc in processed_docs])
important_words = set(tfidf.get_feature_names_out())

# Filter texts to keep only important words
filtered_texts = [[word for word in doc if word in important_words] for doc in processed_docs]

# Lemmatize filtered_texts
lemmatized_texts = []
for doc in filtered_texts:
    lemmatized_doc = [lemmatizer.lemmatize(word) for word in doc]
    lemmatized_texts.append(lemmatized_doc)

# Create a dictionary and corpus
dictionary = Dictionary(lemmatized_texts)
corpus = [dictionary.doc2bow(doc) for doc in lemmatized_texts]  # Bag-of-words format

# Train LDA
lda_model = LdaModel(corpus, num_topics=20, id2word=dictionary, passes=10)

# Display topics
for idx, topic in lda_model.print_topics(-1):
    print(f"Topic {idx}: {topic}")

# Classify each document into a topic
document_topic_mapping = {}

for i, bow in enumerate(corpus):
    topic_distribution = lda_model[bow]  # Get the topic distribution for the document
    most_probable_topic = max(topic_distribution, key=lambda x: x[1])[0]  # Find the topic with the highest probability
    document_topic_mapping[list(cleaned_dict.keys())[i]] = most_probable_topic

# Print document-topic mapping
for episode_id, topic_id in document_topic_mapping.items():
    print(f"Episode ID: {episode_id} => Assigned Topic: {topic_id}")

# Optional: Save the document-topic mapping to a JSON file
with open('document_topic_mapping.json', 'w') as f:
    json.dump(document_topic_mapping, f, indent=4)

# Generate wordclouds for each topic
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Create a folder to save wordclouds
import os
os.makedirs("wordclouds", exist_ok=True)

# Generate wordclouds for each topic
for idx, topic in lda_model.show_topics(num_topics=20, formatted=False, num_words=50):
    topic_words = dict(topic)  # Convert word-probability pairs to dictionary
    
    # Generate wordcloud
    wordcloud = WordCloud(
        background_color='white',
        width=800,
        height=400
    ).generate_from_frequencies(topic_words)
    
    # Display the wordcloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title(f"Topic {idx}", fontsize=16)
    plt.show()
    
    # Save the wordcloud as an image
    wordcloud.to_file(f"wordclouds/topic_{idx}.png")
