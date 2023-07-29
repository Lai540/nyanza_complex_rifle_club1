from flask import Flask, render_template, request, redirect, g, make_response
import sqlite3
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


app = Flask(__name__)

DATABASE = 'club_database.db'

# Helper function to get the database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Close the database connection at the end of each request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Create the members table if it doesn't exist
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS members (
                        Member_number INTEGER,
                        Member_full_Name TEXT NOT NULL,
                        Postal_address TEXT NULL,
                        Fc_no TEXT NULL,
                        ID_number INTEGER PRIMARY KEY,
                        County TEXT NOT NULL,
                        Telephone TEXT NULL,
                        Email TEXT NULL,
                        Membership_category TEXT NULL,
                        Spouse TEXT NOT NULL,
                        Spouse_contact TEXT NULL,
                        Company TEXT NOT NULL,
                        Employer TEXT NOT NULL,
                        Proposer TEXT NOT NULL
                        )''')
        db.commit()

# Initialize the database
init_db()

# Home page route
@app.route('/')
def home():
    return render_template('index.html')

# Add member route
@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        Member_number = request.form['Member_number']
        Member_full_Name = request.form['Member_full_Name']
        Postal_address = request.form['Postal_address']
        Fc_no = request.form['Fc_no']
        ID_number = request.form['ID_number']
        County = request.form['County']
        Telephone = request.form['Telephone']
        Email = request.form['Email']
        Membership_category = request.form['Membership_category']
        Spouse = request.form['Spouse']
        Spouse_contact = request.form['Spouse_contact']
        Company = request.form['Company']
        Employer = request.form['Employer']
        Proposer = request.form['Proposer']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO members (Member_number, Member_full_Name, Postal_address, Fc_no, ID_number, County, Telephone, Email, Membership_category, Spouse, Spouse_contact, Company, Employer, Proposer) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (Member_number, Member_full_Name, Postal_address, Fc_no, ID_number, County, Telephone, Email, Membership_category, Spouse, Spouse_contact, Company, Employer, Proposer))
        db.commit()

        return redirect('/members')

    return render_template('add_member.html')
# Update member route
@app.route('/update_member', methods=['GET', 'POST'])
def update_member():
    if request.method == 'POST':
        Member_number = request.form['Member_number']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM members WHERE Member_number=?", (Member_number,))
        member = cursor.fetchone()

        if member:
            return render_template('update_member.html', member=member)
        else:
            return "Member not found!"

    return render_template('index.html')

# Update member details route
@app.route('/update_member_details', methods=['POST'])
def update_member_details():
    Member_number = request.form['Member_number']
    Member_full_Name = request.form['Member_full_Name']
    Postal_address = request.form['Postal_address']
    Fc_no = request.form['Fc_no']
    ID_number = request.form['ID_number']
    County = request.form['County']
    Telephone = request.form['Telephone']
    Email = request.form['Email']
    Membership_category = request.form['Membership_category']
    Spouse = request.form['Spouse']
    Spouse_contact = request.form['Spouse_contact']
    Company = request.form['Company']
    Employer = request.form['Employer']
    Proposer = request.form['Proposer']

    db = get_db()
    cursor = db.cursor()

    cursor.execute("UPDATE members SET Member_full_Name=?, Postal_address=?, Fc_no=?, ID_number=?, County=?, Telephone=?, Email=?, Membership_category=?, Spouse=?, Spouse_contact=?, Company=?, Employer = ?, Proposer=? WHERE Member_number=?", (Member_full_Name, Postal_address, Fc_no, ID_number, County, Telephone, Email, Membership_category, Spouse, Spouse_contact, Company, Employer, Proposer, Member_number))
    db.commit()

    return redirect('/members')
# View members route
@app.route('/members')
def view_members():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()
    return render_template('view_members.html', members=members)

# View member details by ID route
@app.route('/member_details', methods=['GET'])
def member_details():
    Member_number = request.args.get('Member_number')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM members WHERE Member_number=?", (Member_number,))
    member = cursor.fetchone()

    if member:
        return render_template('view_member.html', member=member)
    else:
        return "Member not found!"

# Remove member route
@app.route('/remove_member/<int:ID_number>')
def remove_member(ID_number):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM members WHERE ID_number =?", (ID_number,))
    db.commit()

    return redirect('/members')

# Print all members as PDF
@app.route('/print_members')
def print_members():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM members")
    members = cursor.fetchall()

    # Generate PDF using ReportLab
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    line_height = 30  # Set the desired line height

    page_height = 700  # Height limit for each page
    current_y = page_height - line_height  # Starting position
    member_number = 1  # Member number counter

    for member in members:
        # Calculate remaining space on the current page
        remaining_space = current_y - line_height

        if remaining_space < line_height * 14:  # Check if there's enough space for the next member
            c.showPage()  # Start a new page
            current_y = page_height - line_height  # Reset the vertical position

        # Add content to the PDF
        c.drawString(180, 700, "Nyanza Complex Rifle Club List of All Members:")
        c.drawString(20, current_y, f"At position {member_number}:")
        c.drawString(120, current_y, "Member Number:")
        c.drawString(380, current_y, str(member[0]))

        c.drawString(120, current_y - line_height, "Name:")
        c.drawString(380, current_y - line_height, member[1])

        c.drawString(120, current_y - line_height * 2, "Postal Address:")
        c.drawString(380, current_y - line_height * 2, member[2])

        c.drawString(120, current_y - line_height * 3, "FC NO:")
        c.drawString(380, current_y - line_height * 3, member[3])

        c.drawString(120, current_y - line_height * 4, "ID NUMBER:")
        c.drawString(380, current_y - line_height * 4, str(member[4]))

        c.drawString(120, current_y - line_height * 5, "County:")
        c.drawString(380, current_y - line_height * 5, member[5])

        c.drawString(120, current_y - line_height * 6, "Telephone:")
        c.drawString(380, current_y - line_height * 6, member[6])

        c.drawString(120, current_y - line_height * 7, "Email:")
        c.drawString(380, current_y - line_height * 7, member[7])

        c.drawString(120, current_y - line_height * 8, "Membership Category:")
        c.drawString(380, current_y - line_height * 8, member[8])

        c.drawString(120, current_y - line_height * 9, "Spouse:")
        c.drawString(380, current_y - line_height * 9, member[9])

        c.drawString(120, current_y - line_height * 10, "Spouse Contact:")
        c.drawString(380, current_y - line_height * 10, member[10])

        c.drawString(120, current_y - line_height * 11, "Company Name:")
        c.drawString(380, current_y - line_height * 11, member[11])

        c.drawString(120, current_y - line_height * 12, "Employer:")
        c.drawString(380, current_y - line_height * 12, member[12])

        c.drawString(120, current_y - line_height * 13, "Proposer:")
        c.drawString(380, current_y - line_height * 13, member[13])

        c.drawString(20, 30, "Approved and signed by: ..................................         Date: ..../..../......")

        current_y -= line_height * 15  # Adjust the spacing as desired
        member_number += 1  # Increment the member number

    c.showPage()
    c.save()

    # Get the PDF content from the buffer
    pdf = buffer.getvalue()
    buffer.close()

    # Create a response with the PDF content
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=members.pdf'

    return response

# Print a single member as PDF
@app.route('/print_member', methods=['GET'])
def print_member():
    Member_number = request.args.get('Member_number')

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM members WHERE Member_number=?", (Member_number,))
    member = cursor.fetchone()

    if member:
        # Generate PDF using ReportLab
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)


        # Add content to the PDF
        c.drawString(180, 700, "Nyanza Complex Rifle Club Member Details:")
        c.drawString(100, 660, f"Member Number:     {member[0]}")
        c.drawString(100, 620, f"Name:     {member[1]}")
        c.drawString(100, 580, f"Postal Address:     {member[2]}")
        c.drawString(100, 540, f"FC NO:     {member[3]}")
        c.drawString(100, 500, f"ID NUMBER:     {member[4]}")
        c.drawString(100, 460, f"County:     {member[5]}")
        c.drawString(100, 420, f"Telephone:     {member[6]}")
        c.drawString(100, 380, f"Email:     {member[7]}")
        c.drawString(100, 340, f"Membership_category:     {member[8]}")
        c.drawString(100, 300, f"Spouse:     {member[9]}")
        c.drawString(100, 260, f"Spouse contact:     {member[10]}")
        c.drawString(100, 220, f"Company Name:     {member[11]}")
        c.drawString(100, 180, f"Employer:     {member[12]}")
        c.drawString(100, 140, f"Proposer:     {member[13]}")
        c.drawString(20, 50, "Approved and signed by: ................         Date: ../../....")

        c.showPage()
        c.save()

        # Get the PDF content from the buffer
        pdf = buffer.getvalue()
        buffer.close()

        # Create a response with the PDF content
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'attachment; filename=member.pdf'

        return response
    else:
        return "Member not found!"


# Home page
@app.route('/home')
def homepage():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
