const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');
const db = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));

// Books
app.get('/api/books', (req, res) => {
  db.all('SELECT * FROM books', [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

app.post('/api/books', (req, res) => {
  const { title, author, isbn } = req.body;
  db.run(
    'INSERT INTO books (title, author, isbn) VALUES (?, ?, ?)',
    [title, author, isbn],
    function(err) {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ id: this.lastID });
    }
  );
});

app.delete('/api/books/:id', (req, res) => {
  db.run('DELETE FROM books WHERE id = ?', [req.params.id], function(err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ changes: this.changes });
  });
});

// Users
app.get('/api/users', (req, res) => {
  db.all('SELECT * FROM users', [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

app.post('/api/users', (req, res) => {
  const { name, email, phone } = req.body;
  db.run(
    'INSERT INTO users (name, email, phone) VALUES (?, ?, ?)',
    [name, email, phone],
    function(err) {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ id: this.lastID });
    }
  );
});

app.get('/api/users/:id', (req, res) => {
  db.get('SELECT * FROM users WHERE id = ?', [req.params.id], (err, row) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(row || {});
  });
});

app.put('/api/users/:id', (req, res) => {
  const { name, email, phone } = req.body;
  db.run(
    'UPDATE users SET name = ?, email = ?, phone = ? WHERE id = ?',
    [name, email, phone, req.params.id],
    function(err) {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ changes: this.changes });
    }
  );
});

// Checkout
app.post('/api/checkout', (req, res) => {
  const { book_id, user_id, due_date } = req.body;
  const dateNow = new Date().toISOString();
  db.run(
    'INSERT INTO loans (book_id, user_id, checkout_date, due_date) VALUES (?, ?, ?, ?)',
    [book_id, user_id, dateNow, due_date],
    function(err) {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ id: this.lastID });
    }
  );
});

app.post('/api/checkin', (req, res) => {
  const { book_id } = req.body;
  const dateNow = new Date().toISOString();
  db.run(
    'UPDATE loans SET return_date = ? WHERE book_id = ? AND return_date IS NULL',
    [dateNow, book_id],
    function(err) {
      if (err) return res.status(500).json({ error: err.message });
      res.json({ changes: this.changes });
    }
  );
});

// Loans
app.get('/api/loans', (req, res) => {
  db.all(
    `SELECT loans.*, books.title, users.name as user_name
     FROM loans
     JOIN books ON loans.book_id = books.id
     JOIN users ON loans.user_id = users.id`,
    [],
    (err, rows) => {
      if (err) return res.status(500).json({ error: err.message });
      res.json(rows);
    }
  );
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
