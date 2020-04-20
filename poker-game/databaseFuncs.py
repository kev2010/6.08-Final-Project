import requests
import sqlite3
import datetime

def create_player_database(db_name):
  conn = sqlite3.connect(db_name)
  c = conn.cursor()
  c.execute('''CREATE TABLE players_table (user, bal, bet,cards,position);''')
  conn.commit()
  conn.close()

def create_state_database(db_name):
  conn = sqlite3.connect(db_name)
  c = conn.cursor()
  c.execute('''CREATE TABLE states_table (deck,board,dealer,pot);''')
  conn.commit()
  conn.close() 

def update_player(db_name,user,bal,bet,cards,position):
  conn = sqlite3.connect(db_name)
  c = conn.cursor()
  c.execute('''INSERT into players_table VALUES (?,?,?,?,?);)''', (user,bal,bet,cards,position))
  conn.commit()
  conn.close()

def update_database(db_name,deck, board, dealer, pot):
  conn = sqlite3.connect(db_name)
  c = conn.cursor()
  c.execute('''INSERT into states_table VALUES (?,?,?,?);''', (deck, board, dealer, pot))
  conn.commit()
  conn.close()

def get_db_size(db_name,table_name):
  conn = sqlite3.connect(db_name)
  c = conn.cursor()
  count = 0
  things = c.execute('''SELECT * FROM ?;''',(table_name))).fetchall()
  for elt in things:
    count += 1
  conn.commit()
  conn.close()
  return count

def clear_table(db_name, table_name):
  conn = sqlite3.connect(db_name)
  c = conn.cursor()
  c.execute('''DELETE * FROM ?;''',(table_name))
  conn.commit()
  conn.close()

def get_player(db_name,table_name, user):
  conn = sqlite3.connect(db_name)
  c = conn.cursor()
  count = 0
  things = c.execute('''SELECT * FROM ? WHERE user = ?;''',(table_name,user))).fetchall()
  conn.commit()
  conn.close()
  return str(things)


