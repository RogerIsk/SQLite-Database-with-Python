import sqlite3
import time
import os

program_files_path = os.path.join(os.path.dirname(__file__), 'Program Files')

if not os.path.exists(program_files_path):                  # Ensure the 'Program Files' directory exists
    os.makedirs(program_files_path)

database_link = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'crime_investigation.db'))  # Connect to the SQLite database
interact_with_database = database_link.cursor()             # Create a cursor for database interaction

def wait_and_clear():                                       # Helper function to wait and clear the screen
    time.sleep(2)
    os.system('clear')

def main_menu():                                            # Main menu function
    os.system('clear')
    print('''        MAIN MENU
_________________________
 1. Create new cases
 2. Update existing information
 3. Display existing information
 4. Delete information
 5. Create new tables
 6. Display existing tables
 7. Delete tables
10. Exit
        ''')
    menu_choice = input('Enter a choice [number]: ')
    while True:
        if menu_choice == '1':
            add_new_info_to_a_table()
        elif menu_choice == '2':
            update_tables()
        elif menu_choice == '3':
            display_information_menu()
        elif menu_choice == '4':
            delete_information()
        elif menu_choice == '5':
            create_tables()
            go_to_menu()
        elif menu_choice == '6':
            os.system('clear')
            print('Currently existing tables\n_________________________')
            display_existing_tables()
            input('\nPress enter for menu ')
            main_menu()
        elif menu_choice == '7':
            delete_tables()
        elif menu_choice == '10':
            database_link.close()
            exit()
        else:
            print('Enter a valid choice...')
            time.sleep(2)
            main_menu()

def go_to_menu():                                           # Helper function to wait and clear the screen, then go to the main menu
    wait_and_clear()
    main_menu()

def log_entry(case_id, message):                            # Function to create log entries in 'Program Files'
    case_folder = os.path.join(program_files_path, f'case_{case_id}') # we let the code know where and under what name the files will be saved
    if not os.path.exists(case_folder):                     # if the file doesnt exist
        os.makedirs(case_folder)                            # create it

    with open(os.path.join(case_folder, 'log.txt'), 'a') as log_file:  # Open the log file in append mode
        log_file.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - {message}\n')  # Write the log entry with a timestamp

def add_new_info_to_a_table():                              # Function to add new information to tables
    os.system('clear')
    print('To which table would you\nlike to add new information?\n_________________________')

    sorted_tables = display_existing_tables()
    table_choice = input('\nEnter a choice [number / item name]: ').capitalize()

    if table_choice.lower() == 'back to main menu' or table_choice == 'back':
        main_menu()
        return

    try:                                                    # Match input with table name or number
        table_index = int(table_choice) - 1                 # we will choose 1 for the 0 element so we have to bring it down by 1 to match the 0
        if 0 <= table_index < len(sorted_tables):           # if the user input was between 1-5 or the right word
            table_choice = sorted_tables[table_index]       # the user choice = the right item
        else:                                               
            raise ValueError                                # happens when we enter smth we are not supposed to and then...
    except ValueError:                                      # ...we go to this code
        if table_choice not in sorted_tables:               # if we choose smth other than 1-5 or some other bs
            print('Enter a valid choice')
            time.sleep(2)
            add_new_info_to_a_table()                       # the menu starts all over after giving a 2 second message
            return

    while True:                                             # if we entered our option correctly we continue to the appropriate option
        if table_choice == 'Crimes':                        # only Crimes table works with ID because its a bit more special than the others
            os.system('clear')
            crime_type = input('What type of crime is it?:          ')
            crime_date = input('When did the crime happen? (date):  ')
            crime_location = input('Where did the crime happen?:        ')
            interact_with_database.execute(f"INSERT INTO Crimes (Type, Date, Location) VALUES (?, ?, ?);",(crime_type, crime_date, crime_location))
            crime_id = interact_with_database.lastrowid     # Get the last inserted row ID (CrimeID)   (chatgpt helped with this line)
            if save_confirmation():                         # the user gets asked if hes sure and if the answe is yes the info gets added to the table
                log_entry(crime_id, f'New crime added: {crime_type}, Date: {crime_date}, Location: {crime_location}')
            print('\nNew crime added.')
            time.sleep(2)
            add_new_info_to_a_table()                       # after all that we go back to the previous menu

        elif table_choice == 'Evidence':
            os.system('clear')
            evidence_type = input('What type of evidence is it?:                        ')
            evidence_description = input('Short description of the evidence:                   ')
            crime_indices = select_multiple_crimes()
            if crime_indices:
                for crime_id in crime_indices:
                    interact_with_database.execute(f"INSERT INTO Evidence (Type, Description, CrimeID) VALUES (?, ?, ?);",(evidence_type, evidence_description, crime_id))
                if save_confirmation():
                    for crime_id in crime_indices:
                        log_entry(crime_id, f'New evidence added: {evidence_type}, Description: {evidence_description}')
                print(f'\nNew evidence added to Crimes: {", ".join(map(str, crime_indices))}.')
            time.sleep(2)
            add_new_info_to_a_table()

        elif table_choice == 'Officers':
            os.system('clear')
            officers_name = input("Officers' first and last name:                      ")
            officers_rank = input("Officers' rank:                                     ")
            officers_department = input("Officers' department:                               ")
            crime_indices = select_multiple_crimes()
            if crime_indices:
                for crime_id in crime_indices:
                    interact_with_database.execute(f"INSERT INTO Officers (Name, Rank, Department, CrimeID) VALUES (?, ?, ?, ?);",(officers_name, officers_rank, officers_department, crime_id))
                if save_confirmation():
                    for crime_id in crime_indices:
                        log_entry(crime_id, f'Officer added: {officers_name}, Rank: {officers_rank}, Department: {officers_department}')
                print(f'\nNew officer added to Crimes: {", ".join(map(str, crime_indices))}.')
            time.sleep(2)
            add_new_info_to_a_table()

        elif table_choice == 'Suspects':
            os.system('clear')
            suspects_name = input('What is the name of the suspect ?:                     ')
            suspects_age = input('How old is the suspect?:                               ')
            suspects_description = input('Short description of the suspect:                      ')
            crime_indices = select_multiple_crimes()
            if crime_indices:
                for crime_id in crime_indices:
                    interact_with_database.execute(f"INSERT INTO Suspects (Name, Age, Description, CrimeID) VALUES (?, ?, ?, ?);", 
                                                   (suspects_name, suspects_age, suspects_description, crime_id))
                if save_confirmation():
                    for crime_id in crime_indices:
                        log_entry(crime_id, f'Suspect added: {suspects_name}, Age: {suspects_age}, Description: {suspects_description}')
                print(f'\nNew suspect added to Crimes: {", ".join(map(str, crime_indices))}.')
            time.sleep(2)
            add_new_info_to_a_table()

        elif table_choice.lower() == 'back to main menu':
            main_menu()

        else:
            print('Please enter a valid choice...')
            time.sleep(2)
            add_new_info_to_a_table()

def prepare_to_delete_crime():                              # A special function that works only with Crimes because 'Crimes' has more options than other tables
    os.system('clear')
    interact_with_database.execute('SELECT CrimeID, Type, Date, Location FROM Crimes') # returns all the requested info from the table
    crimes = interact_with_database.fetchall()              # allows us to access all the info in the form of a list in which each item is a tupple

    if not crimes:                                          # if the list of tupples is empty = []
        print('No crimes found. Returning to menu...')
        time.sleep(2)
        main_menu()
        return None

    print('Select a crime:\n')
    for index, crime in enumerate(crimes, start=1):         # for each tupple() in the list[] we print a tupple and add an index to it
        print(f"{index}. CrimeID: {crime[0]} | Type: {crime[1]} | Date: {crime[2]} | Location: {crime[3]}")

    choice = input(f'\nEnter the crime number [1-{len(crimes)}] or "back" to return: ') # user help if they dont know what to enter (1-4) + hidden back option

    if choice.lower() == 'back':
        delete_information()
        return None

    try:
        crime_index = int(choice) - 1
        if 0 <= crime_index < len(crimes):
            return crimes[crime_index]                      # Return the selected crime details
        else:
            raise ValueError
    except ValueError:
        print('Enter a valid crime number')
        time.sleep(2)
        return prepare_to_delete_crime()

def select_multiple_crimes():
    os.system('clear')
    interact_with_database.execute('SELECT CrimeID, Type, Date, Location FROM Crimes')
    crimes = interact_with_database.fetchall()

    if not crimes:
        print('No crimes found. Returning to menu...')
        time.sleep(2)
        main_menu()
        return []

    print('Select for which crimes:\n')
    for index, crime in enumerate(crimes, start=1):
        print(f"{index}. CrimeID: {crime[0]} | Type: {crime[1]} | Date: {crime[2]} | Location: {crime[3]}")

    choice = input(f'\nEnter the crime numbers [e.g., 1,3,5 for multiple choices] or "back" to return: ')

    if choice.lower() == 'back':
        return []

    try:
        crime_indices = [int(i.strip()) - 1 for i in choice.split(',')]
        valid_crimes = [crimes[i][0] for i in crime_indices if 0 <= i < len(crimes)]
        if not valid_crimes:
            raise ValueError
        return valid_crimes
    except ValueError:
        print('Enter valid crime numbers')
        time.sleep(2)
        return select_multiple_crimes()

def save_confirmation():
    answer = input('\nAre you sure you want to save this? (yes/no) \n')
    while True:
        if answer.lower() in ['yes', 'y']:
            database_link.commit()
            return True
        elif answer.lower() in ['no', 'n']:
            print('\nOperation cancelled, going to main menu...')
            wait_and_clear()
            main_menu()
            return False
        else:
            print('Enter a valid option...')
            wait_and_clear()
            save_confirmation()

def update_tables():
    os.system('clear')
    print('Which table would you\nlike to update?\n_________________________')
    sorted_tables = display_existing_tables()
    table_choice = input('\nEnter a choice [number / item name] or "back" to return: ').capitalize()

    if table_choice.lower() == 'back' or table_choice == '5':
        main_menu()
        return

    try:
        table_index = int(table_choice) - 1
        if 0 <= table_index < len(sorted_tables):
            table_choice = sorted_tables[table_index]
        else:
            raise ValueError
    except ValueError:
        if table_choice not in sorted_tables:
            print('Enter a valid choice')
            time.sleep(2)
            update_tables()
            return

    # Display existing records in the selected table
    os.system('clear')
    interact_with_database.execute(f'SELECT rowid, * FROM {table_choice}')
    rows = interact_with_database.fetchall()

    if not rows:
        print(f'No records found in {table_choice}. Returning to menu...')
        time.sleep(2)
        main_menu()
        return

    column_names = [description[0] for description in interact_with_database.description]

    # Display the records for selection
    print(f'Select a record from the {table_choice} table to update or "back" to return:\n')

    for index, row in enumerate(rows, start=1):
        # Zip column names with the row values, but skip the 'rowid' or duplicate primary key (assumed to be the first column)
        row_display = [f"{col_name}: {value}" for col_name, value in zip(column_names[1:], row[1:])]
        print(f"{index}. " + " | ".join(row_display))

    record_choice = input(f'\nEnter the record number to update [1-{len(rows)}]: ')

    if record_choice.lower() == 'back':
        update_tables()
        return
    
    try:
        record_index = int(record_choice) - 1
        if 0 <= record_index < len(rows):
            selected_row = rows[record_index]
        else:
            raise ValueError
    except ValueError:
        print('Enter a valid record number')
        time.sleep(2)
        update_tables()
        return

    # Display columns to update
    os.system('clear')
    print(f'Which field would you like to update in the selected record?\n')
    for index, column_name in enumerate(column_names[2:], start=1):  # Skip the first two columns (rowid and the primary key)
        print(f"{index}. {column_name}")

    field_choice = input(f'\nEnter the field number to update [1-{len(column_names) - 2}] or "back" to return: ')

    if field_choice.lower() == 'back':
        update_tables()
        return

    try:
        field_index = int(field_choice) - 1
        if 0 <= field_index < len(column_names) - 2:
            field_name = column_names[field_index + 2]  # Adjust for skipping the first two columns
        else:
            raise ValueError
    except ValueError:
        print('Enter a valid field number')
        time.sleep(2)
        update_tables()
        return

    new_value = input(f'Enter the new value for {field_name} or "back" to return: ')

    if new_value.lower() == 'back':
        update_tables()
        return

    # Update the record in the database
    try:
        interact_with_database.execute(f'UPDATE {table_choice} SET {field_name} = ? WHERE rowid = ?', (new_value, selected_row[0]))
        if save_confirmation():
            log_entry(selected_row[0], f'Updated {field_name} to {new_value} in {table_choice} table')
        print(f'\nRecord updated successfully in {table_choice}.')
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    time.sleep(2)
    update_tables()

def displaying_function(table_choice):  # Function to display information from tables
    os.system('clear')
    print(f'All {table_choice}')
    print('_________________________')

    # Execute the query to fetch all rows from the chosen table
    interact_with_database.execute(f'SELECT * FROM {table_choice}')
    rows = interact_with_database.fetchall()

    # Fetch column names to use as headers
    column_names = [description[0] for description in interact_with_database.description]

    # Find the maximum width of each column for pretty printing
    column_widths = [max(len(str(value)) for value in column) for column in zip(*([column_names] + rows))]

    # Create a format string for each row
    format_string = '  '.join(f'{{:<{width}}}' for width in column_widths)

    # Print the header row
    print(format_string.format(*column_names))
    print('-' * sum(column_widths))

    # Print each row of data
    for row in rows:
        print(format_string.format(*row))

    # Prompt to continue
    input('\nPress Enter to continue ')
    display_information_menu()

def display_crimes_data(full_info=True):
    os.system('clear')

    if full_info:
        print('Displaying all crimes with corresponding data...\n')
    else:
        print('Displaying all crimes...\n')

    # Fetch all crimes
    interact_with_database.execute('SELECT CrimeID, Type, Date, Location FROM Crimes')
    crimes = interact_with_database.fetchall()

    for crime in crimes:
        crime_id, crime_type, crime_date, crime_location = crime
        print(f"Crime #{crime_id}:")
        print(f"  Type: {crime_type}")
        print(f"  Date: {crime_date}")
        print(f"  Location: {crime_location}")

        if full_info:
            # Fetch corresponding evidence
            interact_with_database.execute('SELECT Type, Description FROM Evidence WHERE CrimeID = ?', (crime_id,))
            evidence = interact_with_database.fetchall()
            if evidence:
                print("  Evidence:")
                for ev in evidence:
                    print(f"    - Type: {ev[0]}, Description: {ev[1]}")
            else:
                print("  Evidence: None")

            # Fetch corresponding officers
            interact_with_database.execute('SELECT Name, Rank, Department FROM Officers WHERE CrimeID = ?', (crime_id,))
            officers = interact_with_database.fetchall()
            if officers:
                print("  Officers:")
                for officer in officers:
                    print(f"    - Name: {officer[0]}, Rank: {officer[1]}, Department: {officer[2]}")
            else:
                print("  Officers: None")

            # Fetch corresponding suspects
            interact_with_database.execute('SELECT Name, Age, Description FROM Suspects WHERE CrimeID = ?', (crime_id,))
            suspects = interact_with_database.fetchall()
            if suspects:
                print("  Suspects:")
                for suspect in suspects:
                    print(f"    - Name: {suspect[0]}, Age: {suspect[1]}, Description: {suspect[2]}")
            else:
                print("  Suspects: None")

        print("\n" + "-"*40 + "\n")  # Separator between crimes

    input('Press Enter to return to the menu ')
    display_information_menu()

def display_information_menu():  # Menu for displaying information
    os.system('clear')
    print('What would you like to display?\n_________________________')
    print('1. Crimes (full info)')
    print('2. Crimes (only)')
    print('3. Evidence')
    print('4. Officers')
    print('5. Suspects')
    print('6. Back to main menu')

    choice = input('\nEnter a choice [number]: ').strip()

    if choice == '1':
        display_crimes_data(full_info=True)
    elif choice == '2':
        display_crimes_data(full_info=False)
    elif choice == '3':
        displaying_function('Evidence')
    elif choice == '4':
        displaying_function('Officers')
    elif choice == '5':
        displaying_function('Suspects')
    elif choice == '6':
        main_menu()
    else:
        print('Enter a valid choice...')
        time.sleep(2)
        display_information_menu()

def delete_information():  # Function to delete specific information
    os.system('clear')
    print('What would you like to delete?\n_________________________')
    print('1. Crimes')
    print('2. Evidence')
    print('3. Officer')
    print('4. Suspect')
    print('5. Multiple records')
    print('6. Back to main menu')

    choice = input('\nEnter a choice [number]: ').strip()

    if choice == '1':
        delete_crime()
    elif choice == '2':
        delete_from_table('Evidence')
    elif choice == '3':
        delete_from_table('Officers')
    elif choice == '4':
        delete_from_table('Suspects')
    elif choice == '5':
        delete_multiple_records()
    elif choice == '6':
        main_menu()
    else:
        print('Enter a valid choice...')
        time.sleep(2)
        delete_information()

def delete_crime():  # Delete a crime with options
    os.system('clear')
    crime = prepare_to_delete_crime()
    if crime is not None:
        crime_id = crime[0]  # Get the CrimeID from the selected crime

        print('\nChoose an option:')
        print('1. Delete crime and all related information')
        print('2. Delete only the crime (leave related information)')

        choice = input('\nEnter your choice [1/2] or "back" to return: ').strip()

        if choice == '1':
            delete_confirmation()

            try:
                interact_with_database.execute('DELETE FROM Evidence WHERE CrimeID = ?', (crime_id,))
                interact_with_database.execute('DELETE FROM Officers WHERE CrimeID = ?', (crime_id,))
                interact_with_database.execute('DELETE FROM Suspects WHERE CrimeID = ?', (crime_id,))
                interact_with_database.execute('DELETE FROM Crimes WHERE CrimeID = ?', (crime_id,))
                if save_confirmation():
                    log_entry(crime_id, 'Crime and all related information deleted')
                print(f'\nCrime #{crime_id} and all related information deleted.')
            except sqlite3.Error as e:
                print(f"An error occurred: {e}")
        elif choice == '2':
            delete_confirmation()

            try:
                interact_with_database.execute('DELETE FROM Crimes WHERE CrimeID = ?', (crime_id,))
                if save_confirmation():
                    log_entry(crime_id, 'Crime deleted, related information retained')
                print(f'\nCrime #{crime_id} deleted, but related information retained.')
            except sqlite3.Error as e:
                print(f"An error occurred: {e}")
        elif choice.lower() == 'back':
            delete_information()
            return
        else:
            print('Invalid choice. Returning to menu...')
            time.sleep(2)
            main_menu()

    go_to_menu()

def delete_from_table(table_name):  # Delete specific records from a table
    os.system('clear')
    interact_with_database.execute(f'SELECT rowid, * FROM {table_name}')
    rows = interact_with_database.fetchall()

    if not rows:
        print(f'No records found in {table_name}. Returning to menu...')
        time.sleep(2)
        main_menu()
        return

    column_names = [description[0] for description in interact_with_database.description]

    # Display the records for selection
    print(f'Select a record from the {table_name} table to delete or "back" to return:\n')
    for row in rows:
        row_display = [f"{col_name}: {value}" for col_name, value in zip(column_names[1:], row[1:])]
        print(" | ".join(row_display))

    record_choice = input(f'\nEnter the ID number you wish to delete [or multiple e.g 1,2,3] or "back" to return: ')

    if record_choice.lower() == 'back':
        delete_information()
        return

    delete_records_by_indices(table_name, record_choice)

def delete_records_by_indices(table_name, record_choice):
    try:
        indices = [int(i.strip()) - 1 for i in record_choice.split(',')]
        for index in indices:
            if index >= 0:
                interact_with_database.execute(f'DELETE FROM {table_name} WHERE rowid = ?', (index + 1,))
        if save_confirmation():
            for index in indices:
                log_entry(index + 1, f'Record deleted from {table_name}')
        database_link.commit()
        print(f'\nSelected records deleted successfully from {table_name}.')
    except ValueError:
        print('Invalid input. Please enter valid numbers separated by commas.')
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    go_to_menu()

def delete_multiple_records():
    os.system('clear')
    print('From which table would you like to delete multiple records?\n_________________________')
    print('1. Crimes')
    print('2. Evidence')
    print('3. Officers')
    print('4. Suspects')
    print('5. Back to main menu')

    choice = input('\nEnter a choice [number]: ').strip()

    if choice == '1':
        delete_from_table('Crimes')
    elif choice == '2':
        delete_from_table('Evidence')
    elif choice == '3':
        delete_from_table('Officers')
    elif choice == '4':
        delete_from_table('Suspects')
    elif choice == '5':
        delete_information()
    else:
        print('Enter a valid choice...')
        time.sleep(2)
        delete_multiple_records()

def create_tables():  # Function to create tables
    os.system('clear')
    table_name = input("Enter a name for the table you want to create:              ")
    number_of_columns = int(input("How many columns will the table have?                       "))
    columns = []

    for i in range(number_of_columns):
        column_name = input(f"Enter the name of column {i + 1}:                                 ")
        column_type = input(f"Enter a data type for column '{column_name}' [TEXT, INTEGER, etc]:  ")
        columns.append(f"{column_name} {column_type}")

    columns_definition = ",\n        ".join(columns)

    create_a_table = f'''
    CREATE TABLE IF NOT EXISTS {table_name} (
        {columns_definition}
    );
    '''

    try:
        interact_with_database.execute(create_a_table)
        database_link.commit()
        print(f"\nTable '{table_name}' created successfully.")
        go_to_menu()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

def display_existing_tables():  # Function to display existing tables
    interact_with_database.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = interact_with_database.fetchall()

    tables = [table[0] for table in tables if table[0] != 'sqlite_sequence']

    predefined_order = ['Crimes', 'Evidence', 'Officers', 'Suspects']

    # Sort tables based on the predefined order, with others appearing afterward (chatgpt helped, didnt know this code was a thing)
    sorted_tables = sorted(tables, key=lambda x: (predefined_order.index(x) if x in predefined_order else len(predefined_order)))

    # Append "(not working)" to all tables after 'Suspects'
    suspect_index = sorted_tables.index('Suspects') if 'Suspects' in sorted_tables else len(sorted_tables)
    for i in range(suspect_index + 1, len(sorted_tables)):
        sorted_tables[i] += ' [not working]'

    sorted_tables.append('Back to main menu') #we add this option to the end of the list so we can use it

    for index, table in enumerate(sorted_tables, start=1): #we print the list of table names +back option on the screen with an index (1-5)
        print(f"{index}. {table}")

    return sorted_tables #we return a list of 5 elements and theirt index on the screen

def delete_tables():  # Function to delete tables
    os.system('clear')

    sorted_tables = display_existing_tables()

    table_choice = input('\nChoose a table you wish to delete [number / item name] or "back" to return: ').strip().capitalize()

    if table_choice.lower() == 'back':
        main_menu()
        return

    try:
        table_index = int(table_choice) - 1
        if 0 <= table_index < len(sorted_tables):
            table_choice = sorted_tables[table_index]
        else:
            raise ValueError
    except ValueError:
        matching_table = next((table for table in sorted_tables if table.lower() == table_choice.lower()), None)
        if matching_table:
            table_choice = matching_table
        else:
            print('Please enter a valid choice...')
            time.sleep(2)
            delete_tables()
            return

    table_choice = table_choice.replace("[not working]", "")

    if table_choice.capitalize() == 'Back to main menu':
        main_menu()
    else:
        deleting_function(table_choice)

def deleting_function(table_choice):
    os.system('clear')
    delete_confirmation()
    try:
        interact_with_database.execute(f'DROP TABLE IF EXISTS {table_choice}')
        database_link.commit()  # Commit the deletion to the database
        print(f"\nTable '{table_choice}' deleted.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    go_to_menu()

def delete_confirmation():
    answer = input('\nAre you sure you want to delete this? (yes/no) \n')
    while True:
        if answer.lower() in ['yes', 'y']:
            database_link.commit()
            break
        elif answer.lower() in ['no', 'n']:
            print('\nOperation cancelled, going to main menu...')
            wait_and_clear()
            main_menu()
        else:
            print('Enter a valid option...')
            wait_and_clear()
            delete_confirmation()

main_menu()  # Start the program with the main menu

database_link.close()