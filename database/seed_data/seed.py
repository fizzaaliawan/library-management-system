import os
import sys
import uuid
from datetime import datetime, timedelta

# Ensure python path includes root to import models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    from cli.src.db import SessionLocal
    from cli.src.models import User, Member, Book, Loan
except ImportError:
    print("Could not import models from cli.src. Please verify python path.")
    sys.exit(1)

def hash_password(password: str) -> str:
    try:
        import bcrypt
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    except ImportError:
        import hashlib
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

def seed_database():
    print("Starting database seeding...")
    db = SessionLocal()
    try:
        # Delete existing data in reverse order of dependencies
        db.query(Loan).delete()
        db.query(Member).delete()
        db.query(Book).delete()
        db.query(User).delete()
        db.commit()

        # Seed Users
        print("Seeding Users...")
        admin_user_id = uuid.uuid4()
        mem1_user_id = uuid.uuid4()
        mem2_user_id = uuid.uuid4()

        admin_user = User(
            id=admin_user_id,
            email="librarian@library.com",
            hashed_password=hash_password("admin123"),
            role="Librarian",
            is_active=True
        )
        db.add(admin_user)

        member_user1 = User(
            id=mem1_user_id,
            email="fizza@gmail.com",
            hashed_password=hash_password("member123"),
            role="Member",
            is_active=True
        )
        db.add(member_user1)

        member_user2 = User(
            id=mem2_user_id,
            email="jane.smith@example.com",
            hashed_password=hash_password("member123"),
            role="Member",
            is_active=True
        )
        db.add(member_user2)

        # Seed Members
        print("Seeding Members...")
        member1 = Member(
            user_id=mem1_user_id,
            first_name="Fizza",
            last_name="Ali",
            phone="555-0101",
            membership_number="MEM-2026-0001",
            is_active=True
        )
        db.add(member1)

        member2 = Member(
            user_id=mem2_user_id,
            first_name="Jane",
            last_name="Smith",
            phone="555-0102",
            membership_number="MEM-2026-0002",
            is_active=True
        )
        db.add(member2)

        # Seed Books
        print("Seeding Books...")
        book1 = Book(
            title="The Clean Coder",
            author="Robert C. Martin",
            isbn="9780137081073",
            genre="Software Engineering",
            total_copies=5,
            available_copies=4
        )
        db.add(book1)

        book2 = Book(
            title="Design Patterns",
            author="Erich Gamma, Richard Helm, Ralph Johnson, John Vlissides",
            isbn="9780201633610",
            genre="Software Architecture",
            total_copies=3,
            available_copies=3
        )
        db.add(book2)

        book3 = Book(
            title="Clean Architecture",
            author="Robert C. Martin",
            isbn="9780134494166",
            genre="Software Architecture",
            total_copies=4,
            available_copies=3
        )
        db.add(book3)

        book4 = Book(
            title="Refactoring",
            author="Martin Fowler",
            isbn="9780134757599",
            genre="Software Engineering",
            total_copies=2,
            available_copies=2
        )
        db.add(book4)

        # Additional seeded books for varied subjects
        book5 = Book(
            title="Introduction to Algorithms",
            author="Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein",
            isbn="9780262033848",
            genre="Computer Science",
            total_copies=4,
            available_copies=4
        )
        db.add(book5)

        book6 = Book(
            title="Structure and Interpretation of Computer Programs",
            author="Harold Abelson, Gerald Jay Sussman, Julie Sussman",
            isbn="9780262510875",
            genre="Computer Science",
            total_copies=2,
            available_copies=2
        )
        db.add(book6)

        book7 = Book(
            title="Calculus",
            author="Michael Spivak",
            isbn="9780914098911",
            genre="Mathematics",
            total_copies=3,
            available_copies=3
        )
        db.add(book7)

        book8 = Book(
            title="Linear Algebra Done Right",
            author="Sheldon Axler",
            isbn="9783319110790",
            genre="Mathematics",
            total_copies=5,
            available_copies=5
        )
        db.add(book8)

        book9 = Book(
            title="A Brief History of Time",
            author="Stephen Hawking",
            isbn="9780553380163",
            genre="Science",
            total_copies=6,
            available_copies=6
        )
        db.add(book9)

        book10 = Book(
            title="Cosmos",
            author="Carl Sagan",
            isbn="9780345331359",
            genre="Science",
            total_copies=4,
            available_copies=4
        )
        db.add(book10)

        book11 = Book(
            title="Sapiens: A Brief History of Humankind",
            author="Yuval Noah Harari",
            isbn="9780062316097",
            genre="History",
            total_copies=8,
            available_copies=8
        )
        db.add(book11)

        book12 = Book(
            title="The Guns of August",
            author="Barbara W. Tuchman",
            isbn="9780345386236",
            genre="History",
            total_copies=3,
            available_copies=3
        )
        db.add(book12)

        book13 = Book(
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            isbn="9780743273565",
            genre="Fiction",
            total_copies=10,
            available_copies=10
        )
        db.add(book13)

        book14 = Book(
            title="To Kill a Mockingbird",
            author="Harper Lee",
            isbn="9780446310789",
            genre="Fiction",
            total_copies=7,
            available_copies=7
        )
        db.add(book14)

        book15 = Book(
            title="1984",
            author="George Orwell",
            isbn="9780451524935",
            genre="Fiction",
            total_copies=9,
            available_copies=9
        )
        db.add(book15)

        book16 = Book(
            title="Steve Jobs",
            author="Walter Isaacson",
            isbn="9781451648539",
            genre="Biography",
            total_copies=5,
            available_copies=5
        )
        db.add(book16)

        book17 = Book(
            title="Einstein: His Life and Universe",
            author="Walter Isaacson",
            isbn="9780743274968",
            genre="Biography",
            total_copies=4,
            available_copies=4
        )
        db.add(book17)

        # Flush to get book/member references
        db.flush()

        # Seed Loans
        print("Seeding Loans...")
        # Active Loan (John Doe borrowed Clean Architecture)
        loan1 = Loan(
            book_id=book3.id,
            member_id=member1.id,
            borrow_date=datetime.utcnow() - timedelta(days=5),
            due_date=datetime.utcnow() + timedelta(days=9),
            status="Active"
        )
        db.add(loan1)

        # Overdue Loan (John Doe borrowed The Clean Coder 20 days ago, due 6 days ago)
        loan2 = Loan(
            book_id=book1.id,
            member_id=member1.id,
            borrow_date=datetime.utcnow() - timedelta(days=20),
            due_date=datetime.utcnow() - timedelta(days=6),
            status="Overdue"
        )
        db.add(loan2)

        # Returned Loan (Jane Smith borrowed and returned The Clean Coder)
        loan3 = Loan(
            book_id=book1.id,
            member_id=member2.id,
            borrow_date=datetime.utcnow() - timedelta(days=10),
            due_date=datetime.utcnow() + timedelta(days=4),
            return_date=datetime.utcnow() - timedelta(days=2),
            status="Returned"
        )
        db.add(loan3)

        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
