import sqlite3

# Global variable
book_counter = 1
reservation_counter = 1
user_counter = 1


def connect_db():
    return sqlite3.connect('library.db')


# Create the database with three tables
def create_tables():
    with connect_db() as conn:
        c = conn.cursor()
        # Create the Books table
        c.execute('''CREATE TABLE IF NOT EXISTS Books (
                                BookID TEXT PRIMARY KEY,
                                Title TEXT,
                                Author TEXT,
                                ISBN TEXT,
                                Status TEXT
                            )''')

        # Create the Users table
        c.execute('''CREATE TABLE IF NOT EXISTS Users (
                                UserID TEXT PRIMARY KEY,
                                Name TEXT,
                                Email TEXT
                            )''')

        # Create the Reservations table
        c.execute('''CREATE TABLE IF NOT EXISTS Reservations (
                                ReservationID TEXT PRIMARY KEY,
                                BookID TEXT,
                                UserID TEXT,
                                ReservationDate TEXT,
                                FOREIGN KEY (BookID) REFERENCES Books (BookID),
                                FOREIGN KEY (UserID) REFERENCES Users (UserID)
                            )''')


# Add a new book to the database
def add_book():
    global book_counter
    title = input("Enter book title: ")
    author = input("Enter book author: ")
    isbn = input("Enter book ISBN: ")
    status = input("Enter book status(available or unavailable): ")
    book_id = f'LB{book_counter}'
    book_counter += 1

    with connect_db() as conn:
        c = conn.cursor()
        c.execute('''
                   INSERT INTO Books (BookID, Title, Author, ISBN, Status)
                   VALUES (?, ?, ?, ?, ?)
                   ''', (book_id, title, author, isbn, status))
        print(f'Book {book_id} added successfully.')


# Find a book's detail based on BookID
def find_book_detail():
    book_id = input("Enter the BookID: ")
    with connect_db() as conn:
        c = conn.cursor()
        # find details from Books table
        c.execute("SELECT * FROM Books WHERE BookID=?", (book_id,))
        book_info = c.fetchone()
        if book_info:
            print("Search Result:")
            print("Book ID:", book_info[0])
            print("Title:", book_info[1])
            print("Author:", book_info[2])
            print("ISBN:", book_info[3])
            print("Status:", book_info[4])
        else:
            print(f'BookID {book_id} not found. Please enter a valid BookID.')

        # find details from Reservations table
        c.execute(
            "SELECT * FROM Reservations WHERE BookID=?", (book_id,))
        reservations = c.fetchall()
        if reservations:
            for reservation_info in reservations:
                user_id = reservation_info[2]
                print("Reservation ID:", reservation_info[0])
                print("Reservation Date:", reservation_info[3])

            # find details from Users table
            c.execute("SELECT u.UserID, u.Name, u.Email FROM Users u JOIN Reservations r ON r.UserID = u.UserID "
                      "WHERE r.UserID = ?", (user_id,))
            users = c.fetchall()
            if users:
                for user_info in users:
                    print("User ID:", user_info[0])
                    print("Name:", user_info[1])
                    print("Email:", user_info[2])
            else:
                print("no user information.")
        else:
            print("Reservation: Not reserved.")


# Find a book's reservation status based on BookID, Title, UserID, and ReservationID
def find_reservation_status():
    input_text = input("Enter the BookID(LB), Title, UserID(LU), or ReservationID(LR): ")
    with connect_db() as conn:
        c = conn.cursor()
        if input_text.startswith("LB"):
            # Search by BookID
            c.execute("SELECT Status FROM Books WHERE BookID=?", (input_text,))
            status = c.fetchone()
            if status:
                print("Reservation Status:", status[0])
            else:
                print("Book not found in the database.")
        elif input_text.startswith("LU"):
            # Search by UserID
            c.execute("SELECT b.Status FROM Books b JOIN Reservations r ON b.BookID=r.BookID WHERE r.UserID=?",
                      (input_text,))
            status = c.fetchone()
            if status:
                print("Reservation Status:", status[0])
            else:
                print("User not found in the database.")
        elif input_text.startswith("LR"):
            # Search by ReservationID
            c.execute("SELECT b.Status FROM Books b JOIN Reservations r ON b.BookID=r.BookID WHERE r.ReservationID=?",
                      (input_text,))
            status = c.fetchone()
            if status:
                print("Reservation Status:", status[0])
            else:
                print("Reservation not found in the database.")
        else:
            # Search by Title
            c.execute("SELECT b.Status FROM Books b WHERE b.Title=?", (input_text,))
            status = c.fetchone()
            if status:
                print("Reservation Status:", status[0])
            else:
                print("Book not found in the database.")


# Find all the books in the database
def find_all_books():
    with connect_db() as conn:
        c = conn.cursor()
        # Find book details from Books table
        c.execute("SELECT * FROM Books")
        books = c.fetchall()
        for book in books:
            book_id = book[0]
            print("Book ID:", book_id)
            print("Title:", book[1])
            print("Author:", book[2])
            print("ISBN:", book[3])
            print("Status:", book[4])
            # Find reservation details and user details from Reservations and Users table
        c.execute(
            "SELECT * FROM Reservations WHERE BookID=?", (book_id,))
        reservations = c.fetchall()
        if reservations:
            for reservation_info in reservations:
                print("Reservation ID:", reservation_info[0])
                print("Reservation Date:", reservation_info[3])
        else:
            print("Reservation: Not reserved.")


# Modify/update book details based on its BookID
def update_book():
    with connect_db() as conn:
        global reservation_counter
        c = conn.cursor()
        while True:
            book_id = input("Enter BookID: ")
            c.execute("SELECT * FROM Books WHERE BookID=?", (book_id,))
            book_exists = c.fetchone() is not None
            if not book_exists:
                print(f'BookID {book_id} not found. Please enter a valid BookID.')
                if input("Do you want to quit? (y/n): ").lower() == 'y':
                    return
                print('Continuing...')
            else:
                break
        title = input("Enter new title (or press Enter to keep the old): ")
        author = input("Enter new author (or press Enter to keep the old): ")
        isbn = input("Enter new ISBN (or press Enter to keep the old): ")
        c.execute("UPDATE Books SET Title=?, Author=?, ISBN=? WHERE BookID=?", (title, author, isbn, book_id))
        conn.commit()
        status = input("Enter new status (available/unavailable): ")
        while status.lower() not in ['available', 'unavailable']:
            print("Invalid status entered. Please enter 'available' or 'unavailable'.")
            status = input("Enter new status (available/unavailable): ")
        if status.lower() == 'available':
            c.execute("UPDATE Books SET Status=? WHERE BookID=?", (status.lower(), book_id))
        elif status.lower() == 'unavailable':
            c.execute("UPDATE Books SET Status=? WHERE BookID=?", (status.lower(), book_id))
            reservation_id = f'LR{reservation_counter}'
            reservation_counter += 1
            reservation_date = input("Enter Reservation Date (format: YYYY-MM-DD): ")
            c.execute("INSERT INTO Reservations (ReservationID, ReservationDate, BookID) VALUES (?, ?, ?)",
                      (reservation_id, reservation_date, book_id))
        conn.commit()
        print(f'Book {book_id} updated successfully.')


# Delete a book based on its BookID
def delete_book():
    book_id = input("Enter the BookID: ")
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    # Check if the book_id exists in the database
    c.execute("SELECT * FROM Books WHERE BookID=?", (book_id,))
    book_exists = c.fetchone()
    if not book_exists:
        print(f'BookID {book_id} not found. Please enter a valid BookID.')
        conn.close()
        return
    # Check if the book is reserved
    c.execute("SELECT * FROM Reservations WHERE BookID=?", (book_id,))
    reservation = c.fetchone()
    if reservation:

        # Delete book from Reservations table
        c.execute("DELETE FROM Reservations WHERE BookID=?", (book_id,))
    # Delete book from Books table
    c.execute("DELETE FROM Books WHERE BookID=?", (book_id,))
    print(f'Book {book_id} deleted successfully.')
    conn.commit()
    conn.close()


def main():
    create_tables()
    while True:
        print("------welcome to library management system------")
        print("1. Add a new book")
        print("2. Find a book's detail based on BookID")
        print("3. Find a book's reservation status based on BookID, Title, UserID, and ReservationID")
        print("4. Find all the books in the database")
        print("5. Modify/update book details based on its BookID")
        print("6. Delete a book based on its BookID")
        print("7. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            add_book()
        elif choice == '2':
            find_book_detail()
        elif choice == '3':
            find_reservation_status()
        elif choice == '4':
            find_all_books()
        elif choice == '5':
            update_book()
        elif choice == '6':
            delete_book()
        elif choice == '7':
            print("Exiting the program...")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
