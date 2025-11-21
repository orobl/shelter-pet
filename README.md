# shelter-pet

Description:
Happy Paws Shelter Manager is a lightweight web application for managing an animal shelter. It allows staff to track animals, adoptions, employees, adopters, and health records while providing analytics and insights into shelter operations. The app is built using Flask, SQLite, and Bootstrap, making it easy to set up and use for small-to-medium shelters.

This project is intended as a demonstration / educational project, and includes a sample test user for login. 

Features
- Animal Management: Add, view, edit, and track animals in the shelter.
- Adoption Tracking: Record adoption events with dates and fees.
- Employee & Adopter Management: Keep track of employees and adopters.
- Health Records: Track vaccinations, spay/neuter procedures, and general health checks.
- Analytics Dashboard:
  - Monthly intakes vs. adoptions chart
  - Animal status distribution (pie chart)
  - Percentage of animals with completed health checks and spay/neuter
  - List of long-stay animals (20+ days)
- Authentication: Simple login/logout system to protect sensitive data.


shelter-pet/
├── app.py                      # Main Flask app
├── forms.py                    # 
├── shelter_database.db         # SQLite database with dummy data
├── templates/                  # HTML templates
└── README.md                   # Project documentation

Options for Improvement
- Implement stronger password hashing for production (bcrypt or argon2).
- Include user roles (admin, staff, adopters) with permission management.
- Include tracking system for health record followups
