from mylibrary import*
from DeepLearningModels.ChiffreAffaires.chiffreAffaires import chiffreaffaire 

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
        combination['enterprisename']=chiffreaffaire.data1['enterprisename'].copy()
        combination['chifreaffaire']=chiffreaffaire.data1['chifreaffaire'].copy()
        combination['taxesuposetodeclare']=chiffreaffaire.data1['taxesuposetodeclare'].copy()
        combination['taxdeclared']=dataD['taxdeclared'].copy()
        combination['datatopay']=chiffreaffaire.data1['datatopay'].copy()
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