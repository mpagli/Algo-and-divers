#!/usr/bin/python

import sys
import os
import random as rnd

def naive_tokenizer(inputLine, stopWords):
	"""For one line, return a list of words, remove all the stop words"""
	for sw in stopWords:
		inputLine = inputLine.replace(sw,' ')
	return filter(lambda x: x != '',[w.lower() for w in inputLine.split(' ')]) #return everything in lowercase


def read_corpus_from_folder(corpus_source,stopWords):
	"""Reads all the documents from a folder, stores them as a dictionary (documents) of 
	lists (words) , generate a lexicon, filter the stop words"""
	corpus = {}
	for root, dirnames, filenames in os.walk(corpus_source):
			for filename in filenames:
				if filename.endswith(('.txt')):
					pathToFile = os.path.join(root, filename)
					doc = []
					stream = open(pathToFile,'r')
					for line in stream: #create a dictionary with all the words in the document
						words = naive_tokenizer(line.strip('\n'), stopWords)
						for w in words:	
							doc.append(w)
					corpus[filename.replace('.txt','')] = doc
					stream.close()
	return (corpus,set([w for doc in self.corpus for w in self.corpus[doc]])) #(corpus/lexicon)

def read_corpus_with_vocab(corpus_path,vocab_path,stopWords):
	"""Read the documents stored in a single file based on a given lexicon"""
	#Read the lexicon:
	lexicon = set()
	lex_stream = open(vocab_path,'r')
	for w in lex_stream:
		lexicon.add(w.strip('\n').lower())
	lex_stream.close()
	#Read the corpus:
	corpus = {}
	corpus_stream  = open(corpus_path,'r')
	currentDocName = ""
	currentList = []
	lock = 0
	for line in corpus_stream:
		line = line.strip('\n').strip('\t')
		for sw in stopWords:
			line = line.replace(sw,' ')
		line = line.split(' ')

		if line[0] == "<DOCNO>":
			currentDocName = line[1]
		elif line[0] == "<TEXT>":
			lock = 1
		elif lock == 1:
			for w in line:
				if w.lower() in lexicon:
					currentList.append(w.lower())
			corpus[currentDocName] = currentList
			currentList = []
			lock = 0
	corpus_stream.close()
	return (corpus,lexicon)
		

class LDA_topic_extractor(object):
	"""Class to extract the topics from the corpus using Gibbs sampling"""

	def __init__(self, corpus, numTopics, alpha, beta, lexicon):
		self.corpus = corpus
		self.alpha  = float(alpha) #parameter of the Dirichlet distributions for per document topics
		self.beta   = float(beta)  #parameter of the Dirichlet distribution for per topic word
		self.numTopics = numTopics 
		self.lexicon   = lexicon
		self.numDoc    = len(corpus)
		self.n_dt = {doc: [ 0 for x in xrange(numTopics)] for doc in self.corpus} #for every document contain a list of the number of elemnt for each topic 
		self.n_t  = [0 for x in xrange(numTopics)] 		 #contain the number of words for each topics
		self.n_wt = [{key: 0 for key in self.lexicon} for x in xrange(self.numTopics)] #contain for each topics a dictionary of key/value = (word,wordCount)
		self.n_d  = {doc : 0 for doc in self.corpus}	 #contain the number of element in each doc


	def initialize(self): 
		"""Assign a random topic to each word for each document. Fills all the structures"""
		for doc in self.corpus:
			for idx,w in enumerate(self.corpus[doc]):
				currentTopic = rnd.randint(0,self.numTopics-1)
				currentWord  = w
				self.corpus[doc][idx] = (self.corpus[doc][idx],currentTopic) #instead of only the word we also append the topic
				self.n_dt[doc][currentTopic] += 1
				self.n_t[currentTopic] += 1
				self.n_wt[currentTopic][currentWord] += 1
				self.n_d[doc] += 1 


	def sampleFromTopics(self, distrib):
		r = rnd.random()
		s = 0.0
		for idx,val in enumerate(distrib):
			s += val
			if r < s:
				return idx  


	def displayTopics(self,cut=None):
		topics = []		#store the final list of words for each topic
		for idx,t in enumerate(self.n_wt):
			topics.append(filter(lambda x: x[1]!=0, [(k,t[k]) for k in t]))

		#sort the lists:
		for idx,t in enumerate(topics):
			topics[idx] = sorted(t,key=lambda x: x[1], reverse=True)

		print "###",self.numTopics,"topics extracted:\n"
		for idx,t in enumerate(topics):
			print "Topic #"+str(idx+1)+": ",
			count = 0
			for w in t:
				count += 1
				if cut and count > cut:
					break 
				print w[0]+":"+str(w[1]),
			print "\n\n"


	def readOutPhi(self):
		"""Extract p(w|z) from the sampling, store the result in n_wt"""
		for t in xrange(self.numTopics):
			D = self.n_t[t] + self.beta * len(self.lexicon)
			for w in self.n_wt[t]:
				self.n_wt[t][w] = (self.n_wt[t][w] + self.beta)/D


	def extract_topics(self,numIter):
		"""Improve the choice of topics using gibbs sampling"""
		maxCount = numIter
		count = 0

		while(count<maxCount):
			count +=1
			print "\t\tLDA :: iteration "+str(count)
			for doc in self.corpus:
				for idx,word_topic in enumerate(self.corpus[doc]):

					w,t = word_topic

					#remove the influence of the current word
					self.n_dt[doc][t] -= 1
					self.n_wt[t][w]   -= 1
					self.n_t[t]       -= 1
					self.n_d[doc]	  -= 1

					#multinomial sampling: reassign w a new topic choosen with probability p(t|t^(-1),w) 
					dist = []

					for k in xrange(self.numTopics): 
						p_w_t  = (self.n_wt[k][w] + self.beta) / (self.n_t[k] + self.beta * len(self.lexicon));
						p_t_d  = (self.n_dt[doc][k] + self.alpha) / (self.n_d[doc] + self.alpha * self.numTopics);
						dist.append(p_w_t*p_t_d)

					s = sum(dist)
					dist = map(lambda x : x/s, dist) #normalization

					newTopic = self.sampleFromTopics(dist)

					self.corpus[doc][idx]     = (w,newTopic) #the choosen topic is attributed to the word
					self.n_dt[doc][newTopic] += 1
					self.n_wt[newTopic][w]   += 1
					self.n_t[newTopic]       += 1
					self.n_d[doc]	  		 += 1

		self.readOutPhi()	#extract the word distribution for each topic



if __name__ == "__main__" : 

	if len(sys.argv) < 6 :
		print "usage: ./LDA_learn_topics <corpus_file> <lexicon_file> <topicNumber> <alpha> <beta>"
		sys.exit(2)

	corpus_source = sys.argv[1]
	lexicon_file  = sys.argv[2]  
	topicNum = int(sys.argv[3])
	alpha = float(sys.argv[4])
	beta  = float(sys.argv[5])

	stopWords = ['\t','\n','.',':',';',',','\'','\"']

	print "Reading corpus "+corpus_source+" ...",
	corpus, lexicon = read_corpus_with_vocab(corpus_source, lexicon_file, stopWords)
	print " done."

	myLDA = LDA_topic_extractor(corpus,topicNum,alpha,beta,lexicon)
	myLDA.initialize()
	myLDA.extract_topics(100)
	myLDA.displayTopics(10)

	"""
	Output obtained with the Associated Press dataset: http://www.cs.princeton.edu/~blei/lda-c/

	Sources used for the implementation:
		* https://www.youtube.com/watch?v=DDq3OVp9dNA
		* https://dl.dropboxusercontent.com/u/55174954/LDA_tutorial.htm
		* http://www.uoguelph.ca/~wdarling/research/papers/TM.pdf
		* http://www.arbylon.net/publications/text-est.pdf

	Command line used: ./simple_LDA.py corpus/ap.txt corpus/vocab.txt 15 0.1 0.001

	Result:

### 15 topics extracted:

Topic #1:  committee:0.0153523078545 house:0.0140939249119 bill:0.0135186641381 senate:0.013015310961 state:0.012619819179 congress:0.0120805122036 budget:0.0107861754625 government:0.0106423602691 sen:0.00931206972966 administration:0.0092761159313 


Topic #2:  department:0.0107853867017 contract:0.00978209958197 economy:0.00973193522598 food:0.00958144215801 futures:0.0084276619703 july:0.00807651147838 month:0.00767519663048 industry:0.00732404613857 health:0.00687256693468 association:0.0067722382227 


Topic #3:  million:0.0246005834567 company:0.0242392936614 new:0.0155683385724 billion:0.00998476900756 corp:0.00998476900756 year:0.00965632373904 co:0.0073572068594 federal:0.0073572068594 business:0.00732436233254 inc:0.00716013969828 


Topic #4:  soviet:0.0317907202693 united:0.0146652841498 war:0.0140262753394 news:0.0134831178505 union:0.0131636134453 east:0.0115021905382 west:0.0110868348114 minister:0.0107992808467 government:0.0101283215958 world:0.00987271807158 


Topic #5:  children:0.0119310856041 mrs:0.0108976872011 family:0.0106471663762 people:0.0104905908606 two:0.0102400700356 hospital:0.00895615080765 women:0.0084237940546 home:0.00789143730154 found:0.00786012219842 wife:0.00751565606409 


Topic #6:  percent:0.0741668355073 year:0.0269589553091 million:0.0262442859705 billion:0.0192167041411 report:0.0149286881097 last:0.014174314919 workers:0.0110774144518 rate:0.0107994874868 increase:0.00913192569678 months:0.00853636791463 


Topic #7:  court:0.0272395573286 case:0.0150783810542 attorney:0.0141691342299 judge:0.0133356579744 drug:0.0130325756996 law:0.0115550496102 trial:0.0112140820511 charges:0.0110625409137 prison:0.0109488850607 federal:0.0109488850607 


Topic #8:  market:0.0297462425527 stock:0.0209749286771 prices:0.0193064722333 oil:0.0168276226598 dollar:0.0161602400823 new:0.0152545065843 trading:0.0136813905088 price:0.0126803166425 york:0.0123466253538 late:0.0115839024081 


Topic #9:  police:0.0334858353342 people:0.012092127013 killed:0.0116580517717 two:0.0101387884272 army:0.00936365406771 military:0.00871254120575 force:0.00818544984132 spokesman:0.00799941759505 air:0.00753433697937 israel:0.00750333160499 


Topic #10:  new:0.0221752539736 year:0.0137108959338 york:0.0106679242418 plant:0.00675053539688 d:0.00675053539688 years:0.00661062865242 last:0.0065756519663 today:0.00608597836069 t:0.00598104830235 time:0.00591109493012 


Topic #11:  bush:0.0286758352896 president:0.028197373609 states:0.0168418830555 united:0.015183215896 reagan:0.01212106114 white:0.0119934713585 american:0.00915459872009 trade:0.00905890638396 washington:0.00845285492184 made:0.00807008557734 


Topic #12:  t:0.0323448163916 i:0.0315262408869 don:0.011924676098 going:0.0110397296064 think:0.010862740308 like:0.0107742456589 time:0.0106636273474 get:0.0103760197377 people:0.00999991747874 years:0.00929196028546 


Topic #13:  iraq:0.0127998511257 board:0.010041643335 two:0.00969686736119 kuwait:0.00823156947238 offer:0.00792989049527 iraqi:0.00775750250835 iran:0.00758511452143 agreed:0.00676627158357 gulf:0.00663698059338 saudi:0.00650768960319 


Topic #14:  city:0.0183318639921 students:0.0111551495286 area:0.0101020446889 fire:0.00971200585932 miles:0.0094779825616 two:0.00885392043434 officials:0.00877591266843 water:0.00873690878548 people:0.00830786607299 southern:0.00826886219004 


Topic #15:  party:0.0235592990721 dukakis:0.015776642402 political:0.0150371139402 campaign:0.0143680167604 south:0.01401586035 democratic:0.0125720190673 government:0.011480334195 people:0.0101069241944 president:0.00978998342505 national:0.0094026113736 

	"""
