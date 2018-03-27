#-*- coding: utf-8 -*-
import sqlite3
from xmpp import Client as jbr
from xmpp import protocol as jbrp
from xmpp import Presence
import config as conf
from pathlib import Path
import validators
import re

help_str="ping\nget_list\nadd"

class Bot:
	def execute_sql(self,what, *args):
		self.sql_cursor.execute(what % args)
		self.sql.commit()
	def install_sql(self):
		self.execute_sql("create table servers(id INTEGER PRIMARY KEY AUTOINCREMENT , serv_addr varchar)")
	def message_handler(self, conn, nod):
		print ("Message handler")
		username = nod.getFrom()
		comm = nod.getBody()
		comm_args=comm.split(" ",5)
		if comm == "ping":
			print("Ping-Pong")
			self.send_msg(username, "Pong")
		elif comm == "get_list":
			print("I get get_list")
			self.send_msg(username, self.str_list) 
		elif comm.find("add") != -1:
			if(len(comm_args) < 2):
				self.send_msg(username, "You will write server")
			else:
				print("adding server")
				try:
					self.add_to_list(comm_args[1])
					self.send_msg(username, "Added")
				except Exception as exp:
					self.send_msg(username, str(exp) )
				print self.list_servs
		elif comm == "help":
			self.send_msg(username,help_str)
		else:
			self.send_msg(username, "unregistered msg\n"+help_str)
			print "Uregistered command of "+str(username)+" -> " + comm

	def init_sql(self, sql_name='servers.sql'):
		self.sql = sqlite3.connect(sql_name)
		self.sql_cursor = self.sql.cursor()
		f = Path("./installed.c")
		if not f.is_file():
			self.install_sql()
			f = open("installed.c", "w")
			f.write("0")
			f.close()
		

	def add_to_list(self,serv_name):
		#TODO: Check if it XMPP and in I2P
		if not re.match( r"^([a-z0-9]+(-[a-z0-9]+)*\.)+i2p$", serv_name ):
			print re.match( r"^([a-z0-9]+(-[a-z0-9]+)*\.)+i2p$", serv_name )
			raise ValueError( serv_name+ " It is not domain of I2P")

		for el in self.list_servs:
			if el[0] == serv_name:
				raise ValueError("Already added")
			print el[0] + "!="+serv_name
		self.execute_sql("INSERT INTO servers(serv_addr) values('%s')", serv_name)
		self.get_list()
		return True

	def init_list(self):
		self.list_servs = self.sql_cursor.execute("SELECT serv_addr FROM servers ").fetchall()
		self.str_list = ""
		for serv in self.list_servs:
			self.str_list = self.str_list + serv[0] + "\n"

	def get_list(self):
		self.sql_cursor.execute("SELECT serv_addr FROM servers WHERE   id = (SELECT MAX(id) FROM servers)")
		self.list_servs =  self.list_servs + self.sql_cursor.fetchall() 
		self.str_list = self.str_list + self.list_servs[len(self.list_servs)-1][0] + "\n"		

	def connect_to_jbr(self, xid, password):
		xid=jbrp.JID( xid )
		
	def __init__(self, xid=conf.xid, password=conf.password):
		print ("Initing bot")
		
		self.xid=jbrp.JID( xid )
		self.password=password
		self.domain=self.xid.getDomain()
		self.conn = jbr(self.domain, debug = [])

		if not self.conn.connect():
			raise ValueError("Can't connect to server "+self.server)
		self.auth()
		
		print ("Register handler")	
		self.conn.RegisterHandler('message', self.message_handler)
		self.conn.RegisterHandler('presence', self.presence)
		self.init_sql()
		self.init_list()

	def auth(self):
		self.conn.auth(self.xid.getNode(), self.password)
		print("auth.")
	def stop(self):
		try:
			self.conn.disconnect()
			self.sql.close()
		except Exception:
			pass
	def send_msg(self, to, msg):
		print("Send msg")
		self.conn.send( jbrp.Message(to, msg) )
	def Receive(self):
		print ("send init presence")
		self.conn.sendInitPresence(requestRoster=1)
		roster = self.conn.getRoster()
		print ("Cycle")
		while True:
			self.conn.Process(10)
	def presence(self, conn, nod):
   		 if nod.getType() == 'subscribe':
       			conn.send(Presence(to=event.getFrom(), typ='subscribed'))
