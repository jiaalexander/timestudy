#!/usr/bin/python3

# 
# db.py:
# Code for working with the MySQL database

import os,sys
if sys.version < '3':
    raise RuntimeError("Requires Python 3")


DEFAULT_MYSQL_DB   = 'timedb'
DEFAULT_MYSQL_PORT = 3306
DEFAULT_MAX_EXECUTES = 0     # reconnect after 

# Common DB and Config Routines
# Find a MySQL driver..

USE_MYSQLDB=True
USE_PYMYSQL=False               # ran into error when rowid went larger than 65536

def get_mysql_driver():
    """Return any MySQL driver that's installed"""
    try:
        import mysql.connector
        return mysql.connector
    except ImportError:
        pass

    try:
        if USE_MYSQLDB:
            import MySQLdb, _mysql_exceptions
            return MySQLdb
    except ImportError:
        pass

    try:
        if USE_PYMYSQL:
            import pymysql, pymysql.err
            return pymysql
    except ImportError:
        pass

    raise RuntimeError("Cannot find MySQL driver")

def get_mysql_config(fname=None):
    """Get a ConfigParser that's preped with the MySQL defaults"""
    import configparser
    config = configparser.ConfigParser()
    config.add_section('mysql')
    config['mysql'] = {"host":"",
                       "user":"",
                       "passwd":"",
                       "port":DEFAULT_MYSQL_PORT,
                       "db":DEFAULT_MYSQL_DB,
                       "mysqldump":"mysqldump" }
    if fname:
        config.read(fname)
    return config


def mysql_dump(config):
    """Using the config, dump MySQL schema"""
    mc = config["mysql"]
    cmd = ['mysqldump','-h',mc['host'],'-u',mc['user'],'-p' + mc['passwd'], '-d',mc['db']]
    print(cmd)
    return subprocess.call(cmd)

class mysql:
    """Encapsulate a MySQL connection"""
    def __init__(self,config):
        self.config        = config
        self.conn          = None
        self.execute_count = 0  # count number of executes
        self.mysql_max_executes = DEFAULT_MAX_EXECUTES
        self.debug         = config.getint('mysql','debug')

    def send_schema(self,schema):
        c = self.conn.cursor()
        for stmt in schema.split(";"):
            stmt = stmt.strip()
            if stmt:
                print("send ",stmt)
                c.execute(stmt)

    def upgrade_schema(self):
        """Upgrade schema if necessary"""
        self.connect()
        cursor = self.conn.cursor()
        cursor.execute("show tables like 'metadata'")
        res = cursor.fetchall()
        if res:
            return
        self.send_schema(open("schema_v1_v2.sql","r").read())

    def connect(self):
        self.mysql = get_mysql_driver()
        try:
            self.conn = self.mysql.connect(host=self.config.get("mysql","host"),
                                           port=self.config.getint("mysql",'port'),
                                           user=self.config.get("mysql","user"),
                                           passwd=self.config.get("mysql","passwd"),
                                           db=self.config.get("mysql","db"))
            self.conn.cursor().execute("set innodb_lock_wait_timeout=20")
            self.conn.cursor().execute("SET tx_isolation='READ-COMMITTED'")
            self.conn.cursor().execute("SET time_zone = '+00:00'")

        except RuntimeError as e:
            print("Cannot connect to mysqld. host={} user={} passwd={} port={} db={}".format(
                self.config.get('mysql','host'),
                self.config.get('mysql','user'),
                self.config.get('mysql','passwd'),
                self.config.get('mysql','port'),
                self.config.get('mysql','db')))
            raise e

    def execute(self,cmd,args=None):
        """Execute an SQL command and return the cursor, which can be used as an iterator.
        Connect to the database if necessary."""
        self.execute_count += 1
        if self.mysql_max_executes and self.execute_count > self.mysql_max_executes:
            self.close()        # close out and reconnect
        if not self.conn:
            self.connect()
        if self.debug: print("db.execute({},{}) PID:{}".format(cmd,args,os.getpid()))
        cursor = self.conn.cursor()
        cursor.execute(cmd,args)
        return cursor
    
    def select1(self,cmd,args=None):
        """execute an SQL command and return the first row"""
        cursor = self.execute(cmd,args)
        return cursor.fetchone()

    def mysql_version(self):
        return self.select1("select version();")[0]

    def commit(self):
        if self.debug: print("db.COMMIT PID:{}".format(os.getpid()))
        self.conn.commit()

    def close(self):
        if self.conn:
            del self.conn           # delete the connection if it exists
            self.conn = None

def mysql_stats(c):
    global max_id
    c = conn.cursor()
    if args.debug: 
        print(time.asctime())
    for table in ["times","dated"]:
        c.execute("select count(*) from "+table)
        p = c.fetchone()[0]
        if table not in start_rows:
            print("Start Rows in {}: {:,}".format(table,p))
        else:
            print("End Rows in {}: {:,} ({:,} new)".format(table,p,p-start_rows[table]))
        start_rows[table] = p

    c.execute("select max(id) from dated")
    max_id = c.fetchone()[0]
        
    if args.debug:
        print("New dated rows:")
        c.execute("select * from dated where id>%s",(max_id,))
        for row in c.fetchall():
            print(row)

    

if __name__=="__main__":
    import argparse
    import configparser
    import sys

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--config',help='specify config file')
    parser.add_argument("--dumpschema",action="store_true")

    args = parser.parse_args()
    config = get_mysql_config(args.config)

    if args.dumpschema:
        mysql_dumpschema(config)

