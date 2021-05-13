import numpy as np
import copy

products = {}

name = ['milano chocolate chip cookies', 'all Out Ultra', 'Mad Angles', 'cornflakes']
brandName = ['parle', 'allOut', 'Britania', 'Kellogs', 'bingo', 'Tops', 'know', 'tasty', 'fevikwik']
brandToProd = {'parle' : ['milano chocolate chip cookies'], 'bingo' : ['Mad Angles'], 'Kellogs' : ['cornflakes'], 'tasty' : ['tomato', 'ketchup'], 'know' : ['tomato', 'chatpata', 'cup', 'soup']}
brandToprice = {'tasty' : 120, 'know' : 10, 'fevikwik' : 5}

def clean_corpus(corpus):
	
	cleaned = []
	n = len(corpus)
	for i in range(n):
		curr = corpus[i]
		# score = curr['score']
		pred = curr['pred']
		pred =  pred.lower()

		cleaned.append((0.99,pred))

	cleaned.sort(key=lambda x:x[0])
	return np.array(cleaned)



def getBrand(corpus):

	for b in brandName:
		if(b.lower() in corpus):
			return b.lower()
	return ""


def getProduct(corpus):
	c1 = copy.deepcopy(corpus)
	try :
		c2 = copy.deepcopy(corpus)
		corpus = clean_corpus(c2)
		brand = getBrand(np.squeeze(corpus[:,1]))
		btp = brandToProd[brand]
		corpus2 = list(np.delete(np.squeeze(corpus[:,1]),np.where(np.squeeze(corpus[:,1]) == brand)[0][0]))
		corpus2.sort()
		btp.sort()


		# max_s = 0
		# max_p = []
		# for prod in btp:
		# 	l = prod.split()
		# 	l.sort()
		# 	print(l)
		# 	l2 = intersection(corpus2, l)
		# 	if(max_s > len(l2)):
		# 		max_s = len(l2)
		# 		max_p = prod
		price = brandToprice[brand]
		return brand,corpus2,price
	except:
		corpus = clean_corpus(c1)
		corpus = np.squeeze(corpus[:,1])
		corpus.sort()

		max_p = 0
		max_l = []
		max_b = []

		for b in brandToProd.keys():
			l = brandToProd[b]
			l2 = intersection(l,corpus)
			if(max_p <len(l2) ):
				max_l = l2
				max_b = b
				max_p = len(l2)
		return max_b, max_l, brandToprice[max_b]


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3




if __name__ == "__main__":
	corpus = [{'score': 0.9978, 'pred': 'tomato'}, {'score': 0.9999, 'pred': 'ketchup'}]
	b,cp,p = getProduct(corpus)
	print(b,cp,p)