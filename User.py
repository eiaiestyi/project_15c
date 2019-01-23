import getpass

from airtable import Airtable
from passlib.context import CryptContext

import config


class User:
    def __init__(self):
        # Connect to Airtable
        self.users_table = Airtable(config.base_key, 'users', config.api_key)
        self.user = {}

    def login(self):
        """
        Login or create new user.
        :return:
        """
        # self.login or create new user?
        con_or_new = input('To self.login, enter L, to create new user, enter N: ')
        if (not con_or_new.upper() == 'L') and (not con_or_new.upper() == 'N'):
            # If neither 'L' or 'N' entered, ask again
            return self.login()
        else:
            # Ask for username and password
            username = input('Username: ')
            password = getpass.getpass()
            crypt = CryptContext(schemes=["bcrypt"])
            if con_or_new.upper() == 'L':
                # Login
                user = self.users_table.search('name', username)
                if not user:
                    # Error if user name not found
                    print('User does not exist.')
                    return self.login()
                else:
                    # Check password
                    user = user[0]
                    if not crypt.verify(password, user['fields']['password']):
                        # Error if password is incorrect
                        print('Password incorrect.')
                        return self.login()
            else:
                # Create new user
                if not self.users_table.search('name', username):
                    # If name doesn't exist, crete new user
                    user = self.users_table.insert({'name': username, 'password': crypt.hash(secret=password)})
                else:
                    # Error if user name already exists
                    print('User {} already exists.'.format(username))
                    return self.login()
            if user:
                print('Logged in successfully as {}.'.format(username))
                self.user = user['fields']
            else:
                self.login()

    def change_password(self):
        password = getpass.getpass()
        crypt = CryptContext(schemes=["bcrypt"])
        self.users_table.update_by_field('name', self.user['name'], {'password': crypt.hash(secret=password)})
        print('Password changed.')
