from User import User
from Word import Word


# Learn or change password
def options():
    """
    Give selection of three options: start learning, change password or exit.
    :return:
    """
    selection = input(
        'To start learning, type START, to change password, type CHANGE, to stop program, type anything: ')
    if selection.lower() == 'start':
        # Start learning!
        word.learn()
    elif selection.lower() == 'change':
        # Change password
        user.change_password()
    else:
        print('Program stopped.')
        return False
    return options()


user = User()
# Login or create new user
user.login()

# Get scores and words
word = Word(user.user['name'])

options()
