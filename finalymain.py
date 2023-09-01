from mylibrary import *
rest_port = 8050
eureka_client.init(eureka_server="http://localhost:8761/eureka",
                   app_name="flaskapi-machine-learning-model-service",
                    instance_ip="192.168.0.15",
                   instance_port=rest_port)

app = Flask(__name__)

       
@app.route('/chiffreaffaire')
def chiffreaffaire():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, enterprisename, chifreaffaire, datatopay FROM chiffreaffaire")
        chiffreaffaireRows = cursor.fetchall()
        #print(chiffreaffaireRows)
        respone = jsonify(chiffreaffaireRows)
        global data1
        data = pd.DataFrame(chiffreaffaireRows)
        ## calculate the tax exact depending on the ChiffreAfaire
        data1=data
        data1['taxesuposetodeclare']=data1['chifreaffaire'].astype(float) *(0.18)
        data1.loc[:, "taxesuposetodeclare"] = data1["taxesuposetodeclare"].map('{:.2f}'.format)
        #convet data1 to foat
        data1['taxesuposetodeclare'] = data1['taxesuposetodeclare'].astype(float)
        data1.drop(['id'], axis=1,inplace=True)
        #data1.head(2)
        #print(data1.dtypes)
        respone.status_code = 200
        return respone
       # datalist = data.to_dict()
        #datalist = [{k:v} for k, v in datalist.items()]
        #return json.dumps(datalist)
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()  
    
@app.route('/declaration')
def declaration():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT m.id As declarationId,  m.taxdeclared, m.datepayed, c.id As chiffreAfaireId, c.enterprisename, c.chifreaffaire, c.datatopay FROM declaration m INNER JOIN chiffreaffaire c ON c.id = m.id")
        chiffreaffaireRows = cursor.fetchall()
        respone = jsonify(chiffreaffaireRows)
        global data
        dataD = pd.DataFrame(chiffreaffaireRows)
        #print(dataD)
        global combination
        combination= pd.DataFrame()
        combination['enterprisename']=data1['enterprisename'].copy()
        combination['chifreaffaire']=data1['chifreaffaire'].copy()
        combination['taxesuposetodeclare']=data1['taxesuposetodeclare'].copy()
        combination['taxdeclared']=dataD['taxdeclared'].copy()
        combination['datatopay']=data1['datatopay'].copy()
        combination['datepayed']=dataD['datepayed'].copy()
        combination.loc[:,"chifreaffaire"] = combination["chifreaffaire"].map('{:.2f}'.format)
        # Used to convert the difference in terms of months
        combination['periode'] = ((combination.datatopay - combination.datepayed)/np.timedelta64(1, 'M'))
        combination['periode'] = combination['periode'].astype(int)
        global combinationOne
        combinationOne= pd.DataFrame()
        combinationOne=combination
        combinationOne['datepayed'] = combinationOne['datepayed'].dt.strftime('%Y-%m-%d')
        combinationOne['datatopay'] = combinationOne['datatopay'].dt.strftime('%Y-%m-%d')

        respone.status_code = 200
        return respone
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()  

@app.route("/declarationPeriode")
def declarationPeriode():
   
    # print(combinationOne) 
    #datalist = combinationOne.to_dict()
    #datalist = [{k:v} for k, v in datalist.items()]
    #datalist = combinationOne.values.tolist()
    datalist =combinationOne.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.route("/defferencetaxeDeclarationPeriode")
def defferencetaxeDeclarationPeriode(): 
    global combinationTwo
    combinationTwo= pd.DataFrame()
    combinationTwo=combinationOne
    combinationTwo['defferencetaxe'] = combinationTwo['taxesuposetodeclare'] - combinationTwo['taxdeclared'] 
    datalist =combinationTwo.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.route("/periodeExact")
def periodeExact(): 
    #CALCULATE THE periode WITH O VALUES
    global Exact1
    Exact1= pd.DataFrame()
    Exact1=combinationOne.loc[combination['periode'] == 0]
    ## Calculation of Penality depending on periode
    ## let suppose they charge penality 3%
    Exact1['penelity'] = 0.0
    Exact1['totalpenelity'] = Exact1['defferencetaxe'].astype(float) + Exact1['penelity'].astype(float)
    Exact1=Exact1.reset_index(drop=True)
    datalist =Exact1.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
     #ALL ENTERPRISE WHICH DIDN'T DECLARE WITH FRAUD
    global Exact0
    Exact0= pd.DataFrame()
    Exact0=Exact1.loc[Exact1['defferencetaxe'] == 0.0]
    Exact0['result'] =0
    Exact0=Exact0.reset_index(drop=True)
     ##ALL ENTERPRISE WHICH DECLARE WITH FRAUD
    global Exact01
    Exact01= pd.DataFrame()
    Exact01=Exact1.loc[Exact1['defferencetaxe'] >0]
    Exact01['result'] =1
    Exact01=Exact01.reset_index(drop=True)
    #Advance payment in the exact periode 
    global Exact012
    Exact012= pd.DataFrame()
    Exact012=Exact1.loc[Exact1['defferencetaxe'] <0]
    Exact012['result'] =2
    Exact012=Exact012.reset_index(drop=True)
   # print(Exact012)
    return respone

@app.route("/PeriodePositive")
def PeriodePositive(): 
   #CALCULATE THE periode WITH positive VALUES
    global Positive
    Positive= pd.DataFrame()
    Positive=combinationOne.loc[combination['periode'] > 0]
## Calculation of Penality depending on periode
## let suppose they charge penality 3%
    Positive['penelity'] = Positive['taxesuposetodeclare'] * 0.03 * Positive['periode']
    Positive['totalpenelity'] = Positive['defferencetaxe'].astype(float) + Positive['penelity'].astype(float)
    Positive=Positive.reset_index(drop=True)
    datalist =Positive.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    
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
    return respone

@app.route("/PeriodeNegative")
def PeriodeNegative(): 
    #CALCULATE THE defferenceTaxe WITH Negative VALUES
    global Negative
    Negative= pd.DataFrame()
    Negative=combination.loc[combination['periode'] < 0]
## Calculation of Penality depending on periode
## let suppose they charge penality 3%
    Negative['penelity'] =0.0
    Negative['totalpenelity'] = Negative['defferencetaxe'].astype(float) + Negative['penelity'].astype(float)
    Negative=Negative.reset_index(drop=True)
    datalist =Negative.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
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
    respone = json.loads(toJSON)
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
    return respone

@app.route("/withNotFraudDefferenceTaxes")
def withNotFraudDefferenceTaxes():
    global Exact 
    Exact= pd.DataFrame()
    Exact=combination_Concat.loc[combination_Concat['defferencetaxe'] == 0]
    Exact=Exact.assign(result=Exact.reset_index().index + 1)
    Exact['result'] =0
    Exact=Exact.reset_index(drop=True)
    datalist =Exact.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.route("/withFraudeDefferenceTaxes")
def withFraudeDefferenceTaxes(): 
    global Positive1
    Positive1= pd.DataFrame()
    Positive1=combination_Concat.loc[combination_Concat['defferencetaxe'] > 0]
    Positive1['result'] = 1
    Positive1=Positive1.reset_index(drop=True)
    datalist =Positive1.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    return respone

@app.route("/advanceDeclarationDefferenceTaxes")
def advanceDeclarationDefferenceTaxes(): 
    global Negative1
    Negative1= pd.DataFrame()
    Negative1=combination_Concat.loc[combination_Concat['defferencetaxe'] < 0]
    Negative1['result'] =2
    Negative1=Negative1.reset_index(drop=True)
    datalist =Negative1.T.to_dict().values()
    toJSON = json.dumps(list(datalist))
    respone = json.loads(toJSON)
    global combination_Concat1
    comb_Concat1 = [Exact,Positive1,Negative1]
    combination_Concat1 = pd.concat(comb_Concat1)
    combination_Concat1 = combination_Concat1.reset_index(drop=True)
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