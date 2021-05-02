import numpy


products = {}

name = ['milano chocolate chip cookies', 'all Out Ultra', 'Mad Angles', 'cornflakes']
brandName = ['parle', 'allOut', 'Britania', 'Kellogs', 'Bingo', 'Tops']
brandToProd = {'parle' : ['milano chocolate chip cookies'], 'bingo' : ['Mad Angles'], 'Kellogs' : ['cornflakes']}

def clean_corpus(corpus):
	
	cleaned = []
	n = len(corpus)
	for i in range(n):
		curr = corpus[i]
		score = curr['score']
		pred = curr['pred']
		pred =  pred.lower()

		cleaned.append((score,pred))

	cleaned.sort(key=lambda x:x[0])
	return np.array(cleaned)



def getBrand(corpus):

	for b in brandName:
		if(b in corpus):
			return b
	return ""


def getProduct(corpus):
	corpus = clean_corpus(corpus)
	brand = getBrand(np.squeeze(corpus[:,1]))
	btp = brandToProd[brand]
	corpus2 = np.delete(np.squeeze(corpus[:,1]),np.where(l == brand)[0][0])
	corpus2.sort()


	max_s = 0
	max_p = []
	for prod in btp:
		l = prod.split()
		l.sort()
		l2 = intersection(corpus2,l)
		if(max_s > len(l2)):
			max_s = len(l2)
			max_p = prod
	return prod


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3




