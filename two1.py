from mylibrary import *
from Prediction import predictNew

rest_port = 8040
eureka_client.init(eureka_server="http://localhost:8761/eureka",
                   app_name="flaskapi-machine-learning-model-service",
                    instance_ip="192.168.0.103",
                   instance_port=rest_port)

app = Flask(__name__)

@app.route("/newprediction", methods=['POST'])
def create_prediction():
     try:                       
        data = request.json
        p=predictNew.predictNew(**data)
         
        # Make predictions on validation dataset
        predictions = model.predict([[p.chifreaffaire,p.taxesuposetodeclare,p.taxdeclared,p.enterpriseid]])
        # Evaluate predictions            
        result=int("".join(map(str, predictions)))
        print(result)    
        if result ==0:
            val01=accuracy_score(predictions, y_pred=predictions)
            g=val01/0.01
            r = round(g, 1)
            pp='Not fraud with accurate: {r:.1f}%'.format(r=r) 
            respone = jsonify(pp)
            respone.status_code = 200
            return respone
        elif result ==2:
            val01=accuracy_score(predictions, y_pred=predictions)
            g=val01/0.01
            r = round(g, 1)
            pp='Over declaration with accurate: {r:.1f}%'.format(r=r) 
            respone = jsonify(pp)
            respone.status_code = 200
            return respone
        elif result ==1:
            val01=accuracy_score(predictions, y_pred=predictions)
            g=val01/0.01
            r = round(g, 1)
            pp='fraud with accurate: {r:.1f}%'.format(r=r) 
            respone = jsonify(pp)
            respone.status_code = 200
            return respone
        else:
            print('no value')
            respone = jsonify("no value")
            return respone
        

     except Exception as e:
        print(e)
  
           
    
@app.route("/reportClasification")
def reportClasification(): 
  
    try:
        df = pd.read_excel('ChiffreAffaire.xlsx')
        #print(chiffreaffaireRows)
        global data1
        global data
        global dataD
        
        data = pd.DataFrame(df)
        print(data.dtypes)

        ## calculate the tax exact depending on the ChiffreAfaire
        data1=data
        data1['taxesuposetodeclare']=data1['chifreaffaire'].astype(float) *(0.18)
        data1.loc[:, "taxesuposetodeclare"] = data1["taxesuposetodeclare"].map('{:.2f}'.format)
        #convet data1 to foat
        data1['taxesuposetodeclare'] = data1['taxesuposetodeclare'].astype(float)
        data1.drop(['id'], axis=1,inplace=True)
        
        df1 = pd.read_excel('DeclaretionEnterpriseId.xlsx')
        dataD = pd.DataFrame(df1)
        print(dataD.dtypes)
        global combination
        combination= pd.DataFrame()
        combination['enterprisename']=data1['enterprisename'].copy()
        combination['chifreaffaire']=data1['chifreaffaire'].copy()
        combination['taxesuposetodeclare']=data1['taxesuposetodeclare'].copy()
        combination['taxdeclared']=dataD['taxdeclared'].copy()
        combination['datatopay']=data1['datatopay'].copy()
        combination['datepayed']=dataD['datepayed'].copy()
        combination['enterpriseid']=dataD['enterpriseid'].copy()
        combination.loc[:,"chifreaffaire"] = combination["chifreaffaire"].map('{:.2f}'.format)
        combination['chifreaffaire'] = combination['chifreaffaire'].astype(float)

        # Used to convert the difference in terms of months
        combination['periode'] = ((combination.datatopay - combination.datepayed)/np.timedelta64(1, 'M'))
        combination['periode'] = combination['periode'].astype(int)
        combination['defferencetaxe'] = combination['taxesuposetodeclare'] - combination['taxdeclared'] 
        combination['datepayed'] = combination['datepayed'].dt.strftime('%Y-%m-%d')
        combination['datatopay'] = combination['datatopay'].dt.strftime('%Y-%m-%d')
        dataD['datepayed'] = dataD['datepayed'].dt.strftime('%Y-%m-%d')
        dataD['datatopay'] = dataD['datatopay'].dt.strftime('%Y-%m-%d')

    except Exception as e:
        print(e)
     
    
    #CALCULATE THE periode WITH O VALUES
    global Exact1
    Exact1= pd.DataFrame()
    Exact1=combination.loc[combination['periode'] == 0]
    ## Calculation of Penality depending on periode
    ## let suppose they charge penality 3%
    Exact1['penelity'] = 0.0
    Exact1['totalpenelity'] = Exact1['defferencetaxe'].astype(float) + Exact1['penelity'].astype(float)
    Exact1=Exact1.reset_index(drop=True)
    print(len(Exact1))
   
     #ALL ENTERPRISE WHICH DIDN'T DECLARE WITH FRAUD
    global Exact0
    Exact0= pd.DataFrame()
    Exact0=Exact1.loc[Exact1['defferencetaxe'] == 0]
    Exact0['result'] =0
    Exact0=Exact0.reset_index(drop=True)
    print(len(Exact0))
     ##ALL ENTERPRISE WHICH DECLARE WITH FRAUD
    global Exact01
    Exact01= pd.DataFrame()
    Exact01=Exact1.loc[Exact1['defferencetaxe'] >0]
    Exact01['result'] =1
    Exact01=Exact01.reset_index(drop=True)
    print(Exact01)
    #Advance payment in the exact periode 
    global Exact012
    Exact012= pd.DataFrame()
    Exact012=Exact1.loc[Exact1['defferencetaxe'] <0]
    Exact012['result'] =2
    Exact012=Exact012.reset_index(drop=True)
    print(Exact012)
   

   #CALCULATE THE periode WITH positive VALUES
    global Positive
    Positive= pd.DataFrame()
    Positive=combination.loc[combination['periode'] > 0]
## Calculation of Penality depending on periode
## let suppose they charge penality 3%
    Positive['penelity'] = Positive['taxesuposetodeclare'] * 0.03 * Positive['periode']
    Positive['totalpenelity'] = Positive['defferencetaxe'].astype(float) + Positive['penelity'].astype(float)
    Positive=Positive.reset_index(drop=True)
    
    #ALL ENTERPRISE WHICH  DECLARE WITH FRAUD
    global Positive0
    Positive0= pd.DataFrame()
    Positive0=Positive.loc[Positive['defferencetaxe'] > 0]
    Positive0['result'] = 3
    Positive0=Positive0.reset_index(drop=True)
    
    #ALL ENTERPRISE WHICH DIDN'T DECLARE WITH FRAUD
    global Positive01
    Positive01= pd.DataFrame()
    Positive01=Positive.loc[Positive['defferencetaxe'] == 0]
    Positive01['result'] =4
    Positive01=Positive01.reset_index(drop=True)
 #Advance payment in the exact periode
    global Positive012
    Positive012= pd.DataFrame()
    Positive012=Positive.loc[Positive['defferencetaxe'] < 0]
    Positive012['result'] =5
    Positive012=Positive012.reset_index(drop=True)

    #CALCULATE THE defferenceTaxe WITH Negative VALUES
    global Negative
    Negative= pd.DataFrame()
    Negative=combination.loc[combination['periode'] < 0]
## Calculation of Penality depending on periode
## let suppose they charge penality 3%
    Negative['penelity'] =0.0
    Negative['totalpenelity'] = Negative['defferencetaxe'].astype(float) + Negative['penelity'].astype(float)
    Negative=Negative.reset_index(drop=True)
   
    #ALL ENTERPRISE WHICH  DECLARE WITH FRAUD
    global Negative10
    Negative10= pd.DataFrame()
    Negative10=Negative.loc[Negative['defferencetaxe'] > 0]
    Negative10['result'] =6
    Negative10=Negative10.reset_index(drop=True)
    #ALL ENTERPRISE WHICH DIDN'T DECLARE WITH FRAUD
    global Negative101
    Negative101= pd.DataFrame()
    Negative101=Negative.loc[Negative['defferencetaxe'] == 0]
    Negative101['result'] =7
    Negative101=Negative101.reset_index(drop=True)
    
    #Advance payment in the exact periode
    global Negative1012
    Negative1012= pd.DataFrame()
    Negative1012=Negative.loc[Negative['defferencetaxe'] < 0]
    Negative1012['result'] =8
    Negative1012=Negative1012.reset_index(drop=True)
    ####################  CONCATENATE ALL DATAFRAME IN ONE DATAFRAME (this dataframe is for details according to each periode)
    global combination_Concat_periode
    comb_Concat_periode = [Exact0,Exact01,Exact012,Positive0,Positive01,Positive012,Negative10,Negative101,Negative1012]
    combination_Concat_periode = pd.concat(comb_Concat_periode)
    combination_Concat_periode = combination_Concat_periode.reset_index(drop=True)
    #print(len(combination_Concat_periode))
    ################### CONCATENTE ALL DATAFRAME IN ONE DATAFRAME(GENERAL DATAFRME WITHOUT CARERING OF PERIDE)
    global combination_Concat
    comb_Concat = [Exact1,Positive,Negative]
    combination_Concat = pd.concat(comb_Concat)
    combination_Concat = combination_Concat.reset_index(drop=True)
    #print(len(combination_Concat))
    global Exact 
    Exact= pd.DataFrame()
    Exact=combination.loc[combination['defferencetaxe'] == 0]
    Exact=Exact.assign(result=Exact.reset_index().index + 1)
    Exact['result'] =0
    Exact=Exact.reset_index(drop=True)
    
    global Positive1
    Positive1= pd.DataFrame()
    Positive1=combination.loc[combination['defferencetaxe'] > 0]
    Positive1['result'] = 1
    Positive1=Positive1.reset_index(drop=True)
 
    global Negative1
    Negative1= pd.DataFrame()
    Negative1=combination.loc[combination['defferencetaxe'] < 0]
    Negative1['result'] =2
    Negative1=Negative1.reset_index(drop=True)
  
    global combination_Concat1
    comb_Concat1 = [Exact,Positive1,Negative1]
    combination_Concat1 = pd.concat(comb_Concat1)
    combination_Concat1 = combination_Concat1.reset_index(drop=True)
    
    print('#######################################################################')
   ##print(combination_Concat1.dtypes)
    global mydataOld
    global mydata 
    mydataOld=combination_Concat_periode.drop(['enterprisename', 'datatopay','datepayed'], axis=1)
    mydata=combination_Concat1.drop(['enterprisename', 'datatopay','datepayed','periode','defferencetaxe'], axis=1)
    print(mydata.dtypes)
    print(mydata)

    class_namesd = {0:'Not Fraud', 1:'Fraud',2:'OVer Declaration'}
    
    class_names = {0:'NotFraudExactPeriode', 1:'FraudExactPeriode',2:'OVerDeclarationExactPeriode',
               3:'fraudPositivePeriode', 4:'notfraudPositivePeriode',5:'OVerDeclarationPositivePeriode',
               6:'fraudPegativePeriode', 7:'notfraudNegativePeriode',8:'OVerDeclarationNegativePeriode'}
    global vv
    vv=pd.DataFrame
    vv=mydataOld.result.value_counts().rename(index = class_names)
    myvvList1=[]
    myvvList1 = vv.index.tolist() 
    myvvList2=[]
    myvvList2 = vv.tolist() 
    global ResultCombination  #########################################################################
    ResultCombination=pd.DataFrame()
    ResultCombination['description']=myvvList1
    ResultCombination['number']=myvvList2

    hh=pd.DataFrame
    hh=mydata.result.value_counts().rename(index = class_namesd)
    myhhList1=[]
    myhhList1 = hh.index.tolist()
    myhhList2=[]
    myhhList2 = hh.tolist()
    global ResultDetails  #######################################################
    ResultDetails=pd.DataFrame()
    ResultDetails['description']=myhhList1
    ResultDetails['number']=myhhList2
    print(ResultDetails)
#Training data
    X = mydata.drop('result', axis = 1).values
    Y = mydata['result'].values

## traing data with train_test_split foction
    X_train, X_validation, y_train, Y_validation = train_test_split(X, Y, test_size=0.20, random_state=1)
# Spot Check Algorithms
    models = []
    models.append(('LR', LogisticRegression(solver='liblinear', multi_class='ovr',max_iter=1100)))
    models.append(('LDA', LinearDiscriminantAnalysis()))
    models.append(('KNN', KNeighborsClassifier()))
    models.append(('DTC', DecisionTreeClassifier()))
    models.append(('XGB', XGBClassifier()))
    models.append(('RF', RandomForestClassifier()))
    models.append(('Gaus', GaussianNB()))
    models.append(('SVC', SVC()))
# evaluate each model in turn
    results = []
    names = []
#initialize some list
    list_names=[]
    list_mean=[]
    list_std=[]
    global model
    for name, mod in models:
        kfold = KFold(n_splits=10, random_state=1, shuffle=True)
        cv_results = cross_val_score(mod, X_train, y_train, cv=kfold, scoring='accuracy')
        results.append(cv_results)
        names.append(name)
        list_names.append(name)
        list_mean.append(cv_results.mean())
        list_std.append(cv_results.std())
    global CompareAlgo
    CompareAlgo=pd.DataFrame() #########################################
    CompareAlgo['namealgorithm']=list_names
    CompareAlgo['mean']=list_mean
    CompareAlgo['std']=list_std
    #WE COMPARE THE ALGORITH WITH MEAN VALUES AND GET ITS ALGORITHNAME
    val = CompareAlgo['mean'].idxmax()
    print(val)
    global df_classification_report
    df_classification_report=pd.DataFrame()
    
    if val ==0:
        print('LR')
    # Make predictions on validation dataset
        model = LogisticRegression()
        model.fit(X_train, y_train)
        predictions = model.predict(X_validation)
    # Evaluate predictions
        report =classification_report(Y_validation, predictions, output_dict=True)
        df_classification_report = pd.DataFrame(report).transpose()
        df_classification_report = df_classification_report.sort_values(by=['f1-score'], ascending=False)
    elif val ==1:
        print('LDA')
    # Make predictions on validation dataset
        model = LinearDiscriminantAnalysis()
        model.fit(X_train, y_train)
        predictions = model.predict(X_validation)
    # Evaluate predictions
        report =classification_report(Y_validation, predictions, output_dict=True)
        df_classification_report = pd.DataFrame(report).transpose()
        df_classification_report = df_classification_report.sort_values(by=['f1-score'], ascending=False)
        
    elif val ==2:
        print('KNN')
        # Make predictions on validation dataset
        model = KNeighborsClassifier()
        model.fit(X_train, y_train)
        predictions = model.predict(X_validation)
    # Evaluate predictions
        report =classification_report(Y_validation, predictions, output_dict=True)
        df_classification_report = pd.DataFrame(report).transpose()
        df_classification_report = df_classification_report.sort_values(by=['f1-score'], ascending=False)
    elif val == 3:
        print('DTC')
    # Make predictions on validation dataset
        model = DecisionTreeClassifier()
        model.fit(X_train, y_train)
        predictions = model.predict(X_validation)
    # Evaluate predictions
        report =classification_report(Y_validation, predictions, output_dict=True)
        df_classification_report = pd.DataFrame(report).transpose()
        df_classification_report = df_classification_report.sort_values(by=['f1-score'], ascending=False)
        print(confusion_matrix(Y_validation,predictions))
    elif val == 4:
        print('XGB')
    # Make predictions on validation dataset
        model = XGBClassifier()
        model.fit(X_train, y_train)
        predictions = model.predict(X_validation)
    # Evaluate predictions
        report =classification_report(Y_validation, predictions, output_dict=True)
        df_classification_report = pd.DataFrame(report).transpose()
        df_classification_report = df_classification_report.sort_values(by=['f1-score'], ascending=False)
                    
    elif val == 5:
        print('RF')
    # Make predictions on validation dataset
        model = RandomForestClassifier()
        model.fit(X_train, y_train)
        predictions = model.predict(X_validation)
    # Evaluate predictions
        report =classification_report(Y_validation, predictions, output_dict=True)
        df_classification_report = pd.DataFrame(report).transpose()
        df_classification_report = df_classification_report.sort_values(by=['f1-score'], ascending=False)
    elif val == 6:
        print('SVC')
    # Make predictions on validation dataset
        model = SVC()
        model.fit(X_train, y_train)
        predictions = model.predict(X_validation)
    # Evaluate predictions   
        report =classification_report(Y_validation, predictions, output_dict=True)
        df_classification_report = pd.DataFrame(report).transpose()
        df_classification_report = df_classification_report.sort_values(by=['f1-score'], ascending=False)
 
    elif val == 7:
        print('Gaus')
    # Make predictions on validation dataset
        model = GaussianNB()
        model.fit(X_train, y_train)
        predictions = model.predict(X_validation)
    # Evaluate predictions
        report =classification_report(Y_validation, predictions, output_dict=True)
        df_classification_report = pd.DataFrame(report).transpose()
        df_classification_report = df_classification_report.sort_values(by=['f1-score'], ascending=False)
    else:
      print('no value')
      
    df_classification_report.loc[:, "support"] = df_classification_report["support"].map('{:.2f}'.format)
    df_classification_report.loc[:, "f1-score"] = df_classification_report["f1-score"].map('{:.2f}'.format)
    df_classification_report.loc[:, "recall"] = df_classification_report["recall"].map('{:.2f}'.format)
    df_classification_report.loc[:, "precision"] = df_classification_report["precision"].map('{:.2f}'.format)
    myList = df_classification_report.index.tolist()
    global ReportClasification
    ReportClasification=pd.DataFrame()
    ReportClasification['precision']=df_classification_report['precision'].copy()
    ReportClasification['recall']=df_classification_report['recall'].copy()
    ReportClasification['f1score']=df_classification_report['f1-score'].copy()
    ReportClasification['support']=df_classification_report['support'].copy()
    ReportClasification['classes']=myList
    datalist =ReportClasification.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.route("/clasification")
def clasification():
    datalist =ReportClasification.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone
@app.route("/chiffreaffaire")
def chiffreaffaire():
    
    datalist =data.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone
@app.route("/declaration")
def declaration():
    datalist =dataD.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone
@app.route("/withNotFraudDefferenceTaxes")
def withNotFraudDefferenceTaxes():
    datalist =Exact.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.route("/withFraudeDefferenceTaxes")
def withFraudeDefferenceTaxes(): 
    datalist =Positive1.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.route("/advanceDeclarationDefferenceTaxes")
def advanceDeclarationDefferenceTaxes(): 
    datalist =Negative1.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone    
@app.route("/combinationConcatperiode")
def combinationConcatperiode(): 
   
    datalist =combination_Concat_periode.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.route("/combinationConcatDefferenceTaxe")
def combinationConcatDefferenceTaxe(): 
    datalist =combination_Concat1.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.route("/compareAlgorithm")
def compareAlgorithm(): 
    datalist =CompareAlgo.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.route("/resultDetails")
def resultDetails(): 
    datalist =ResultDetails.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.route("/resultCombination")
def resultCombination(): 
    datalist =ResultCombination.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.route("/withNotFraudPeriodeExact")
def withNotFraudPeriodeExact(): 
    datalist =Exact0.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone
@app.route("/withFraudePeriodeExact")
def withFraudePeriodeExact(): 

    datalist =Exact01.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone 

@app.route("/advanceDeclarationPeriodeExact")
def advanceDeclarationPeriodeExact(): 

    datalist =Exact012.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone 

@app.route("/withNotFraudPeriodePositive")
def withNotFraudPeriodePositive(): 
   
    datalist =Positive01.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone
@app.route("/withFraudePeriodePositive")
def withFraudePeriodePositive(): 

    datalist =Positive0.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone 

@app.route("/advanceDeclarationPeriodePositive")
def advanceDeclarationPeriodePositive(): 

    datalist =Positive012.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone 


@app.route("/withNotFraudPeriodeNegative")
def withNotFraudPeriodeNegative(): 
   
    datalist =Positive01.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone
@app.route("/withFraudePeriodeNegative")
def withFraudePeriodeNegative(): 

    datalist =Positive0.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone 

@app.route("/advanceDeclarationPeriodeNegative")
def advanceDeclarationPeriodeNegative(): 

    datalist =Positive012.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone 

@app.route("/periodeExact")
def periodeExact(): 
    #CALCULATE THE periode WITH O VALUES
    datalist =Exact1.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.route("/PeriodePositive")
def PeriodePositive(): 
   #CALCULATE THE periode WITH positive VALUES
    datalist =Positive.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.route("/PeriodeNegative")
def PeriodeNegative(): 
    datalist =Negative.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.errorhandler(404)
def showMessage(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone

if __name__ == "__main__":
    app.run(host='0.0.0.0', port = rest_port)