from mylibrary import *


@app.route('/chiffreaffaire')
def chiffreaffaire():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT id, enterprisename, chifreaffaire, datatopay FROM chiffreaffaire")
        chiffreaffaireRows = cursor.fetchall()
        #print(chiffreaffaireRows)
        respone = jsonify(chiffreaffaireRows)
        data = pd.DataFrame(chiffreaffaireRows)
        ## calculate the tax exact depending on the ChiffreAfaire
        global data1
        data1 = pd.DataFrame()
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
