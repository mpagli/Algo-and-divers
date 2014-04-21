#!/usr/bin/python

def Viterbi(hiddenStates, observations, obs_names, start_proba, trans_proba, emit_proba ):
	"""Implementation of the Viterbi algorithm, the parameters are : 
	- hiddenStates : a list of possible hidden states 
	- observations : a list containing the observations 
	- obs_names    : a list containing the possible observations
	- start_proba  : a list containing all the start proba for each hidden state (reference by index)
	- trans_proba  : a list of list containig the transition proba (reference to hidden state by index)
	- emit_proba   : same as above but for emission proba : [[P(O1|H1), P(O2|H1) ... ],[],[],...]  """

	path = []	

	NumHStates = len(hiddenStates)

	trace = [[0 for y in range(NumHStates)] for x in observations]

	#Initialization : 
	for i in range(NumHStates):
		trace[0][i] = start_proba[i] * emit_proba[i][obs_names.index(observations[0])]

	path = [[hiddenStates[x]] for x in range(NumHStates)]

	for i,obs in enumerate(observations):
		
		if i == 0:
			continue

		newPath = []

		for m in range(NumHStates):	
			(proba, pth) = max((trace[i-1][n] * trans_proba[n][m] * emit_proba[m][obs_names.index(obs)], n) for n in range(NumHStates))
			trace[i][m]= proba
			newPath.append(path[pth]+[hiddenStates[m]])

		path = newPath

	#return the most probable path:
	(maxProba,pth) = max((trace[len(observations)-1][n], n) for n in range(NumHStates))
	return (maxProba, path[pth])

#Test 
if __name__ == "__main__":
	
	hiddenStates = ['1','2']					#2 unfair coins
	observations = list("HTTHTTHHTTHTTTHHTHHTTHTTTTHTHHTHTHHTTTH")#these are the observations, what is the most probable seq of coins ?
	obs_names    = ['H','T']					#the order matters 
	start_proba  = [.5,.5]						#same proba to start with coin1 or coin2
	trans_proba  = [[.4,.6],[.9,.1]]			
	emit_proba   = [[.49,.51],[.85,.15]]

	res = Viterbi(hiddenStates, observations, obs_names, start_proba, trans_proba, emit_proba )

	print "Path : "+','.join(res[1])
	print "Associated probability :",res[0]
