# Personal Library Management

A simple web application to manage your personal book collection. Built with Node.js, Express, SQLite and vanilla HTML/CSS/JavaScript.

## Features

- Add and remove books
- Track users who borrow books
- Checkout and checkin books with due dates
- View current loans and overdue books
- Admin login with changeable password

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```
2. Start the server:
   ```bash
   npm start
   ```
3. Open `http://localhost:3000/login.html` in your browser and log in with:
   - **Username:** `admin`
   - **Password:** `tempPassword`
   After logging in you can change the password from the "Change Password" link.

The database is stored in `library.db` in the project directory.

## Barcode Scanning

For scanning ISBN barcodes, you can integrate a JavaScript library like [QuaggaJS](https://serratus.github.io/quaggaJS/). Include the library in `index.html` and use it to populate the ISBN field when adding books.
