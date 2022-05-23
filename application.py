
from flask import Flask,render_template, request,Response
import pymysql
from pandas import DataFrame
from time import time
import numpy as np
import psycopg2
import pdfkit
import pyodbc



application = Flask(__name__, template_folder='templates')
application.config['SECRET_KEY'] = 'some_random_secret'



result = ""
csv_file = None
pdf_file = None
html_out = ""
last_query = ""




@application.route('/',methods=['GET','POST'])
def start():
    return render_template('my_index.html')


@application.route("/getPlotCSV")
def getPlotCSV():
    csv = '1,2,3\n4,5,6\n'
    return Response(
        csv_file,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=output.csv"})

@application.route("/getPdf")
def getPdf():
    if html_out!="":
        pdfkit.from_url('http://flastfinalproject-env.eba-x3qqhbgk.us-east-2.elasticbeanstalk.com/', pdf_file)
    return Response(
    pdf_file,
    mimetype="text/pdf",
    headers={"Content-disposition":
             "attachment; filename=output.pdf"}
    )



@application.route('/index',methods=['GET','POST'])
def index():

    global result,csv_file,html_out,last_query
    csv_file = None
    html_out = ""
    result=""
    if request.method == 'POST':
            try:
                query_con = request.form['query']
                last_query = query_con
                option = request.form['database']
                if option=="mysql":
                    db = pymysql.connect(host="instacart.ck12z0ni2znt.us-east-2.rds.amazonaws.com",
                                         user="admin",
                                         passwd="cs527group7",
                                         db="instacart")
                    cur = db.cursor()
                    tic = time()
                    r = cur.execute(query_con)
                    print("this is sqlr", r)
                    if cur.description is not None and r==0:
                        columns = cur.description
                        key_list = []
                        for i in range(len(columns)):
                            key_list.append(columns[i][0])
                        df=DataFrame(columns=key_list)
                        csv_file = df.to_csv()
                        html_out = df.to_html()
                        c=1
                    elif cur.description is None and r==0:
                        c=2
                    elif cur.description is None and r!=0:
                        c=3
                    elif cur.description is not None and r!=0:
                        columns = cur.description
                        key_list = []
                        data_row = cur.fetchall()
                        for i in range(len(columns)):
                            key_list.append(columns[i][0])
                        df=DataFrame(data_row)
                        if r==0:
                            df=DataFrame(columns=key_list)
                        else:
                            df.index = np.arange(1, len(df)+1)
                            df.columns=(key_list)
                        csv_file = df.to_csv()
                        html_out = df.to_html()
                        c=0

                    db.commit()
                    cur.close()
                    db.close()
                    toc = time()
                    if c==1:
                        return render_template('index.html', column_names=df.columns.values, row_data=[], exec_time =str(round(toc - tic, 7)), zip=zip, last_q = last_query)
                    if c==3:
                        return render_template('index.html', column_names=[], row_data=[], exec_time =str(round(toc - tic, 7)), zip=zip, last_q = last_query) + "Query Executed: " + str(r) + " rows affected"
                    if c==2:
                        return render_template('index.html', column_names=[], row_data=[], exec_time = str(round(toc - tic, 7)), zip=zip, last_q = last_query) + "Query Executed: "
                    if c==0:
                        return render_template('index.html', column_names=df.columns.values, row_data=list(df.values.tolist()), exec_time = str(round(toc - tic, 7)), zip=zip, last_q = last_query)

                elif option=="redshift":
                    db = psycopg2.connect(dbname= 'instacart',
                                            host='instacart-redshift.chpiebwu4pg9.us-east-2.redshift.amazonaws.com',
                                            port= '5439',
                                            user= 'cs527group7',
                                            password= 'Cs527group7')
                    cur = db.cursor()
                    tic = time()
                    r = cur.execute(query_con)
                    if cur.description is None:
                        c=2
                    elif cur.description is not None and r!=0:
                        print("chelho")
                        columns = cur.description
                        data_row = cur.fetchall()
                        print("SQL", data_row)
                        key_list = []
                        for i in range(len(columns)):
                            key_list.append(columns[i][0])
                        df=DataFrame(data_row)
                        print("This is redshift",df)
                        if data_row==[]:
                            df=DataFrame(columns=key_list)
                        else:
                            df.index = np.arange(1, len(df)+1)
                            df.columns=(key_list)
                        csv_file=df.to_csv()
                        c=0

                    db.commit()
                    cur.close()
                    db.close()
                    toc = time()

                    if c==2:
                        return render_template('index.html', column_names=[], row_data=[], exec_time = str(round(toc - tic, 7)), zip=zip, last_q = last_query) + "Query Executed Successfully"
                    if c==0:
                        return render_template('index.html', column_names=df.columns.values, row_data=list(df.values.tolist()), exec_time = str(round(toc - tic, 7)), zip=zip, last_q = last_query)

                elif option == "mongo":
                    server = '127.0.0.1'
                    port = 27017
                    database = 'instacart'
                    db = pyodbc.connect('DRIVER={Devart ODBC Driver for MongoDB};'
                                         'Server=' + server + ';Port=' + str(port) +
                                         ';Database=' + database)
                    cur = db.cursor()
                    tic = time()
                    r = cur.execute(query_con)
                    key_list=[]
                    if cur.description is not None and r == 0:
                        columns = cur.description
                        key_list = []
                        for i in range(len(columns)):
                            key_list.append(columns[i][0])
                        df = DataFrame(columns=key_list)
                        csv_file = df.to_csv()
                        html_out = df.to_html()
                        c = 1
                    elif cur.description is None and r == 0:
                        c = 2
                    elif cur.description is None and r != 0:
                        c = 3
                    elif cur.description is not None and r != 0:
                        columns = cur.description
                        key_list = []
                        data_row = cur.fetchall()
                        print(data_row[0])
                        a_list = [el[1:] for el in data_row]
                        print(a_list)
                        for i in range(1,len(columns)):
                            key_list.append(columns[i][0])
                        print("this is key_list", key_list)
                        df = DataFrame(a_list)

                        if r == 0:
                            df = DataFrame(columns=key_list)
                        else:
                            df.index = np.arange(1, len(df) + 1)
                            df.columns = (key_list)
                        csv_file = df.to_csv()
                        html_out = df.to_html()
                        c = 0

                    db.commit()
                    cur.close()
                    db.close()
                    toc = time()
                    print("after df", df)

                    print("df.columns.values",df.columns.values)
                    if c == 1:
                        return render_template('index.html', column_names=df.columns.values, row_data=[],
                                               exec_time=str(round(toc - tic, 7)), zip=zip, last_q=last_query)
                    if c == 3:
                        return render_template('index.html', column_names=[], row_data=[],
                                               exec_time=str(round(toc - tic, 7)), zip=zip,
                                               last_q=last_query) + "Query Executed: " + str(r) + " rows affected"
                    if c == 2:
                        return render_template('index.html', column_names=[], row_data=[],
                                               exec_time=str(round(toc - tic, 7)), zip=zip,
                                               last_q=last_query) + "Query Executed: "
                    if c == 0:
                        return render_template('index.html', column_names=df.columns.values,
                                               row_data=list(df.values.tolist()), exec_time=str(round(toc - tic, 7)),
                                               zip=zip, last_q=last_query)



            except Exception as e:
                result = '<h3>'+str(e)+'</h3>'
                return render_template('index.html', column_names=[], row_Data=list(), exec_time="", last_q = last_query) + result


    else:

        return render_template('index.html', column_names=[], row_data=list(), exec_time="", last_q="")




if __name__=='__main__':
    application.run(debug=True)