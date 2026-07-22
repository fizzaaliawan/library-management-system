import click
from tabulate import tabulate
from datetime import datetime, timedelta
import uuid
import sys
import os

# Set Python path to include parent directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from cli.src.db import SessionLocal
from cli.src.models import User, Member, Book, Loan

# Helper function to get database session
def get_db_session():
    return SessionLocal()

@click.group()
def cli():
    """Library Management System CLI (Phase 1)"""
    pass

# ==================== BOOK COMMANDS ====================

@cli.group(name="book")
def book_group():
    """Manage Books"""
    pass

@book_group.command(name="add")
@click.option("--title", required=True, help="Title of the book")
@click.option("--author", required=True, help="Author of the book")
@click.option("--isbn", required=True, help="ISBN unique identifier")
@click.option("--genre", help="Genre of the book")
@click.option("--copies", default=1, type=int, help="Total number of copies")
def add_book(title, author, isbn, genre, copies):
    """Add a new book to the library"""
    db = get_db_session()
    try:
        # Check if active book with same ISBN exists
        existing = db.query(Book).filter(Book.isbn == isbn, Book.is_deleted == False).first()
        if existing:
            click.echo(f"Error: An active book with ISBN {isbn} already exists ('{existing.title}').")
            return
        
        # Check if there is a soft-deleted book with same ISBN to restore or alert
        deleted_book = db.query(Book).filter(Book.isbn == isbn, Book.is_deleted == True).first()
        if deleted_book:
            deleted_book.is_deleted = False
            deleted_book.deleted_at = None
            deleted_book.title = title
            deleted_book.author = author
            deleted_book.genre = genre
            deleted_book.total_copies = copies
            deleted_book.available_copies = copies
            db.commit()
            click.echo(f"Restored previously soft-deleted book: '{title}' by {author} (ISBN: {isbn}).")
            return

        new_book = Book(
            title=title,
            author=author,
            isbn=isbn,
            genre=genre,
            total_copies=copies,
            available_copies=copies
        )
        db.add(new_book)
        db.commit()
        click.echo(f"Successfully added book: '{title}' by {author} (ISBN: {isbn}) with {copies} copies.")
    except Exception as e:
        db.rollback()
        click.echo(f"Error adding book: {e}")
    finally:
        db.close()

@book_group.command(name="list")
def list_books():
    """List all active books in the library"""
    db = get_db_session()
    try:
        books = db.query(Book).filter(Book.is_deleted == False).all()
        if not books:
            click.echo("No active books found in the library.")
            return

        headers = ["ID", "Title", "Author", "ISBN", "Genre", "Total", "Available"]
        data = [[str(b.id), b.title, b.author, b.isbn, b.genre or "N/A", b.total_copies, b.available_copies] for b in books]
        click.echo(tabulate(data, headers=headers, tablefmt="grid"))
    except Exception as e:
        click.echo(f"Error listing books: {e}")
    finally:
        db.close()

@book_group.command(name="search")
@click.argument("query")
def search_books(query):
    """Search books by title, author, or ISBN"""
    db = get_db_session()
    try:
        books = db.query(Book).filter(
            Book.is_deleted == False,
            (Book.title.ilike(f"%{query}%") | 
             Book.author.ilike(f"%{query}%") | 
             Book.isbn.ilike(f"%{query}%"))
        ).all()
        
        if not books:
            click.echo(f"No books found matching '{query}'.")
            return

        headers = ["ID", "Title", "Author", "ISBN", "Genre", "Total", "Available"]
        data = [[str(b.id), b.title, b.author, b.isbn, b.genre or "N/A", b.total_copies, b.available_copies] for b in books]
        click.echo(tabulate(data, headers=headers, tablefmt="grid"))
    except Exception as e:
        click.echo(f"Error searching books: {e}")
    finally:
        db.close()

@book_group.command(name="update")
@click.option("--isbn", required=True, help="ISBN of the book to update")
@click.option("--title", help="New title of the book")
@click.option("--author", help="New author of the book")
@click.option("--genre", help="New genre of the book")
@click.option("--copies", type=int, help="New total copies")
def update_book(isbn, title, author, genre, copies):
    """Update details of an existing book"""
    db = get_db_session()
    try:
        book = db.query(Book).filter(Book.isbn == isbn, Book.is_deleted == False).first()
        if not book:
            click.echo(f"Error: Active book with ISBN {isbn} not found.")
            return

        if title:
            book.title = title
        if author:
            book.author = author
        if genre:
            book.genre = genre
        if copies is not None:
            # Check availability logic
            borrowed_copies = book.total_copies - book.available_copies
            if copies < borrowed_copies:
                click.echo(f"Error: Cannot set total copies to {copies} because {borrowed_copies} copies are currently borrowed.")
                return
            book.total_copies = copies
            book.available_copies = copies - borrowed_copies

        db.commit()
        click.echo(f"Successfully updated book (ISBN: {isbn}).")
    except Exception as e:
        db.rollback()
        click.echo(f"Error updating book: {e}")
    finally:
        db.close()

@book_group.command(name="delete")
@click.option("--isbn", required=True, help="ISBN of the book to soft-delete")
def delete_book(isbn):
    """Soft delete a book"""
    db = get_db_session()
    try:
        book = db.query(Book).filter(Book.isbn == isbn, Book.is_deleted == False).first()
        if not book:
            click.echo(f"Error: Active book with ISBN {isbn} not found.")
            return

        # Check if there are active loans
        active_loans = db.query(Loan).filter(Loan.book_id == book.id, Loan.status == "Active").count()
        if active_loans > 0:
            click.echo(f"Error: Cannot delete book because there are {active_loans} active loans for it.")
            return

        book.is_deleted = True
        book.deleted_at = datetime.utcnow()
        db.commit()
        click.echo(f"Successfully soft-deleted book '{book.title}' (ISBN: {isbn}).")
    except Exception as e:
        db.rollback()
        click.echo(f"Error deleting book: {e}")
    finally:
        db.close()


# ==================== MEMBER COMMANDS ====================

@cli.group(name="member")
def member_group():
    """Manage Members"""
    pass

@member_group.command(name="register")
@click.option("--first-name", required=True, help="First name of the member")
@click.option("--last-name", required=True, help="Last name of the member")
@click.option("--email", required=True, help="Email address of the member")
@click.option("--phone", help="Phone number of the member")
def register_member(first_name, last_name, email, phone):
    """Register a new member (creates user & member records)"""
    db = get_db_session()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email, User.is_deleted == False).first()
        if existing_user:
            click.echo(f"Error: Active user with email {email} already registered.")
            return

        # Restore soft-deleted user/member if exists
        deleted_user = db.query(User).filter(User.email == email, User.is_deleted == True).first()
        if deleted_user:
            deleted_user.is_deleted = False
            deleted_user.deleted_at = None
            
            # Check associated member
            member = db.query(Member).filter(Member.user_id == deleted_user.id).first()
            if member:
                member.is_deleted = False
                member.first_name = first_name
                member.last_name = last_name
                member.phone = phone
                member.is_active = True
            db.commit()
            click.echo(f"Restored previously soft-deleted member: {first_name} {last_name} ({email}).")
            return

        # Create user record with default mock password
        import hashlib
        dummy_hashed = hashlib.sha256(b"member123").hexdigest()
        
        new_user = User(
            email=email,
            hashed_password=dummy_hashed,
            role="Member",
            is_active=True
        )
        db.add(new_user)
        db.flush() # flush to get user id

        # Generate unique membership number
        membership_no = f"MEM-{datetime.utcnow().year}-{str(uuid.uuid4())[:8].upper()}"

        new_member = Member(
            user_id=new_user.id,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            membership_number=membership_no,
            is_active=True
        )
        db.add(new_member)
        db.commit()
        click.echo(f"Successfully registered member: {first_name} {last_name}")
        click.echo(f"Email: {email} | Membership Number: {membership_no}")
    except Exception as e:
        db.rollback()
        click.echo(f"Error registering member: {e}")
    finally:
        db.close()

@member_group.command(name="list")
def list_members():
    """List all registered members"""
    db = get_db_session()
    try:
        members = db.query(Member).join(User).filter(Member.is_deleted == False).all()
        if not members:
            click.echo("No registered members found.")
            return

        headers = ["ID", "Name", "Email", "Phone", "Membership No.", "Active"]
        data = [[
            str(m.id), 
            f"{m.first_name} {m.last_name}", 
            m.user.email, 
            m.phone or "N/A", 
            m.membership_number, 
            "Yes" if m.is_active else "No"
        ] for m in members]
        click.echo(tabulate(data, headers=headers, tablefmt="grid"))
    except Exception as e:
        click.echo(f"Error listing members: {e}")
    finally:
        db.close()

@member_group.command(name="search")
@click.argument("query")
def search_members(query):
    """Search members by name, email, or membership number"""
    db = get_db_session()
    try:
        members = db.query(Member).join(User).filter(
            Member.is_deleted == False,
            (Member.first_name.ilike(f"%{query}%") |
             Member.last_name.ilike(f"%{query}%") |
             Member.membership_number.ilike(f"%{query}%") |
             User.email.ilike(f"%{query}%"))
        ).all()

        if not members:
            click.echo(f"No members found matching '{query}'.")
            return

        headers = ["ID", "Name", "Email", "Phone", "Membership No.", "Active"]
        data = [[
            str(m.id), 
            f"{m.first_name} {m.last_name}", 
            m.user.email, 
            m.phone or "N/A", 
            m.membership_number, 
            "Yes" if m.is_active else "No"
        ] for m in members]
        click.echo(tabulate(data, headers=headers, tablefmt="grid"))
    except Exception as e:
        click.echo(f"Error searching members: {e}")
    finally:
        db.close()

@member_group.command(name="update")
@click.option("--email", required=True, help="Email of the member to update")
@click.option("--first-name", help="New first name")
@click.option("--last-name", help="New last name")
@click.option("--phone", help="New phone number")
@click.option("--active", type=bool, help="Set active status (true/false)")
def update_member(email, first_name, last_name, phone, active):
    """Update details of an existing member"""
    db = get_db_session()
    try:
        user = db.query(User).filter(User.email == email, User.is_deleted == False).first()
        if not user or not user.member:
            click.echo(f"Error: Active member with email {email} not found.")
            return

        member = user.member
        if first_name:
            member.first_name = first_name
        if last_name:
            member.last_name = last_name
        if phone:
            member.phone = phone
        if active is not None:
            member.is_active = active

        db.commit()
        click.echo(f"Successfully updated member {email}.")
    except Exception as e:
        db.rollback()
        click.echo(f"Error updating member: {e}")
    finally:
        db.close()


# ==================== LOAN COMMANDS ====================

@cli.group(name="loan")
def loan_group():
    """Manage Book Loans"""
    pass

@loan_group.command(name="borrow")
@click.option("--member-email", required=True, help="Email of the borrowing member")
@click.option("--isbn", required=True, help="ISBN of the book to borrow")
@click.option("--days", default=14, type=int, help="Borrow duration in days (default: 14)")
def borrow_book(member_email, isbn, days):
    """Borrow a book for a member"""
    db = get_db_session()
    try:
        # Check member
        user = db.query(User).filter(User.email == member_email, User.is_deleted == False).first()
        if not user or not user.member:
            click.echo(f"Error: Member with email {member_email} not found.")
            return
        member = user.member
        if not member.is_active:
            click.echo("Error: Member membership is currently inactive.")
            return

        # Check book
        book = db.query(Book).filter(Book.isbn == isbn, Book.is_deleted == False).first()
        if not book:
            click.echo(f"Error: Book with ISBN {isbn} not found.")
            return
        if book.available_copies <= 0:
            click.echo(f"Error: Book '{book.title}' has no copies available for borrowing.")
            return

        # Check if user already has an active loan of this book
        existing_loan = db.query(Loan).filter(
            Loan.member_id == member.id, 
            Loan.book_id == book.id, 
            Loan.status.in_(["Active", "Overdue"])
        ).first()
        if existing_loan:
            click.echo(f"Error: Member has already borrowed this book and has not returned it yet.")
            return

        # Register loan
        borrow_date = datetime.utcnow()
        due_date = borrow_date + timedelta(days=days)
        
        new_loan = Loan(
            book_id=book.id,
            member_id=member.id,
            borrow_date=borrow_date,
            due_date=due_date,
            status="Active"
        )
        db.add(new_loan)

        # Update available copies
        book.available_copies -= 1
        db.commit()

        click.echo(f"Successfully checked out '{book.title}' to {member.first_name} {member.last_name}.")
        click.echo(f"Due date: {due_date.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        db.rollback()
        click.echo(f"Error borrowing book: {e}")
    finally:
        db.close()

@loan_group.command(name="return")
@click.option("--member-email", required=True, help="Email of the borrowing member")
@click.option("--isbn", required=True, help="ISBN of the book to return")
def return_book(member_email, isbn):
    """Return a borrowed book"""
    db = get_db_session()
    try:
        # Check member
        user = db.query(User).filter(User.email == member_email, User.is_deleted == False).first()
        if not user or not user.member:
            click.echo(f"Error: Member with email {member_email} not found.")
            return
        member = user.member

        # Check book
        book = db.query(Book).filter(Book.isbn == isbn, Book.is_deleted == False).first()
        if not book:
            click.echo(f"Error: Book with ISBN {isbn} not found.")
            return

        # Find active/overdue loan
        loan = db.query(Loan).filter(
            Loan.member_id == member.id,
            Loan.book_id == book.id,
            Loan.status.in_(["Active", "Overdue"])
        ).first()
        
        if not loan:
            click.echo(f"Error: No active loan found for '{book.title}' by member {member_email}.")
            return

        # Update loan details
        loan.return_date = datetime.utcnow()
        loan.status = "Returned"
        
        # Increase copies
        book.available_copies += 1
        db.commit()
        click.echo(f"Successfully returned '{book.title}' from {member.first_name} {member.last_name}.")
    except Exception as e:
        db.rollback()
        click.echo(f"Error returning book: {e}")
    finally:
        db.close()

@loan_group.command(name="history")
@click.option("--member-email", help="Filter by member email")
@click.option("--isbn", help="Filter by book ISBN")
def loan_history(member_email, isbn):
    """View loan history with optional filters"""
    db = get_db_session()
    try:
        query = db.query(Loan).join(Book).join(Member).join(User)
        
        if member_email:
            query = query.filter(User.email == member_email)
        if isbn:
            query = query.filter(Book.isbn == isbn)
            
        loans = query.order_by(Loan.borrow_date.desc()).all()
        if not loans:
            click.echo("No loans history matches the criteria.")
            return

        headers = ["Member Email", "Book Title", "ISBN", "Borrow Date", "Due Date", "Return Date", "Status"]
        data = []
        for l in loans:
            ret_date = l.return_date.strftime('%Y-%m-%d %H:%M') if l.return_date else "Pending"
            data.append([
                l.member.user.email,
                l.book.title,
                l.book.isbn,
                l.borrow_date.strftime('%Y-%m-%d %H:%M'),
                l.due_date.strftime('%Y-%m-%d %H:%M'),
                ret_date,
                l.status
            ])
        click.echo(tabulate(data, headers=headers, tablefmt="grid"))
    except Exception as e:
        click.echo(f"Error loading loan history: {e}")
    finally:
        db.close()

@loan_group.command(name="active")
def active_loans():
    """List all active and overdue loans"""
    db = get_db_session()
    try:
        loans = db.query(Loan).join(Book).join(Member).join(User).filter(
            Loan.status.in_(["Active", "Overdue"])
        ).order_by(Loan.due_date.asc()).all()

        if not loans:
            click.echo("No active or overdue loans at this time.")
            return

        # Perform local update check for overdue state
        now = datetime.utcnow()
        updated_any = False
        for l in loans:
            if l.status == "Active" and now > l.due_date:
                l.status = "Overdue"
                updated_any = True
        if updated_any:
            db.commit()

        headers = ["Member Name", "Email", "Book Title", "ISBN", "Borrow Date", "Due Date", "Status"]
        data = [[
            f"{l.member.first_name} {l.member.last_name}",
            l.member.user.email,
            l.book.title,
            l.book.isbn,
            l.borrow_date.strftime('%Y-%m-%d %H:%M'),
            l.due_date.strftime('%Y-%m-%d %H:%M'),
            l.status
        ] for l in loans]
        click.echo(tabulate(data, headers=headers, tablefmt="grid"))
    except Exception as e:
        click.echo(f"Error checking active loans: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    cli()
