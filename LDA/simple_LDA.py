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
		self.alpha  = float(alpha) #parameter of the Dirichlet distribution for per document topics
		self.beta   = float(beta)  #parameter of the Dirichlet distributions for per topic words
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
		cardinal = []	#store the number of words for this topic to normalize
		for idx,t in enumerate(self.n_wt):
			topics.append(filter(lambda x: x[1]!=0, [(k,t[k]) for k in t]))
			cardinal.append(sum([float(x[1]) for x in topics[idx]]))

		#sorting the lists
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
				print w[0]+":"+str(w[1]/cardinal[idx]),
			print "\n\n"



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

					#multinomial sampling: reassign w a new topic choosen with probability p(t|doc)*p(w|t) 
					dist = []

					for k in xrange(self.numTopics): 
						p_w_t  = (self.n_wt[k][w] + self.beta) / (self.n_t[k] + self.beta * len(self.lexicon));
						p_t_d  = (self.n_dt[doc][k] + self.alpha) / (self.n_d[doc] + self.alpha * self.numTopics);
						dist.append(p_w_t*p_t_d)

					s = sum(dist)
					dist = map(lambda x : x/s, dist) #normalization

					newTopic = self.sampleFromTopics(dist)

					self.corpus[doc][idx]     = (w,newTopic)
					self.n_dt[doc][newTopic] += 1
					self.n_wt[newTopic][w]   += 1
					self.n_t[newTopic]       += 1
					self.n_d[doc]	  		 += 1



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
	Output obtain with the Associated Press dataset: http://www.cs.princeton.edu/~blei/lda-c/

	Sources used for the implementation:
		* https://www.youtube.com/watch?v=DDq3OVp9dNA
		* https://dl.dropboxusercontent.com/u/55174954/LDA_tutorial.htm
		* http://www.uoguelph.ca/~wdarling/research/papers/TM.pdf
		* http://www.arbylon.net/publications/text-est.pdf

	Command line used: ./simple_LDA.py corpus/ap.txt corpus/vocab.txt 15 25 0.01

	Result:

### 15 topics extracted:

	Topic #1:  thursday:0.0229041967962 market:0.0215894543819 week:0.0196865377296 trade:0.0163996816939 prices:0.0163304847248 economic:0.0158461059406 friday:0.0153963256409 stock:0.0151195377642 late:0.0148427498876 earlier:0.0146005604955 


	Topic #2:  president:0.0338066977533 time:0.0174862229758 congress:0.0167443832132 support:0.0149780980642 plan:0.0148014695492 state:0.0144482125194 called:0.0138830012717 family:0.0132471386181 system:0.0128232301823 leaders:0.011410202063 


	Topic #3:  officials:0.0348796651552 two:0.0222183467039 air:0.015730728985 meeting:0.0148936170213 minister:0.0141960237182 agency:0.0138123474015 security:0.0137425880712 saying:0.0135333100802 mrs:0.0118590861528 held:0.0118590861528 


	Topic #4:  percent:0.0644871325365 year:0.0521356993042 million:0.051702899757 billion:0.0285647701169 company:0.0252688351034 month:0.0151812764257 business:0.0142823850584 bank:0.0130172786896 sales:0.0111529114093 corp:0.0101208509505 


	Topic #5:  bush:0.0372487989715 united:0.0339332837134 states:0.03379795656 american:0.0246972054943 world:0.0200622504906 military:0.0200284187022 president:0.0192502875702 war:0.0161377630422 force:0.0137018742811 washington:0.0121456120171 


	Topic #6:  government:0.0517824162804 country:0.0192006133045 political:0.0185385231906 official:0.0164825591525 administration:0.016308324912 told:0.0154720005575 program:0.0154371537094 committee:0.015297766317 defense:0.0149144509879 agreement:0.0133463428233 


	Topic #7:  federal:0.0253187094936 just:0.0206181895876 members:0.0182679296346 office:0.0181610996368 money:0.0160244996795 last:0.0152766896945 death:0.01150202977 prison:0.0101844597963 t:0.0100064097999 five:0.00954347980913 


	Topic #8:  people:0.0579154579362 police:0.0372979693328 two:0.0245199613206 three:0.0200649260948 home:0.0187525901368 killed:0.0138485978726 children:0.0131578947368 spokesman:0.0129161486393 man:0.0125017267578 four:0.0121563751899 


	Topic #9:  soviet:0.0350747320925 monday:0.0248519458545 city:0.0247814438804 party:0.0235829103215 news:0.0232304004512 union:0.0214678510998 west:0.0189297800338 east:0.0146291596165 gorbachev:0.014029892837 national:0.0120558375635 


	Topic #10:  new:0.0714755776543 tuesday:0.0212050307107 york:0.0196329336063 last:0.0149532026908 higher:0.0123208540509 number:0.0116627668909 cents:0.0103465925709 close:0.0102003509798 lower:0.00994442819538 announced:0.00972506580872 


	Topic #11:  report:0.0217619963005 day:0.021435566356 today:0.0162489572377 found:0.0156686373363 service:0.0153784773857 general:0.014653077509 months:0.0144717275398 came:0.0138551376446 attorney:0.013564977694 drug:0.0128758478111 


	Topic #12:  court:0.0257153075823 law:0.0158798283262 case:0.0155579399142 north:0.0153075822604 judge:0.0125894134478 rights:0.01169527897 charges:0.0107296137339 trial:0.0105865522175 university:0.010443490701 district:0.00979971387697 


	Topic #13:  years:0.0289417301816 house:0.0213199395877 t:0.0187559270837 work:0.0169997541358 going:0.015946050367 state:0.0158055565312 says:0.0142250008781 department:0.0140845070423 bill:0.0135576551579 good:0.0129254328966 


	Topic #14:  i:0.0486506644969 t:0.0266815839436 m:0.0202739354489 like:0.0152224030377 dukakis:0.0151545972335 campaign:0.0151206943314 reagan:0.0150528885273 don:0.0139001898563 think:0.0128152969894 democratic:0.0126796853811 


	Topic #15:  first:0.0301441210046 south:0.0206549657534 john:0.0141623858447 years:0.0138056506849 take:0.0131278538813 director:0.0120576484018 high:0.0113798515982 wednesday:0.0113441780822 times:0.0106307077626 see:0.00988156392694 


	"""
