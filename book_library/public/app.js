async function fetchBooks() {
  const res = await fetch('/api/books');
  return res.json();
}

async function fetchUsers() {
  const res = await fetch('/api/users');
  return res.json();
}

async function fetchLoans() {
  const res = await fetch('/api/loans');
  return res.json();
}

async function refresh() {
  const books = await fetchBooks();
  const users = await fetchUsers();
  const loans = await fetchLoans();

  const bookList = document.getElementById('book-list');
  bookList.innerHTML = '';
  books.forEach(b => {
    const li = document.createElement('li');
    li.textContent = `${b.title} by ${b.author}`;
    bookList.appendChild(li);
  });

  const bookSelect = document.getElementById('checkout-book');
  bookSelect.innerHTML = '';
  books.forEach(b => {
    const opt = document.createElement('option');
    opt.value = b.id;
    opt.textContent = b.title;
    bookSelect.appendChild(opt);
  });

  const userSelect = document.getElementById('checkout-user');
  userSelect.innerHTML = '';
  users.forEach(u => {
    const opt = document.createElement('option');
    opt.value = u.id;
    opt.textContent = u.name;
    userSelect.appendChild(opt);
  });

  const loanList = document.getElementById('loan-list');
  loanList.innerHTML = '';
  loans.forEach(l => {
    const li = document.createElement('li');
    const status = l.return_date ? 'returned' : `due ${l.due_date}`;
    li.textContent = `${l.title} -> ${l.user_name} (${status})`;
    loanList.appendChild(li);
  });
}

document.getElementById('book-form').addEventListener('submit', async e => {
  e.preventDefault();
  const title = document.getElementById('title').value;
  const author = document.getElementById('author').value;
  const isbn = document.getElementById('isbn').value;
  await fetch('/api/books', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, author, isbn })
  });
  e.target.reset();
  refresh();
});

document.getElementById('user-form').addEventListener('submit', async e => {
  e.preventDefault();
  const name = document.getElementById('user-name').value;
  const email = document.getElementById('user-email').value;
  const phone = document.getElementById('user-phone').value;
  await fetch('/api/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, phone })
  });
  e.target.reset();
  refresh();
});

document.getElementById('checkout-form').addEventListener('submit', async e => {
  e.preventDefault();
  const book_id = document.getElementById('checkout-book').value;
  const user_id = document.getElementById('checkout-user').value;
  const due_date = document.getElementById('due-date').value;
  await fetch('/api/checkout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ book_id, user_id, due_date })
  });
  e.target.reset();
  refresh();
});

refresh();
