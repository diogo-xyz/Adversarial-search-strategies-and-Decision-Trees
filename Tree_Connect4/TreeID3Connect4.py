import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from copy import deepcopy
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix,ConfusionMatrixDisplay,classification_report
from joblib import dump,load
from mpl_toolkits.mplot3d import Axes3D

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

        self.target = None # calsse que o nó folha vai prever  
        self.splitPredictor = None # Qual a variavel preditiva que vamos usar para o split

class Tree:
    def __init__(self,predictors,dataSet,depth):
        self.node = Node(depth)
        self.dataSet = dataSet

        self.predictors = predictors # Lista com o nome das variaveis preditoras que podem ser utilizadas para fazer o split 

    def ID3(self,maxDepth,minSampleSize,minSampleSplit):
        '''Cria a árvore ID3'''
        target = np.unique(np.array([data["move"] for data in self.dataSet])) # lista com as targets que estão no dataset
        if self.node.depth < maxDepth and len(self.dataSet) >= minSampleSize and len(self.dataSet) >= minSampleSplit and len(target) > 1 and self.predictors != 0:
            
            infoGain,splitPredictor = selectPredictor(self.predictors,self.dataSet)

            if infoGain > 0:
                # Guardar os valores de decisão do nó
                self.node.splitPredictor = splitPredictor

                updatePredictors = deepcopy(self.predictors)
                updatePredictors.remove(splitPredictor)
                # Divide o dataset para o nó esquerdo e para o nó direito
                dataSetLeft = [observation for observation in self.dataSet if observation[splitPredictor] == 0]
                dataSetRight = [observation for observation in self.dataSet if observation[splitPredictor] == 1]
                # Cria os nós filhos e chamda recursiva da função para continuar a contruir a arvore 
                self.node.leftChild = Tree(updatePredictors,dataSetLeft,self.node.depth+1)
                self.node.rightChild = Tree(updatePredictors,dataSetRight,self.node.depth+1)
                self.node.leftChild.ID3(maxDepth,minSampleSize,minSampleSplit)
                self.node.rightChild.ID3(maxDepth,minSampleSize,minSampleSplit)
            else:
                self.node.leaf = True

        else:
            self.node.leaf = True

        if self.node.leaf:
            target = [observation["move"] for observation in self.dataSet]
            values,counts = np.unique(target,return_counts = True)
            commonValue = values[np.argmax(counts)]
            self.node.target = commonValue # O valor mais comum fica como previsão do nó
            self.node.targetProbabilities = self.calcPredictProba(values,counts)
            #Calculo da probabilidade de prever cada target util para construir o curva ROC-AUC

    def calcPredictProba(self,values,counts):
        '''Calcula a probabilidade de cada target ser prevista no nó'''
        total = sum(counts)
        targetProbabilities = {}
        for target in [0,1,2,3,4,5,6]:

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
            if sample[self.node.splitPredictor] == 0:
                return self.node.leftChild.predict(sample)
            else:
                return self.node.rightChild.predict(sample)
            
    def print(self, prefix="", is_last=True):
        connector = "└── " if is_last else "├── "

        if self.node.leaf:
            print(f"{prefix}{connector}Leaf: class => {self.node.target}")
        else:
            print(f"{prefix}{connector}[depth={self.node.depth}] {self.node.splitPredictor} = 0")

        child_prefix = prefix + ("    " if is_last else "│   ")

        if not self.node.leaf:
            self.node.leftChild.print(child_prefix, True)
            self.node.rightChild.print(child_prefix, False)



def calcEntropy(dataSet):
    if len(dataSet) == 0: return 0

    entropy = 0
    targets = [0,1,2,3,4,5,6]

    for target in targets:
        probability = len([observation for observation in dataSet if observation["move"] == target]) / len(dataSet)

        if probability > 0: entropy -= probability * math.log(probability,2)
    return entropy


def calcConditionalEntropy(splitPredictor,dataSet):

    left = [observation for observation in dataSet if observation[splitPredictor] == 0]
    right = [observation for observation in dataSet if observation[splitPredictor] == 1]
    
    probabilityLeft = len(left)/len(dataSet)
    probabilityRight = len(right)/len(dataSet)
    conditionalEntropy = probabilityLeft * calcEntropy(left) + probabilityRight * calcEntropy(right)
    
    return conditionalEntropy

def selectPredictor(predictors,dataSet):
    '''Retorna o ganho de informaçaõ, qual é o melhor atributo para fazer a divisão e o valor que faz a divisão'''
    entropyDataSet = calcEntropy(dataSet)

    maxInfoGain = 0
    maxGainPredictor = None

    for predictor in predictors:
        infoGain = entropyDataSet - calcConditionalEntropy(predictor,dataSet)
        if infoGain > maxInfoGain:
            maxInfoGain = infoGain
            maxGainPredictor = predictor
    return maxInfoGain,maxGainPredictor


def readCSV(test_size=0.3, random_state=42):
    df = pd.read_csv("Tree_Connect4/connect4_Dataset.csv", dtype=int)
    dataSet = df.to_dict(orient="records")
    headers = df.columns[:-1].tolist()

    # Realiza uma divisão estratificada do dataset
    train_data, test_data = train_test_split(dataSet, test_size=test_size, random_state=random_state, stratify = df.iloc[:,-1] )

    return train_data, test_data, headers

def gridSearch():
    '''Esta função permite encontrar os melhores hiperparametros para a ID3 através do algortimo grid Search'''
    trainSet, testSet, predictors = readCSV()
    # Valores que o grid Search vai usar 
    depth = [9, 10, 11, 12]
    minSampleSize = [10, 15, 20, 35]
    minSampleSplit = [15, 20, 35, 40]

    results = []
    bestAccuracy = -1

    for d in depth:
        for minSize in minSampleSize:
            for minSplit in minSampleSplit:
                if minSplit <= minSize:
                    continue
                dt = Tree(predictors, trainSet, 0)
                dt.ID3(d, minSize, minSplit)

                y_test = []
                y_pred = []
                for sample in testSet:
                    predictedTarget, _ = dt.predict(sample)
                    y_test.append(sample["move"])
                    y_pred.append(predictedTarget)

                report_dict = classification_report(y_test, y_pred, output_dict=True) # Avalia o modelo
                # Guarda os resultados
                accuracy = report_dict['accuracy']
                f1Score = report_dict['macro avg']['f1-score']
                results.append((d, minSize, minSplit, accuracy, f1Score))

                if accuracy > bestAccuracy:
                    bestDepth = d
                    bestSampleSize = minSize
                    bestSampleSplit = minSplit
                    bestAccuracy = accuracy

    # Separar resultados em arrays
    depths, minSizes, minSplits, accuracies, f1Scores = zip(*results)

    # Plot 3D para Accuracy
    fig = plt.figure(figsize=(14, 6))

    ax1 = fig.add_subplot(121, projection='3d')
    scatter1 = ax1.scatter(depths, minSizes, minSplits, c=accuracies, cmap='viridis', s=60)
    ax1.set_title("Accuracy")
    ax1.set_xlabel("Max Depth")
    ax1.set_ylabel("Min Sample Size")
    ax1.set_zlabel("Min Sample Split")
    fig.colorbar(scatter1, ax=ax1, label="Accuracy")

    # Plot 3D para F1 Score
    ax2 = fig.add_subplot(122, projection='3d')
    scatter2 = ax2.scatter(depths, minSizes, minSplits, c=f1Scores, cmap='plasma', s=60)
    ax2.set_title("F1 Score (Macro Avg)")
    ax2.set_xlabel("Max Depth")
    ax2.set_ylabel("Min Sample Size")
    ax2.set_zlabel("Min Sample Split")
    fig.colorbar(scatter2, ax=ax2, label="F1 Score")

    plt.tight_layout()

    # Guardar os gráficos
    fig.savefig("Tree_Connect4/gridsearch_connect4.png", dpi=300)
    print("Gráfico salvo como 'gridsearch_connect4.png'")

    print("\nMelhores parâmetros encontrados:")
    print("Max Depth:", bestDepth)
    print("Min Sample Size:", bestSampleSize)
    print("Min Sample Split:", bestSampleSplit)

def createTree():
    trainSet,testSet,predictors = readCSV()

    # Cria a ID3 
    dt = Tree(predictors,trainSet,0)
    dt.ID3(12,10,15)
    
    # Verificamos quais foram as previsões corretas para o dataset teste e calculamos a accuracy
    y_test = [] # Classe verdadeira
    y_prev = [] # Classe prevista pela árvore
    accuracy = 0 
    for sample in testSet:
        predictedTraget,_ = dt.predict(sample)
        y_test.append(sample["move"])
        y_prev.append(predictedTraget)
        if sample["move"] == predictedTraget:
            accuracy += (1/len(testSet))
    print("accuracy on test set: ",(accuracy * 100),"%")

    # Cria a confuison matrix
    cm = confusion_matrix(y_test, y_prev)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(cmap='Blues')
    plt.title("Confusion Matrix")
    plt.savefig("Tree_Connect4/confusion_matrix.png")
    plt.show()
    plt.close()

    # Avalia o modelo
    report = classification_report(
        y_test,
        y_prev,
        labels = [0,1,2,3,4,5,6],
        target_names=[f"coluna_{c}" for c in [0,1,2,3,4,5,6]],
        digits=3)
    print(report)

    report_dict = classification_report(y_test, y_prev, output_dict=True)
    accuracy = report_dict['accuracy']
    f1Score = report_dict['macro avg']['f1-score'] 

    dump(dt, "Tree_Connect4/my_tree.joblib") # Guarda a arvore num ficheiro my_tree.joblib 
    return dt,accuracy,f1Score

def loadTree():
    loaded_tree = load("Tree_Connect4/my_tree.joblib") # Carrega a árvore gerada
    return loaded_tree