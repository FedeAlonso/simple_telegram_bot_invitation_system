# Simple Telegram BOT invitation System
Simple telegram bot invitation system. Written in python.

_This code is a functional POC_

The code is a modified version of [echobot](https://docs.python-telegram-bot.org/en/stable/examples.echobot.html) , with an invitation system added, so you cannot access the bot's functionality if you do not have an invitation.

## Before running:
### Install dependencies
The code has been tested in ython 3.9.2. 
We recommend the use of [virtual environments](https://docs.python.org/3/library/venv.html).
To install the dependencies, run in a terminal:
```sh
$ pip install -r requirements.txt
```

### Config file
In the _resources/config.json_ file we can configure the file where the database will be created

## Running the bot:
Once the dependencies have been installed, run the following line in a terminal:
```sh
$ python invitation_bot.py
```

## DB
Two different tables have been created, one to manage users and the other to manage invitations.

### USERS table
| Field  | Description |
| ------ | ----------- |
| ID | Telegram User ID |
| NAME | Telegram User First Name |
| ROL | 0 (Super Admin), 1 (Admin), 2(user) |
| TYPE | Descriptive field to describe different types of users (assistant, customer, ...). Not used|
| REGISTRATION_DATE | Registration Date |
| REGISTRATION_INVITATION | Invitation from INVITATIONS table |
| CONVERSATION_STATUS | To maintain the conversation after an update. 0 by default. Also can be modified to 1 if /cancel. Not Used |

### INVITATIONS table
| Field  | Description |
| ------ | ----------- |
| ID | Autoincrement PK |
| INVITATION | Invitation |
| INVITATING_USER_ID | User ID who is inviting someone |
| INVITATION_USED | 0 if not, 1 if already used |

