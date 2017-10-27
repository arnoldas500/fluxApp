# run from terminal with:                                                                            
# export FLASK_APP=flaskFlux.py                                                                          
# python3 -m flask run --host=0.0.0.0 -p 9093 --with-threads
import io
import pandas as pd
import datetime
import re
#!flask/bin/python
from flask import Flask, jsonify , request, make_response
from flask_cors import CORS, cross_origin
app = Flask(__name__)
outside_sites = ['http://appsvr.asrc.cestm.albany.edu']
cors = CORS(app, resources={r"/*": {'origins': outside_sites}})


#app = Flask(__name__)

def formatTime(params):
    dates = params['dates']
    datesF = datetime.datetime.strftime(dates, '%Y/%m/%dT')

def getCSV(params, dates):
    #timeMin = params['time_min']
    #timeMax = params['time_max']
    date = params['dates']
    datesStrp = dates.replace("/","")
    #20170909_FLUX_BURT_Flux_NYSMesonet.csv
    print('/flux/' + dates +'/' +datesStrp + '_FLUX_BURT_Flux_NYSMesonet.csv')
    df = pd.read_csv('/flux/' + dates + '/' + datesStrp + '_FLUX_BURT_Flux_NYSMesonet.csv')

#    print(df.head())
#    print(df['CO2'])
    a = "arnold"
    df2 = pd.DataFrame() #creating an empty dataframe
    df2['datetime'] = pd.to_datetime(df['datetime'])
    df2['justDate']= df2['datetime'].dt.date
    df2['justHour'] = df2['datetime'].dt.hour
    df2['CO2']= df.loc[:,'CO2']
    
    datesNew = params['dates']
    df2['days_from'] = df2['datetime'] - datesNew
    df2['intDay'] = df2.days_from.dt.days 
    print(df2['justDate'])
    print(df2['justHour'])
    print(df2['intDay'])
    print(df2.tail())
    #df.set_index(['datetime'],inplace=True)
    #dfJson = df.loc[:,'justDate','justHour','CO2'].to_json()
    dfJson = df2.to_json()
    return dfJson

def testCSV(params, dates):
    #timeMin = params['time_min'] 
    date = params['dates']
    datesStrp = dates.replace("/","")
    #20170909_FLUX_BURT_Flux_NYSMesonet.csv                                                                                                              
                            
    print('/flux/' + dates +'/' +datesStrp + '_FLUX_BURT_Flux_NYSMesonet.csv')
    df = pd.read_csv('/flux/' + dates + '/' + datesStrp + '_FLUX_BURT_Flux_NYSMesonet.csv')

#    print(df.head())                                                                                                                                    
                            
#    print(df['CO2'])                                                                                                                                    
                            
    a = "arnold"
    df2 = pd.DataFrame() #creating an empty dataframe                                                                                                    
                            
    df2['datetime'] = pd.to_datetime(df['datetime'])
    df2['justDate']= df2['datetime'].dt.date
    df2['justHour'] = df2['datetime'].dt.hour
    df2['CO2']= df.loc[:,'CO2']

    datesNew = params['dates']
    df2['days_from'] = df2['datetime'] - datesNew
    df2['intDay'] = df2.days_from.dt.days
    print(df2['justDate'])
    print(df2['justHour'])
    print(df2['intDay'])
    print(df2.tail())
    #df.set_index(['datetime'],inplace=True)                                                                                                             
                            #[ [0.0.-0.7] ] day hour co2
    #dfJson = df.loc[:,'justDate','justHour','CO2'].to_json()

    df2.drop('datetime', axis=1, inplace=True)
    df2.drop('intDay', axis=1, inplace=True)
    df2.drop('days_from', axis=1, inplace=True)
    #writing to csv file
    csvData = df2.to_csv(header=False, index=False)
    
    #dfJson = df2.to_json()
    return csvData

    

@app.route('/plot', methods=['GET'])
def plot():
    # organize the request params                                                                    
    params = {}
    dates = request.args.get('dates',type=str)
    datesF = dates.replace("/", "")
    print(datesF)
    params['dates'] = datetime.datetime.strptime(dates, '%Y/%m/%d')
    response = testCSV(params, dates)

    #time_min_str = request.args.get('time_min', type=str)
    #params['time_min'] = datetime.datetime.strptime(time_min_str, '%Y-%m-%dT%H:%M:00.000Z')
    #time_max_str = request.args.get('time_max', type=str)
    #params['time_max'] = datetime.datetime.strptime(time_max_str, '%Y-%m-%dT%H:%M:00.000Z')

    #params['barbs'] = True if 'barbs' in request.args.keys() else False
    #lidar_ids_str = request.args.get('lidar_id', type=str)
    #scan_ids_str = request.args.get('scan_id', type=str)
    #params['lidar_ids'] = list(map(int, lidar_ids_str.split(',')))
    #params['scan_ids'] = list(map(int, scan_ids_str.split(',')))
    # ax = getPlot(request.args)                                                                     
    # canvas = FigureCanvas(ax.get_figure())                                                         
    # fig = getPlot(params)                                                                          
    # # fig = getPlot(request.args)                                                                  
    # canvas = FigureCanvas(fig)                                                                     
    # # png_output = io.StringIO()                                                                   
    # png_output = BytesIO()                                                                         
    #sending the actual dic to python
    #response = getCSV(params)
    # img = getPlot(request.args)                                                                    
    # response = make_response(img.getvalue())                                                       
    #for matplotlib
    # response.headers['Content-Type'] = 'image/png'
    return response
