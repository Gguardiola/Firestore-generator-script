#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from optparse import OptionParser
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from random import randint
from faker import Faker
fake = Faker('es_ES')


num_comptes = 90
num_adreces = 50
num_titulars = 100
#restamos el num_adreces ya que al asegurarnos 1 titular por cada adreça iterarmos el resto de titulars aleatorios
titulars_restantes = num_titulars - num_adreces
num_contractes = 400
# restamos el num_comptes ya que al asegurarnos 1 contracte por cada compte iteraremos el resto de contractes de forma aleatoria
num_contractes = num_contractes - num_comptes
atypes = ('C', 'L', 'S')
vowels = ('a', 'e', 'i', 'o', 'u')
somecons = ('b', 'd', 'f', 'k', 'l', 'm', 'p', 'r', 's')
#total_titulars se rellenará con la generación de los 1000 titulars necesarios para comptes y adreces
total_titulars = []
#used_titulars guarda los ya usados en adreces
used_titulars = []

def r(lim):
  "0 <= random int < lim"
  return randint(0, lim-1)
def generarTitulars():
  for i in range(num_titulars):
    owner_id = randint(10000000, 99999999)
    owner    = randname(2) + ' ' + randname(4)  
    total_titulars.append({"owner_id": owner_id, "owner": owner})

def borrador(db,target): 
    #borrar el contenido de una colección por document, ya que Firestore no deja eliminar de golpe
    for doc in db.collection(target).stream():
        doc.reference.delete()

def randname(syll):
  "random name with syll 2-letter syllables"
  v = len(vowels)
  c = len(somecons)
  res = str()
  for i in range(syll):
    res += somecons[r(c)] + vowels[r(v)]
  return res.capitalize()


def create_comptes(db,num_titulars,num_contractes):
  print("Creating comptes collection")
  db.collection("comptes")
  borrador(db,"comptes")

  for i in range(num_comptes):
    print(i+1, end = '\r')
    acc_id  = randint(100000000000, 999999999999)
    balance = randint(100, 99999)/100
    typ = atypes[r(3)]

    #aseguramos mínimo un contracte
    titulars = []
    titulars_pos = randint(0,num_titulars -1)
    while True:
      if not total_titulars[titulars_pos] in titulars:
        titulars.append(total_titulars[titulars_pos]) 
        break   
    
    #ahora introducimos de 3 a 5 contractes adicionales por compte
    contractes_compte = randint(3,5)
    for j in range(contractes_compte):
      if num_contractes > 0:
        titulars_pos = randint(0,num_titulars -1)
        if not total_titulars[titulars_pos] in titulars:
          titulars.append(total_titulars[titulars_pos])
          num_contractes = num_contractes -1

        else:
          j = j+1

    #introducimos el document en la collection comptes
    try:
      db.collection("comptes").document(str(acc_id)).set({
                                    "type": typ,
                                    "balance": balance,
                                    "titulars": titulars
      })      

    except Exception as e:
      print("ERROR: {}".format(e))


def create_adreces(db,num_titulars,titulars_restantes):
  print("Creating adreces collection")
  db.collection("adreces")
  borrador(db,"adreces")
  print("%d adreces will be inserted." % num_adreces)
  
  for i in range(num_adreces):
    print(i+1, end = '\r')
    address = fake.address()
    phone   = fake.phone_number()

    #aseguramos mínimo 1 titular por adreça
    titulars = []
    while True:
      titulars_pos = randint(0,num_titulars -1)    
      if titulars_pos not in used_titulars:
        titulars.append({"owner_id": total_titulars[titulars_pos]["owner_id"]}) 
        used_titulars.append(titulars_pos)
        break  
          
    #introducimos de 2 a 5 titulars adicionales por cada adreça
    titulars_adreces = randint(2,5)
    for i in range(titulars_adreces):
      if titulars_restantes > 0:
        titulars_pos = randint(0,num_titulars -1)
        if titulars_pos not in used_titulars:
          titulars.append({"owner_id": total_titulars[titulars_pos]["owner_id"]})
          titulars_restantes = titulars_restantes -1
          used_titulars.append(titulars_pos)
        else:
          i += 1

    #introducimos el document en la collection
    try:
      db.collection("adreces").document(address).set({
                                    "phone": phone,
                                    "titulars": titulars
      })

    except Exception as e:
      print("ERROR: {}".format(e))


# Programa principal
#cred = credentials.Certificate("dabd-gabriel-firebase-adminsdk-85uq1-9292df5b29.json")
#firebase_admin.initialize_app(cred)
firebase_admin.initialize_app()
db = firestore.client()

# def checkContractes(db):
#   cont = 0
#   all = db.collection("comptes").stream()
#   for doc in all:
#     for i in doc.to_dict()["titulars"]:
#       if "owner_id" in i:
#         cont = cont+1
#   print(cont)


generarTitulars()
create_adreces(db,num_titulars,titulars_restantes)
create_comptes(db,num_titulars,num_contractes)
#checkContractes(db)
