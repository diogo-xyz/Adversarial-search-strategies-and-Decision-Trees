from Iris.StratifiedCrossValidation import stratifiedFold
from Iris.metrics import *
import csv
import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from copy import deepcopy

class Node:
    def __init__(self,depth):
        self.leaf = False
        self.targetProbabilities = None 
        # Probabilidade de prever cada classe num nó folha
        # key -> target
        # Value -> probabilidade
        self.depth = depth 

        self.leftChild = None
        self.rightChild = None

        self.target = None # classe que o nó folha vai prever  
        self.split = None  # Numero a partir do qual é feito o split
        self.splitPredictor = None # Qual a variavel preditiva que vamos usar para o split


class Tree:
    def __init__(self,predictors,predictorsDomain,dataSet,depth):
        self.node = Node(depth)
        self.dataSet = dataSet

        self.predictors = predictors # Lista com o nome das variaveis preditoras que podem ser utilizadas para fazer o split 
        self.predictorsDomain = predictorsDomain 
        # Dicionario    key: variavel preditora     # values: uma lista de possiveis valores para a variavel

    def ID3(self,maxDepth,minSampleSize):
        '''Cria a árvore ID3'''
        target = np.unique(np.array([data["class"] for data in self.dataSet])) # lista com as targets que estão no dataset
        if self.node.depth < maxDepth and len(self.dataSet) > minSampleSize and len(target) > 1:
            
            infoGain,splitPredictor,split = selectPredictor(self.predictors,self.predictorsDomain,self.dataSet)
            
            if infoGain > 0:
                # Guardar os valores de decisão do nó
                self.node.split = split
                self.node.splitPredictor = splitPredictor
                
                updatePredictors = deepcopy(self.predictors)
                updatePredictors[splitPredictor] -= 1

                if(updatePredictors[splitPredictor] == 0): del updatePredictors[splitPredictor] # Já não pode ser mais utilizado

                # Divide o dataset para o nó esquerdo e para o nó direito
                dataSetLeft = [observation for observation in self.dataSet if observation[splitPredictor] < split]
                dataSetRight = [observation for observation in self.dataSet if observation[splitPredictor] >= split]
                # Cria os nós filhos e chamda recursiva da função para continuar a contruir a arvore 
                self.node.leftChild = Tree(updatePredictors,self.predictorsDomain,dataSetLeft,self.node.depth+1)
                self.node.rightChild = Tree(updatePredictors,self.predictorsDomain,dataSetRight,self.node.depth+1)
                self.node.leftChild.ID3(maxDepth,minSampleSize)
                self.node.rightChild.ID3(maxDepth,minSampleSize)
            else:
                self.node.leaf = True

        else:
            self.node.leaf = True

        if self.node.leaf:
            target = [observation["class"] for observation in self.dataSet]
            values,counts = np.unique(target,return_counts = True)
            commonValue = values[np.argmax(counts)]
            self.node.target = str(commonValue) # O valor mais comum fica como previsão do nó
            self.node.targetProbabilities = self.calcPredictProba(values,counts) 
            #Calculo da probabilidade de prever cada target util para construir o curva ROC-AUC

    def calcPredictProba(self,values,counts):
        '''Calcula a probabilidade de cada target ser prevista no nó'''
        total = sum(counts)
        targetProbabilities = {}
        for target in ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]:

            if(target in values): # class aparece na folha 
                index = list(values).index(target)
                targetProbabilities[target] = float(counts[index] / total)
            else: # A classe não aparece na folha
                targetProbabilities[target] = 0.0
        return targetProbabilities

    def predict(self, sample):
        '''Previsão da ID3'''
        if self.node.leaf:
            return self.node.target,self.node.targetProbabilities
        else:
            if sample[self.node.splitPredictor] < self.node.split:
                return self.node.leftChild.predict(sample)
            else:
                return self.node.rightChild.predict(sample)

    def print(self, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "

        if self.node.leaf:
            print(f"{prefix}{connector}Leaf: class => {self.node.target}")
        else:
            print(f"{prefix}{connector}[depth={self.node.depth}] {self.node.splitPredictor} < {self.node.split}")

        child_prefix = prefix + ("    " if is_last else "│   ")

        if not self.node.leaf:
            self.node.leftChild.print(child_prefix, False)
            self.node.rightChild.print(child_prefix, True)


def calcEntropy(dataSet):
    if len(dataSet) == 0: return 0

    entropy = 0
    targets = ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]

    for target in targets:
        probability = len([observation for observation in dataSet if observation["class"] == target]) / len(dataSet)

        if probability > 0: entropy -= probability * math.log(probability,2)
    return entropy

def calcConditionalEntropy(splitPredictor,split,dataSet):
    
    smaller = [observation for observation in dataSet if observation[splitPredictor] < split]
    greater = [observation for observation in dataSet if observation[splitPredictor] >= split]
    
    probabilitySmaller = len(smaller)/len(dataSet)
    probabilityGreater = len(greater)/len(dataSet)
    conditionalEntropy = probabilitySmaller * calcEntropy(smaller) + probabilityGreater * calcEntropy(greater)
    
    return conditionalEntropy


def selectPredictor(predictors,predictorsDomain,dataSet):
    '''Retorna o ganho de informaçaõ, qual é o melhor atributo para fazer a divisão e o valor que faz a divisão'''
    entropyDataSet = calcEntropy(dataSet)
    
    maxInfoGain = 0
    maxGainPredictor = None
    maxGainSplit = 0

    for predictor in predictors:
        for split in predictorsDomain[predictor]:
            infoGain = entropyDataSet - calcConditionalEntropy(predictor,split,dataSet)
            if infoGain > maxInfoGain:
                maxInfoGain = infoGain
                maxGainPredictor = predictor
                maxGainSplit = split
    return maxInfoGain,maxGainPredictor,maxGainSplit



def readCSV():
    '''Os valores são guardados da seguinte forma:
    {'sepallength': 6.1, 'sepalwidth': 2.6, 'petallength': 5.0, 'petalwidth': 1.5, 'class': 'Iris-versicolor'},
    na lista dataSet'''

    dataSet = []
    with open ("Iris/iris.csv",newline ='') as file:
        data = csv.reader(file,delimiter = ',')
        attributtes = True

        for row in data:
            observation = {}

            if attributtes:
                headers = row 
                # Os headers são sepallength,sepalwidth,petallength,petalwidth e class
                # Só estão na primeira linha do dataSet o que justifica o uso da flag -> attributtes

            if not attributtes:
                for i in range(1,len(row)-1): 
                    observation[headers[i]] = float(row[i])
                observation[headers[len(row)-1]] = row[len(row)-1]
                dataSet.append(observation)
            attributtes = False

    return dataSet

def getPredictorsDomain(dataSet):
    '''Retorna um dicionário: keys --> nomes das variáveis preditoraS;  values --> listas com os valores únicos que cada
    preditor pode ter'''
    
    predictorsDomain = {}
    all_keys = list(dataSet[0].keys())
    predictorsList = [k for k in all_keys if k != 'class'] 

    datanp = np.array([[observation[pred] for pred in predictorsList] for observation in dataSet], dtype=float)

    for i, pred in enumerate(predictorsList):
        valores_unicos = np.unique(datanp[:, i])
        predictorsDomain[pred] = valores_unicos.tolist()

    return predictorsDomain


def evaluateModel(dataSet,predictors,predictorsDomain,seed,depth,minsampleSize):
    '''Através do método Stratified K Fold Cross Validation avaliamos o modelo criado'''

    folds = stratifiedFold(dataSet,seed=seed)
    targets = ["Iris-setosa", "Iris-versicolor", "Iris-virginica"]

    # Listas numpy para guardar as metricas 
    valuesAccuracy = np.array([])
    f1ScoreSetosa = np.array([])
    f1ScoreVersicolor = np.array([])
    f1ScoreVirginica = np.array([])
    aucSetosa = np.array([])
    aucVersicolor = np.array([])
    aucVirginica = np.array([])

    for trainSet,testSet in folds:
        # Criar e treinar a arvore 
        dt = Tree(predictors,predictorsDomain,trainSet,0)
        dt.ID3(depth,minsampleSize)

        # Avaliação da arvore 
        values = {target: [0]*4 for target in targets}
        # key: Nome da classes           Values: [True Positives,False Positives,True Negatives,False Negatives]
        correctPredictions = 0

        trueTragets = [] # Quais são as verdadeiras classes das observações
        targetProbabilitiesLeaf = [] 
        # Uma lista de dicionarios 
        # A probabilidade de prever cada uma das 3 classes do dataSet
        # Guarda o dicionario targetProbabilities

        for observation in testSet:
            predictedTraget,targetProbabilities = dt.predict(observation)

            trueTragets.append(observation["class"])
            targetProbabilitiesLeaf.append(targetProbabilities)
            
            if observation["class"] == predictedTraget:
                correctPredictions += 1 
                values[predictedTraget][0] += 1 # Acrescenta ao TP da classe
                for target in targets: 
                    if target != predictedTraget: values[target][2] += 1 # Acrescenta aos TN da outras classes
            
            else:
                values[observation["class"]][3] += 1 # Acrescenta ao FN da classe que era suposto prever
                values[predictedTraget][1] += 1 # Acrescenta ao FP da calsse que preveu errada

        # Calcula as metricas e guarda cada uma
        valuesAccuracy = np.append(valuesAccuracy, calcAccuracy(correctPredictions, len(testSet)))

        f1Scores = calcf1Score(values)
        f1ScoreSetosa = np.append(f1ScoreSetosa,f1Scores[0])
        f1ScoreVersicolor = np.append(f1ScoreVersicolor,f1Scores[1])
        f1ScoreVirginica = np.append(f1ScoreVirginica,f1Scores[2])

        rocAuc = roc_auc(trueTragets,targetProbabilitiesLeaf)
        aucSetosa = np.append(aucSetosa,rocAuc[0])
        aucVersicolor = np.append(aucVersicolor,rocAuc[1])
        aucVirginica = np.append(aucVirginica,rocAuc[2])

    accuracy = np.mean(valuesAccuracy)
    f1Score = np.mean([np.mean(f1ScoreSetosa),np.mean(f1ScoreVersicolor),np.mean(f1ScoreVirginica)])
    auc = np.mean([np.mean(aucSetosa),np.mean(aucVersicolor),np.mean(aucVirginica)])
    return accuracy,f1Score,auc

def gridSearch():
    '''Esta função permite encontrar os melhores hiper parametros para a ID3 através do algortimo grid Search'''
    
    dataSet = readCSV()
    predictorsDomain = getPredictorsDomain(dataSet) # Os valores possiveis de cada atributo
    # Valores que o grid Search vai usar 
    depths = [2, 3, 4, 5]
    minsampleSize = [2, 3, 4, 5]

    results = []
    best_acc = {"depth": None, "minSize": None, "value": -1} # Guarda os melhores hiper parametros 

    for d in depths:
        for m in minsampleSize:
            predictors = {"sepallength":2, "sepalwidth":2,"petallength":2, "petalwidth":2}  # Quantas vezes cada atributo pode ser usado
            acc, f1, auc = evaluateModel(dataSet, predictors, predictorsDomain,15,d,m) # Avalia o modelo
            results.append((d, m, acc, f1, auc))

            if acc > best_acc["value"]:
                best_acc.update({"depth": d, "minSize": m, "value": acc})

    df = pd.DataFrame(results, columns=["depth","minSize","accuracy","f1Score","rocAuc"]) # Guarda os resultados num dataset
    pivots = {
        "accuracy": df.pivot(index="minSize", columns="depth", values="accuracy"),
        "f1Score":  df.pivot(index="minSize", columns="depth", values="f1Score"),
        "rocAuc":   df.pivot(index="minSize", columns="depth", values="rocAuc"),}

    fig, axes = plt.subplots(1, 3, figsize=(15,5), sharey=True)
    title = {"accuracy": "Accuracy", "f1Score":"F1-score", "rocAuc":"ROC-AUC"}

    for ax, (metric, pivot) in zip(axes, pivots.items()): # Construi o grafico para cada métrica
        im = ax.imshow(
            pivot.values,
            origin="lower",
            aspect="auto",
            cmap="viridis"
        )
        ax.set_title(title[metric])
        ax.set_xlabel("max_depth")
        ax.set_xticks(np.arange(len(pivot.columns)))
        ax.set_xticklabels(pivot.columns)
        if ax is axes[0]:
            ax.set_ylabel("min_samples_split")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

    # Desenha e guarda o grafico para cada métrica 
    fig.suptitle("Grid Search Metrics", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig("Iris/grid_search_all_metrics.png")
    plt.show() 
    plt.close()

    print(f"Melhor max_depth: {best_acc['depth']}")
    print(f"Melhor min_samples_split: {best_acc['minSize']}")
    print(f"Melhor accuracy: {best_acc['value']:.4f}")

def mainID3():
    '''Cria a '''
    dataSet = readCSV()
    predictorsDomain = getPredictorsDomain(dataSet) # Os valores possiveis de cada atributo

    predictors = {"sepallength":2,"sepalwidth":2,"petallength":2,"petalwidth":2} # Quantas vezes cada atributo pode ser usado

    accuracy,f1Score,auc = evaluateModel(dataSet,predictors,predictorsDomain,15,3,2) # Avalia o modelo

    # Cria a ID3 
    dt = Tree(predictors,predictorsDomain,dataSet,0)
    dt.ID3(3,2)
    dt.print("")

    return dt,accuracy,f1Score,auc