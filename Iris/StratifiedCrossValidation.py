import random

def createSubLists(data, lenSublist):
    return [data[i:i+lenSublist] for i in range(0,len(data),lenSublist)]

def stratifiedFold(dataSet, k = 5,seed = None):
    if seed is not None: random.seed(seed)

    groupTragets = {}
    # Key: nome da classe
    # Value: todas as observações que são da classe  
    for observation in dataSet:
        target = observation["class"]
        if target not in groupTragets:
            groupTragets[target] = []
        groupTragets[target].append(observation)


    # Dividir de forma igual todas as obsrevações da classe em k folds
    # Ou seja, temos 50 observações de uma classe e k = 5, é feito 5 listas cada uma com 10 observações
    # Os values do dicionario groupTragets passa a ser uma lista de listas  
    for target,observation in groupTragets.items():
        random.shuffle(observation)
        groupTragets[target] = createSubLists(observation,len(observation)//k)

    
    # A lista folds guarda k tuples (trainSet,testSet)
    folds = []
    for i in range(k):

        testSet = []
        trainSet = []
        for target in groupTragets:
            
            testSet.extend(groupTragets[target][i])

            for j in range(k):
                if i != j:
                    trainSet.extend(groupTragets[target][j])
        folds.append((trainSet,testSet))
    
    return folds