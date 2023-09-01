from mylibrary import *
from DeepLearningModels.Declarations.declarations import declaration

@app.route("/declarationPeriode")
def declarationPeriode():
    datalist =declaration.combinationOne.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone
   # print(combinationOne) 
    #datalist = combinationOne.to_dict()
    #datalist = [{k:v} for k, v in datalist.items()]
    #datalist = combinationOne.values.tolist()
    