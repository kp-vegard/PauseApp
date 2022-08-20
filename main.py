from flask import Flask, render_template, request, redirect
import time
from datetime import date, datetime, timedelta
import pandas as pd
import os
import csv
import sys

root = sys.path[0]
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
    return render_template('out.html', names=data['Navn'].values)
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
    name = request.form['name'].title()
    place = request.form['place'].title()
    t = datetime.now()
    e = t + timedelta(minutes=30)
    start_time = t.strftime('%H:%M')
    pause_end = e.strftime('%H:%M')
    current_time = time.time()
    todays_date = date.today()
    month = datetime.now().month
    with open(f'{root}/active/onbreak.csv', 'a', encoding='UTF-8') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([name, place, start_time, current_time])

    for attempt in range(5):
        try:
            with open(f'{root}/data/{month}/log/{todays_date}.txt', 'a', encoding='UTF-8') as file:
                file.write(f'{name} ({place}) sjekket seg inn {start_time}\n')
        except FileNotFoundError:
            try: new_month()
            except: new_day()
        else: break
    return render_template('done.html', end_time=pause_end)

@app.route('/done_out', methods=['POST'])
def check_out_data():
    name = request.form['name']
    todays_date = date.today()
    end_time = datetime.now().strftime('%H:%M')
    month = datetime.now().month
    total_time = 0
    #Copy content from main file to to temp and removing the name stamping out
    with open(f'{root}/active/onbreak.csv', 'r', encoding='UTF-8') as csv_file:
        with open(f'{root}/active/temp.csv', 'w', encoding='UTF-8') as temp_file:
            writer = csv.writer(temp_file)
            for row in csv.reader(csv_file):
                if row:
                    if row[0] == name:
                        place = row[1]
                        tid_inn = row[2]
                        total_time = int(float(row[3]))
                        for attempt in range(5):
                            try:
                                with open(f'{root}/data/{month}/total/{todays_date}.csv', 'a', encoding='UTF-8') as file:
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
    with open(f'{root}/active/onbreak.csv', 'w', encoding='UTF-8') as csv_file:
        with open(f'{root}/active/temp.csv', 'r', encoding='UTF-8') as temp_file:
            writer = csv.writer(csv_file)
            for row in csv.reader(temp_file):
                writer.writerow(row)
    #Remove temp file
    os.remove(f'{root}/active/temp.csv')
    for attempt in range(5):
        try:
            with open(f'{root}/data/{month}/log/{todays_date}.txt', 'a', encoding='UTF-8') as file:
                file.write(f'{name} ({place}) sjekket seg ut {end_time}\n')
        except FileNotFoundError:
            try: new_month()
            except: new_day()
        else: break
    return render_template('done_out.html', pause_length=total_time)

def load_database():
    df = pd.read_csv(f'{root}/active/onbreak.csv', encoding='UTF-8')
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
            df = pd.read_csv(f'{root}/data/{month}/total/{date.today()}.csv', encoding='UTF-8')
            return df
        except FileNotFoundError:
            try: new_month()
            except: new_day()

def new_month():
    month = datetime.now().month
    os.makedirs(f'{root}/data/{month}/log')
    os.makedirs(f'{root}/data/{month}/total')
    new_day()

def new_day():
    month = datetime.now().month
    with open(f'{root}/data/{month}/total/{date.today()}.csv', 'w', encoding='UTF-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Navn','Sted','Tid inn', 'Tid ut','Tid på pause'])
        
if __name__ == '__main__':
    app.run(host='0.0.0.0')