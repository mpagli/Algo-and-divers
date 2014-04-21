#!/usr/bin/python

def simpleDistance(s1,s2):
	"""Compute the distance between two strings considering deletions, insertions
	and substitution, all the weights are set to 1"""
	mem = [[i+j for j in range(len(s1)+1)] for i in range(len(s2)+1)]
	for j in range(1,len(s1)+1):
		for i in range(1,len(s2)+1):
			if s1[j-1] == s2[i-1]:
				mem[i][j]= mem[i-1][j-1]
			else : 
				mem[i][j]= 1 + min(mem[i-1][j-1],mem[i][j-1],mem[i-1][j])
	return mem[len(s2)][len(s1)]

def weightedDistance(s1,s2,weights):
	"""Compute the distance between two strings considering deletions, insertions
	and substitution, look for substitutions weights in the weights dictionary"""
	mem = [[float(i+j) for j in range(len(s1)+1)] for i in range(len(s2)+1)]
	for j in range(1,len(s1)+1):
		for i in range(1,len(s2)+1):
			if s1[j-1] == s2[i-1]:
				mem[i][j]= mem[i-1][j-1]
			else : 
				substWeight = weights(s1[j-1])(s2[i-1])
				mem[i][j]= min(substWeight+mem[i-1][j-1],1.0+mem[i][j-1],1.0+mem[i-1][j])
	return mem[len(s2)][len(s1)]

if __name__ == "__main__" :
	print simpleDistance("avt","avait")