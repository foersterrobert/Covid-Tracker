import requests
import bs4
import tkinter as tk
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from datetime import datetime
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib import style
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

style.use("fast")

class App:
    def __init__(self, root, url='https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Fallzahlen.html'):
        self.root = root
        self.root.title('Covid-Tracker')
        self.root.geometry('1070x800')
        self.root.configure(background='white')
        self.root.resizable(False, False)
        self.url = url
        self.html_data = requests.get(self.url)
        self.data = self.get_covid_data()
        self.bundeslandL = {
            'Baden-Württemberg': [(8.55, 48.3), self.data[0]],
            'Bayern': [(12.204954, 48.520008), self.data[1]],
            'Berlin': [(13.404954, 52.520008), self.data[2]],
            'Brandenburg': [(13.704954, 51.820008), self.data[3]],
            'Bremen': [(8.634954, 53.190008), self.data[4]],
            'Hamburg': [(9.993682, 53.551086), self.data[5]],
            'Hessen': [(9.1, 50.5), self.data[6]],
            'Mecklenburg-Vorpommern': [(13.004954, 53.820008), self.data[7]],
            'Niedersachsen': [(10.04954, 52.020008), self.data[8]],
            'Nordrhein-Westfalen': [(7.404954, 51.220008), self.data[9]],
            'Rheinland-Pfalz': [(7.304954, 49.920008), self.data[10]],
            'Saarland': [(7.004954, 49.320008), self.data[11]],
            'Sachsen': [(13.804954, 50.820008), self.data[12]],
            'Sachsen-Anhalt': [(11.944954, 51.920008), self.data[13]],
            'Schleswig-Holstein': [(9.404954, 54.520008), self.data[14]],
            'Thüringen': [(10.59, 50.8), self.data[15]],
            # 'Gesamt': [(0, 0), self.data[16]],
        }

        self.gesamt = self.data[16]

        self.incidenceText = '\n'.join([f'{i}: {j[1][1]}' for (i, j) in self.bundeslandL.items()]) + '\n\nGesamt:' + self.gesamt[1]
        self.casesText = '\n'.join([f'{i}: {j[1][0]}' for (i, j) in self.bundeslandL.items()]) + '\n\nGesamt:' + self.gesamt[0]
        
        self.today = datetime.now()

        self.lF = tk.LabelFrame(root, bd=0, bg='white', height=750)
        self.lF.grid(row=0, column=0, sticky='N')

        self.rF = tk.LabelFrame(root, bd=0, bg='white')
        self.rF.grid(row=0, column=1)

        self.label = tk.Label(self.lF, bg='white', justify='left', font=('Courier', 16), text=self.incidenceText)
        self.label.grid(row=0, column=0, sticky='N', pady=(50, 5), padx=10)

        self.bF = tk.LabelFrame(self.lF, bd=0, bg='white')
        self.bF.grid(row=1, column=0, sticky='W', pady=(190, 0), padx=10)

        self.Cbtn = tk.Button(self.bF, text='cases', font=18, command=self.cases, bg='white')
        self.Cbtn.grid(row=0, column=1, padx=3)

        self.Ibtn = tk.Button(self.bF, text='incidence', font=18, command=self.incidence, bg='#dce6f5')
        self.Ibtn.grid(row=0, column=0, padx=3)

        self.info = tk.Label(self.lF, bg='white', justify='left', font=('Courier', 16), text=f'Source: rki.de\nDate: {self.today.strftime("%d.%m.")}')
        self.info.grid(row=2, column=0, sticky='W', pady=(20, 20), padx=10)

        self.fig = Figure(figsize=(7,8))
        self.fig.subplots_adjust(left=0.05, bottom=0.03, right=.98, top=0.96)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.rF)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0)
        self.mapPlot(s=1)

    def get_covid_data(self):
        data = []
        bs = bs4.BeautifulSoup(self.html_data.text, 'html.parser')
        rows = bs.find('tbody', class_=None).findAll('tr')

        for row in rows:
            cells = row.findAll('td')
            cases = cells[3].get_text()
            inszidenz = cells[4].get_text()
            data.append([cases, inszidenz])

        return data

    def cases(self):
        self.Ibtn['bg'] = 'white'
        self.Cbtn['bg'] = '#dce6f5'
        self.label['text'] = self.casesText
        self.mapPlot(s=0)

    def incidence(self):
        self.Cbtn['bg'] = 'white'
        self.Ibtn['bg'] = '#dce6f5'
        self.label['text'] = self.incidenceText
        self.mapPlot(s=1)


    def mapPlot(self, s):
        self.ax.clear()

        plz_shape_df = gpd.read_file('map/plz-gebiete.shp', dtype={'plz': str})

        plz_region_df = pd.read_csv(
            'map/zuordnung_plz_ort.csv', 
            sep=',', 
            dtype={'plz': str}
        )

        plz_region_df.drop('osm_id', axis=1, inplace=True)

        germany_df = pd.merge(
            left=plz_shape_df, 
            right=plz_region_df, 
            on='plz',
            how='inner'
        )

        germany_df.drop(['note'], axis=1, inplace=True)

        germany_df.plot(
            ax=self.ax, 
            column='bundesland', 
            categorical=True, 
            cmap='tab20',
            alpha=0.9
        )

        for b in self.bundeslandL.keys():
            self.ax.text(
                x=self.bundeslandL[b][0][0], 
                # Add small shift to avoid overlap with point.
                y=self.bundeslandL[b][0][1] + 0.08, 
                s=f'{b} \n {self.bundeslandL[b][1][s]}', 
                fontsize=12,
                ha='center', 
            )
            # Plot city location centroid.
            self.ax.plot(
                self.bundeslandL[b][0][0], 
                self.bundeslandL[b][0][1], 
                marker='o',
                c='black', 
                alpha=0.5
            )

        self.ax.set(
            title=f'Covid-Tracker | Gesamt: {self.data[16][s]}', 
            aspect=1.3, 
        )

        self.canvas.draw()
        