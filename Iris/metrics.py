import numpy as np

def calcAccuracy(correctPredictions,totalPredictions):
    return correctPredictions/totalPredictions

def calcf1Score(values):
    '''Calcula o F1 score para cada classe'''
    # values --> key: Nome da calsse    Values: [True Positives,False Positives,True Negatives,False Negatives]
    f1Score = []
    for confusionValues in values.values():
        
        precision = confusionValues[0] / (confusionValues[0] + confusionValues[1])  if (confusionValues[0] + confusionValues[1]) > 0 else 0.0
        recall = confusionValues[0] / (confusionValues[0] + confusionValues[3]) if (confusionValues[0] + confusionValues[3]) > 0 else 0.0
        f1Score.append( (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0 )

    return f1Score

def calc_ROC_AUC(trueTragets,porbScores, positiveTarget):
    '''Calcula o ROC-AUC score para cada classe'''
    targetTrue = np.array([1 if label == positiveTarget else 0 for label in trueTragets])
    targetScore = np.array([probs[positiveTarget] for probs in porbScores])

    # targetTrue --> lista:  se preveu corretamente a classe caso contrario 0
    # targetScore --> lista: qual é a probabilidade da calsse ter sido prevista

    sorted_indices = np.argsort(-targetScore)
    targetTrue = targetTrue[sorted_indices]
    targetScore = targetScore[sorted_indices]

    tp = 0
    fp = 0
    fn = np.sum(targetTrue)
    tn = len(targetTrue) - fn

    tprList = [] # Lista para os valores true positive rate
    fprList = [] # Lista para os valores false positive rate

    for label in targetTrue:
        if label == 1:
            tp += 1
            fn -= 1
        else:
            fp += 1
            tn -= 1

        tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        tprList.append(tpr)
        fprList.append(fpr)

    # Calcular AUC através da regra do trapézio
    auc = np.trapz(tprList, fprList)

    return float(auc)

def roc_auc(trueTragets,targetProbabilitiesLeaf):
    '''Calcula o ROC-AUC para cada uma das targets'''
    # trueTragets --> Quais são as verdadeiras classes das observações
    # targetProbabilitiesLeaf --> Uma lista de dicionarios:  probabilidade de prever cada uma das 3 classes, no nó folha
    auc = []
    for target in ['Iris-setosa', 'Iris-versicolor', 'Iris-virginica']:
        auc.append(calc_ROC_AUC(trueTragets, targetProbabilitiesLeaf, target))
    return auc
    