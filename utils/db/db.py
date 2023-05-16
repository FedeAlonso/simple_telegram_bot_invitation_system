import sqlite3
import os
import string
import random
import logging
from datetime import datetime
from pathlib import Path


def log_and_query(conn, query):
    """
    Log a query and execute it.

        Parameters:
            conn (connection object): SQLite3 connection object
            query (str): Query to execute
    """
    logging.info(query)
    conn.execute(query)


def create_db_if_not_exist(db_name):

    #Check if db not exists:
    if not Path(db_name).is_file():
        # Check if the db file should be contained in a folder that does not exist
        db_path_list = db_name.split(os.path.sep)
        if len(db_path_list) > 1:
            db_path_directory = db_name.replace(db_path_list[-1], "")
            if not Path(db_path_directory).is_dir():
                Path(db_path_directory).mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_name)
        logging.info("Opened database successfully")
        conn.close()


def create_tables_if_not_exist(db_name):
    """
    USERS:
        ID: Telegram ID
        NAME: Telegram NAME
        ROL: 0: Super Admin
             1: Admin
             2: User
        TYPE: We can have different types of Users. Like customers, assistants, inviters
        REGISTRATION_DATE: Registration date
        REGISTRATION_INVITATION: Invitation from INVITATIONS table
        CONVERSATION_STATUS: To maintain the conversation after an update. 0 by default. Also can be modified to 1 if /cancel
    
    INVITATIONS:
        ID: Autoincrement PK
        INVITATION: Invitation
        INVITATING_USER_ID: User ID who is inviting someone
        INVITATION_USED: 0 if not, 1 if already used
    """

    conn = sqlite3.connect(db_name)
    # Table Users
    conn.execute('''CREATE TABLE IF NOT EXISTS USERS
            (ID INT PRIMARY KEY,
            NAME TEXT NOT NULL,
            ROL INT NOT NULL,
            TYPE TEXT NOT NULL,
            REGISTRATION_DATE INT NOT NULL,
            REGISTRATION_INVITATION TEXT NOT NULL,
            CONVERSATION_STATUS INT NOT NULL);''')
    logging.info("Table USERS created (OR NOT) successfully")

    # Table Invitations
    conn.execute('''CREATE TABLE IF NOT EXISTS INVITATIONS
            (ID INTEGER PRIMARY KEY AUTOINCREMENT,
            INVITATION TEXT NOT NULL,
            INVITING_USER_ID INT,
            INVITATION_USED INT);''')
    logging.info("Table INVITATIONS created (OR NOT) successfully")
    conn.close()


def insert_in_users(db_name, user_info):

    conn = sqlite3.connect(db_name)
    query =  f"""
        INSERT INTO USERS (ID,NAME,ROL,TYPE,REGISTRATION_DATE,REGISTRATION_INVITATION, CONVERSATION_STATUS) 
        VALUES ({user_info["id"]}, '{user_info["name"]}', {user_info["rol"]}, '{user_info["type"]}', {user_info["registration_date"]}, '{user_info["registration_invitation"]}', 0)
    """
    log_and_query(conn, query)
    conn.commit()
    logging.info("Records created successfully")
    conn.close()


def generate_new_invitations(db_name, num_invitations=1, user_id=None):
    """
    Create new invitations and assign them to a user
        
        Parameters:
            db_name (str): SQLite 3 DB file
            num_invitations (int): Num. of invitations to assign
            user_id (int): Telegram ID of the user which is going to get the invitations
    """
    characters = string.ascii_lowercase + string.digits
    conn = sqlite3.connect(db_name)
    for i in range(num_invitations):
        invitation = ''.join(random.choice(characters) for i in range(8))
        query = f"""
            INSERT INTO INVITATIONS (INVITATION) 
            VALUES ('{invitation}')
        """
        if user_id is not None:
            # Verify that the user exists in the USERS table
            query = f"SELECT COUNT(*) FROM USERS WHERE ID={user_id}"
            log_and_query(conn, query)
            user_exist = cursor.fetchone()[0] == 1
            
            if user_exist:
                query = f"""
                    INSERT INTO INVITATIONS (INVITATION, INVITING_USER_ID, INVITATION_USED) 
                    VALUES ('{invitation}', {user_id}, 0)
                """
            else:
                logging.error(f"Cannot assign invitations. User {user_id} does not exist")
                break
                
        log_and_query(conn, query)
        conn.commit()
        logging.info("Records created successfully")
    conn.close()


def provision_superadmin(db_name, superadmin_id):
    """
    Provision a first user in order to make everything work
        
        Parameters:
            db_name (str): SQLite 3 DB file
            superadmin_id (int): Telegram ID of the superadmin user
    """
    # Verify that the user does not exist in the USERS table
    conn = sqlite3.connect(db_name)
    query = f"SELECT COUNT(*) FROM USERS WHERE ID={first_user_id}"
    log_and_query(conn, query)
    user_exist = cursor.fetchone()[0] == 1
    if user_exist:
        logging.error("ERROR: First user already provisioned")
        return
    
    user_info = {
        "id": first_user_id,
        "name": "super_admin",
        "rol": 0,
        "type": "super_admin",
        "registration_date": int(datetime.now().strftime("%Y%m%d%H%M%S")),
        "registration_invitation": "0000"
    }
    insert_in_users(db_name, user_info)


def get_user_available_invitations(db_name, user_id):
    """
    Get available of a user, given it's user_id
        
        Parameters:
            db_name (str): SQLite 3 DB file
            user_id (int): Telegram ID of the user 
    """
    conn = sqlite3.connect(db_name)
    query = f"SELECT INVITATION FROM INVITATIONS WHERE INVITING_USER_ID={user_id} AND INVITATION_USED=0"

    query = f"SELECT COUNT(*) FROM USERS WHERE ID={first_user_id}"
    logging.info(query)
    cursor = conn.execute(query)
    user_exist = cursor.fetchone()[0] == 1
    if user_exist:
        logging.error("ERROR: First user already provisioned")
        return
