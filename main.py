from tkinter import Place
from urllib import request
from flask import Flask, render_template, request, redirect
import time
from datetime import date, datetime 
import pandas as pd
import os
import csv

app = Flask(__name__)

@app.route('/')
def home():
    return redirect('valg')

@app.route('/valg')
def options():
    return render_template('options.html')

@app.route('/inn')
def inn():
    return render_template('inn.html')

@app.route('/ut')
def out():
    data = load_database()
    return render_template('out.html', data=zip(data['Navn'].values, data['Sted'].values))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/admin')
def admin():
    data = load_database()
    data2 = load_breaks()
    del data['time']
    return render_template('admin.html',  
                            tables=[data.to_html(classes='data')], 
                            titles=data.columns.values,
                            tables2=[data2.to_html(classes='data2')],
                            titles2=data2.columns.values
                            )

@app.route('/done', methods=['POST'])
def check_in_data():
    name = request.form['name']
    place = request.form['place']
    start_time = datetime.now().strftime('%H:%M')
    current_time = time.time()
    todays_date = date.today()
    month = datetime.now().month

    with open(f'active/onbreak.csv', 'a') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([name, place, start_time, current_time])

    for attempt in range(5):
        try:
            with open(f'data/{month}/log/{todays_date}.txt', 'a') as file:
                file.write(f'{name} ({place}) sjekket seg inn {start_time}\n')
        except FileNotFoundError:
            try: new_month()
            except: new_day()
        else: break

    return render_template('done.html')

@app.route('/done_out', methods=['POST'])
def check_out_data():
    name, place = request.form['name'].split()
    todays_date = date.today()
    end_time = datetime.now().strftime('%H:%M')
    month = datetime.now().month
    #Copy content from main file to to temp and removing the name stamping out
    with open('active/onbreak.csv', 'r') as csv_file:
        with open('active/temp.csv', 'w') as temp_file:
            writer = csv.writer(temp_file)
            for row in csv.reader(csv_file):
                if row[0] == name and row[1] == place:
                    tid_inn = row[2]
                    total_time = int(float(row[3])) 

                    for attempt in range(5):
                        try:
                            with open(f'data/{month}/total/{todays_date}.csv', 'a') as file:
                                time_now = int(time.time())
                                total_time = time_now - total_time
                                total_time = int(total_time//60)
                                writer2 = csv.writer(file)
                                writer2.writerow([name, place, tid_inn, end_time, total_time])
                            
                        except FileNotFoundError:
                            try: new_month()
                            except: new_day()
                        else: break
                else:
                    writer.writerow(row)


    #Copy content from temp file to main file
    with open('active/onbreak.csv', 'w') as csv_file:
        with open('active/temp.csv', 'r') as temp_file:
            writer = csv.writer(csv_file)   
            for row in csv.reader(temp_file):
                writer.writerow(row)
    #Remove temp file
    os.remove('active/temp.csv')

    for attempt in range(5):
        try: 
            with open(f'data/{month}/log/{todays_date}.txt', 'a') as file:
                file.write(f'{name} ({place}) sjekket seg ut {end_time}\n')
        except FileNotFoundError:
            try: new_month()
            except: new_day()
        else: break


    return render_template('done_out.html')


def load_database():
    df = pd.read_csv('active/onbreak.csv')
    current_time = time.time()
    new = []
    for i in df['time'].values:
        t = current_time - i
        t = int(t//60)
        new.append(t)
    df['Tid'] = new
    return df

def load_breaks():
    month = datetime.now().month
    for attemps in range(5):
        try:
            df = pd.read_csv(f'data/{month}/total/{date.today()}.csv')
            return df
        except FileNotFoundError:
            try: new_month()
            except: new_day()
    

def new_month():
    month = datetime.now().month
    os.makedirs(f'data/{month}/log')
    os.makedirs(f'data/{month}/total')
    new_day()

def new_day():
    month = datetime.now().month
    with open(f'data/{month}/total/{date.today()}.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['Navn','Sted','Tid inn', 'Tid ut','Tid på pause'])

if __name__ == '__main__':
    app.run(host='0.0.0.0')