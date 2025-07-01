const express = require('express');
const bodyParser = require('body-parser');
const session = require('express-session');
const bcrypt = require('bcryptjs');
const path = require('path');
const db = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());
app.use(session({
  secret: 'library-secret',
  resave: false,
  saveUninitialized: false
}));

// Ensure accounts table and default admin
db.run(`CREATE TABLE IF NOT EXISTS accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE,
  password TEXT,
  is_admin INTEGER DEFAULT 0
)`);

db.get('SELECT COUNT(*) as count FROM accounts', (err, row) => {
  if (err) return;
  if (row.count === 0) {
    const hash = bcrypt.hashSync('tempPassword', 10);
    db.run('INSERT INTO accounts (username, password, is_admin) VALUES (?, ?, 1)', ['admin', hash]);
  }
});

// Authentication middleware
function requireAuth(req, res, next) {
  if (req.session.userId) return next();
  return res.status(401).json({ error: 'Unauthorized' });
}

// Redirect to login page if not authenticated
app.use((req, res, next) => {
  if (req.path.startsWith('/api') || req.path === '/login.html') return next();
  if (!req.session.userId && req.path.endsWith('.html')) {
    return res.redirect('/login.html');
  }
  next();
});

app.use(express.static(path.join(__dirname, 'public')));

// Login
app.post('/api/login', (req, res) => {
  const { username, password } = req.body;
  db.get('SELECT * FROM accounts WHERE username = ?', [username], (err, row) => {
    if (err || !row) return res.status(401).json({ error: 'Invalid credentials' });
    if (!bcrypt.compareSync(password, row.password)) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    req.session.userId = row.id;
    req.session.isAdmin = !!row.is_admin;
    res.json({ success: true });
  });
});

app.post('/api/logout', (req, res) => {
  req.session.destroy(() => {
    res.json({ success: true });
  });
});

app.post('/api/change-password', requireAuth, (req, res) => {
  const { oldPassword, newPassword } = req.body;
  db.get('SELECT password FROM accounts WHERE id = ?', [req.session.userId], (err, row) => {
    if (err || !row) return res.status(500).json({ error: 'Unexpected' });
    if (!bcrypt.compareSync(oldPassword, row.password)) {
      return res.status(400).json({ error: 'Old password incorrect' });
    }
    const hash = bcrypt.hashSync(newPassword, 10);
    db.run('UPDATE accounts SET password = ? WHERE id = ?', [hash, req.session.userId], function(err2) {
      if (err2) return res.status(500).json({ error: err2.message });
      res.json({ success: true });
    });
  });
});

// Books
app.get('/api/books', requireAuth, (req, res) => {
  db.all('SELECT * FROM books', [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

app.post('/api/books', requireAuth, (req, res) => {
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

app.delete('/api/books/:id', requireAuth, (req, res) => {
  db.run('DELETE FROM books WHERE id = ?', [req.params.id], function(err) {
    if (err) return res.status(500).json({ error: err.message });
    res.json({ changes: this.changes });
  });
});

// Users
app.get('/api/users', requireAuth, (req, res) => {
  db.all('SELECT * FROM users', [], (err, rows) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(rows);
  });
});

app.post('/api/users', requireAuth, (req, res) => {
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

app.get('/api/users/:id', requireAuth, (req, res) => {
  db.get('SELECT * FROM users WHERE id = ?', [req.params.id], (err, row) => {
    if (err) return res.status(500).json({ error: err.message });
    res.json(row || {});
  });
});

app.put('/api/users/:id', requireAuth, (req, res) => {
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
app.post('/api/checkout', requireAuth, (req, res) => {
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

app.post('/api/checkin', requireAuth, (req, res) => {
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
app.get('/api/loans', requireAuth, (req, res) => {
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
