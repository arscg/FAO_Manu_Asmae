#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 12:18:09 2023

@author: arscg
"""

import glob, sys, sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from colorama import Fore, Back, Style
import seaborn as sns
import matplotlib.pyplot as plt


conn = sqlite3.connect('bdd.sqlite.db')


def create_view(connect):
    SQL =     ''' CREATE VIEW vue_pourcentage_pauverte_2 AS
select  "Code groupe de pays partenaires" as Code_Group_Pays,
        "Groupe de pays partenaires" as Group_Pays, 
        "Code Pays" as Code_Pays,
        Pays, 
        Année, 
        val_pauvreté, 
        Symbole, 
        val_population, 
        percentage_gjhjhkjhkjhkhk
from FAOSTAT_data INNER JOIN  ( -- vue de la jointure entre la table population et sous alimentation et calcul de la pauvreté
        select FAOSTAT_2013_population."Code Pays", 
            FAOSTAT_2013_population.Pays AS Pays, 
              FAOSTAT_2013_sous_alimentation.Année, 
              FAOSTAT_2013_sous_alimentation.Valeur as val_pauvreté,
            FAOSTAT_2013_sous_alimentation.Symbole,
            FAOSTAT_2013_population.Valeur as val_population,
            ((FAOSTAT_2013_sous_alimentation.Valeur/3)/(FAOSTAT_2013_population.Valeur/1000))*100 as percentage
        from FAOSTAT_2013_sous_alimentation INNER JOIN FAOSTAT_2013_population on FAOSTAT_2013_population."Code Pays" =FAOSTAT_2013_sous_alimentation."Code Pays"
    ) on "Code Pays" = FAOSTAT_data."Code pays partenaire" -- jointure pour integration du groupe de pays
where (FAOSTAT_data."Code groupe de pays partenaires" % 100)==0 and FAOSTAT_data."Code groupe de pays partenaires" != 5000
ORDER BY percentage DESC;'''
    
    cursor = connect.cursor()
    print("Connected to the database")
    cursor.execute(SQL)
    connect.commit()
    print("Database created")
    cursor.close()
    
    return 


create_view(conn)


def population():
    SQL = 	''' select "Code Pays", Pays, Valeur 
from FAOSTAT_2013_population 
order by valeur desc;'''
    return pd.read_sql_query(SQL, con=conn)


print(population())

def mal_nutrition():
    SQL = 	''' select "Code zone", "zone", Année, Valeur, Symbole from FAOSTAT_2013_sous_alimentation;'''
    return pd.read_sql_query(SQL, con=conn)
print(mal_nutrition())

# def percentage():

#     SQL = 	''' select FAOSTAT_2013_population."Code Pays", FAOSTAT_2013_population.Pays AS Pays, 
# FAOSTAT_2013_sous_alimentation.Année, FAOSTAT_2013_sous_alimentation.Valeur as val_pauvreté,
# FAOSTAT_2013_sous_alimentation.Symbole,
# FAOSTAT_2013_population.Valeur as val_population,
# (FAOSTAT_2013_sous_alimentation.Valeur/(FAOSTAT_2013_population.Valeur/1000))*100 as percentage
# from FAOSTAT_2013_sous_alimentation INNER JOIN FAOSTAT_2013_population 
# on FAOSTAT_2013_population."Code Pays" =FAOSTAT_2013_sous_alimentation."Code Pays"
# ORDER BY percentage DESC 

#     ;'''
    
#     SQL = 	''' select 	"Code groupe de pays partenaires" as Code_Group_Pays,
# 		"Groupe de pays partenaires" as Group_Pays, 
# 		"Code Pays" as Code_Pays,
# 		Pays, 
# 		Année, 
# 		val_pauvreté, 
# 		Symbole, 
# 		val_population, 
# 		percentage
# from FAOSTAT_data INNER JOIN  ( -- vue de la jointure entre la table population et sous alimentation et calcul de la pauvreté
# 		select FAOSTAT_2013_population."Code Pays", 
# 			FAOSTAT_2013_population.Pays AS Pays, 
# 		  	FAOSTAT_2013_sous_alimentation.Année, 
# 		  	FAOSTAT_2013_sous_alimentation.Valeur as val_pauvreté,
# 			FAOSTAT_2013_sous_alimentation.Symbole,
# 			FAOSTAT_2013_population.Valeur as val_population,
# 			(FAOSTAT_2013_sous_alimentation.Valeur/(FAOSTAT_2013_population.Valeur/1000))*100 as percentage
# 		from FAOSTAT_2013_sous_alimentation INNER JOIN FAOSTAT_2013_population on FAOSTAT_2013_population."Code Pays" =FAOSTAT_2013_sous_alimentation."Code Pays"
# 	) on "Code Pays" = FAOSTAT_data."Code pays partenaire" -- jointure pour integration du groupe de pays
# where (FAOSTAT_data."Code groupe de pays partenaires" % 100)==0 and FAOSTAT_data."Code groupe de pays partenaires" != 5000
# ORDER BY percentage DESC 
#     ;'''

def percentage():
    SQL = ''' select * from vue_pourcentage_pauverte ;'''
    return pd.read_sql_query(SQL, con=conn)

def percentage_grou_pays():
    
    SQL = ''' 
    select Group_Pays as Regions, count(Group_Pays) as nb_pays, avg(percentage) as "Average percentage of poor nutrition", percentage 
    from vue_pourcentage_pauverte 
    group by Group_Pays;
    '''
    return pd.read_sql_query(SQL, con=conn)

def list_group_pays():
    SQL='''
    select DISTINCT Group_Pays from vue_pourcentage_pauverte
    '''
    return pd.read_sql_query(SQL, con=conn)

#chargement dataframe à partir de la requette %
df=percentage()
df_grp_pays=list_group_pays()

labels=list_group_pays()["Group_Pays"]
colors=['orange', 'blue','red', 'green','m', 'gray']

pal=[]
for i in df.index:
    if df["Group_Pays"][i]=="Afrique":
        pal.append("red")
    elif df["Group_Pays"][i]=="Europe":
        pal.append("blue")
    elif df["Group_Pays"][i]=="Amériques":
        pal.append("green")
    elif df["Group_Pays"][i]=="Océanie":
        pal.append("m")
    elif df["Group_Pays"][i]=="Asie":
        pal.append("orange")
    else:
        pal.append("gray")

#paramétrage de la figure
fig,ax= plt.subplots(figsize=(70,50), dpi=50)
ax.set_xlabel('pays')
ax.set_ylabel('percentage')
df.dropna(how='any', inplace=True)
#tracé du bar graph de pourcentage
sns.barplot(x = 'percentage', y =  'Pays', data = df, palette = pal)
plt.legend( labels=labels, labelcolor  = colors, bbox_to_anchor=(0.8,0.5), loc=2,
           fontsize=50, facecolor="gray",
           title_fontsize=50, title="Group zones", markerscale=5)

plt.title("\n% de pauvreté par pays\nen fonction de leur zone\ngéographique\n", fontsize=50 )


palette= "blend:#7AB,#EDA"
fig,ax= plt.subplots(figsize=(20,12), dpi=100)
ax.set_xlabel('pays', fontsize = 30.0)
ax.set_ylabel('percentage', fontsize = 40.0)
# sns.barplot(x = 'percentage', y =  'Pays', data = df.head(20), palette = palette)
sns.barplot(x = 'percentage', y =  'Pays', data = df.head(20), palette = pal)
plt.tick_params(axis='both', which='major', labelsize=25)

df=percentage_grou_pays()

# pal=[]
# for var in df:
#     pal.append("gray")
    
# pal[1]="red"
    
#paramétrage de la figure
fig,ax= plt.subplots(figsize=(12,8), dpi=100)
ax.set_xlabel('Average percentage of poor nutrition')
ax.set_ylabel('Regions')

colors=['red', 'm','orange', 'blue','green', 'gray']

#tracé du bar graph de pourcentage
# sns.barplot(x = 'Regions'  , y =  'Average percentage of poor nutrition', data = df, palette = "pastel")
sns.barplot(x = 'Regions'  , y =  "percentage", data = df, palette = colors)
plt.tick_params(axis='both', which='major', labelsize=25)

