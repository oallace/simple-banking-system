import sqlite3
import random as rd


DATA_FILE, TABLE_NAME = ('card.s3db', 'card')
ID_NUMBER, NUMBER_INDEX, PIN_INDEX, BALANCE_INDEX = (0, 1, 2, 3)


class BankingData:

    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()

    def create_table(self, table_name):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (\n"
                            f"id INTEGER,\n"
                            f"number TEXT,\n"
                            f"pin TEXT,\n"
                            f"balance INTEGER DEFAULT 0);")
        self.connection.commit()

    def write_card(self, table_name, number, pin):
        account_id = int(number[6:15])
        self.cursor.execute(f"INSERT INTO {table_name} VALUES ({account_id}, {number}, {pin}, 0);")
        self.connection.commit()

    def search(self, table_name, number):
        res = self.cursor.execute(f"SELECT * FROM {table_name} WHERE number = {number}")
        return res.fetchone()

    def update_balance(self, table_name, number, new_balance):
        self.cursor.execute(f"UPDATE {table_name} SET balance = {new_balance} WHERE number = {number}")
        self.connection.commit()

    def delete_card(self, table_name, number):
        self.cursor.execute(f"DELETE FROM {table_name} WHERE number = {number}")
        self.connection.commit()


def luhn_algorithm(str_number):
    total = 0
    double = True
    for d in str_number:
        d = int(d)
        if double:
            d = 2 * d
            if d > 9:
                d = d - 9
            double = False
        else:
            double = True
        total += d
    cs = (10 - total % 10) % 10
    return cs


def generate_card_number(database, table_name):
    account_id = rd.randint(0, 999999999)
    while database.cursor.execute(f'SELECT id FROM {table_name} WHERE id = {account_id}').fetchone():
        account_id = rd.randint(0, 999999999)
    card_number = "400000" + "{:09d}".format(account_id)
    card_number += str(luhn_algorithm(card_number))
    return card_number


def generate_pin():
    return "{:04}".format(rd.randint(0, 9999))


def ask_operation():
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")
    return input()


def ask_logged_operation():
    print("1. Balance")
    print("2. Add income")
    print("3. Do transfer")
    print("4. Close account")
    print("5. Log out")
    print("0. Exit")
    return input()


def logged_menu(database, card_number):
    op = ask_logged_operation()
    card_infos = database.search(TABLE_NAME, card_number)
    while op != "5":
        if op == "1":
            print(f"Balance: {card_infos[BALANCE_INDEX]}")
        elif op == "2":
            # add income
            print("Enter income:")
            income = int(input())
            database.update_balance(TABLE_NAME, card_number, card_infos[BALANCE_INDEX] + income)
            card_infos = database.search(TABLE_NAME, card_number)
            print("Income was added!")
            op = ask_logged_operation()
        elif op == "3":
            # do transfer:
            print("Enter card number:")
            dest = input()
            if int(dest[-1]) != luhn_algorithm(dest[:-1]):
                print("Probably you made a mistake in the card number.")
                print("Please try again!")
            elif not database.search(TABLE_NAME, dest):
                print("Such a card does not exist")
            else:
                print("Enter how much money you want to transfer:")
                amount = int(input())
                if amount > card_infos[BALANCE_INDEX]:
                    print("Not enough money!")
                else:
                    dest_infos = database.search(TABLE_NAME, dest)
                    database.update_balance(TABLE_NAME, dest, dest_infos[BALANCE_INDEX] + amount)
                    database.update_balance(TABLE_NAME, card_number, card_infos[BALANCE_INDEX] - amount)
                    card_infos = database.search(TABLE_NAME, card_number)
                    print("Success!")
            op = ask_logged_operation()
        elif op == "4":
            # close account
            database.delete_card(TABLE_NAME, card_number)
            print("The account has been closed!")
            break
        elif op == "0":
            return -1

    return 0


def main_menu(database):
    op = ask_operation()
    while op != "0":
        if op == "1":
            new_card_number = generate_card_number(database, TABLE_NAME)
            pin = generate_pin()
            database.write_card(TABLE_NAME, new_card_number, pin)
            print("Your card has been created")
            print("Your card number:")
            print(new_card_number)
            print("Your card PIN:")
            print(pin)
            print('\n')
        elif op == "2":
            print("Enter your card number:")
            card_number = input()
            print("Enter your PIN:")
            pin = input()
            card_info = database.search(TABLE_NAME, card_number)
            if card_info and int(card_info[PIN_INDEX]) == int(pin):
                print("You have successfully logged in!\n")
                if logged_menu(database, card_number) == -1:
                    break
            else:
                print("Wrong card number or PIN!")

        else:
            print("Enter a valid operation!")
        op = ask_operation()
    print("Bye!")


if __name__ == '__main__':

    data = BankingData(DATA_FILE)
    data.create_table(TABLE_NAME)
    main_menu(data)
