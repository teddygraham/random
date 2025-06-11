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

async function renderBooks() {
  const list = document.getElementById('book-list');
  if (!list) return;
  const books = await fetchBooks();
  list.innerHTML = '';
  books.forEach(b => {
    const li = document.createElement('li');
    li.textContent = `${b.title} by ${b.author}`;
    list.appendChild(li);
  });
}

async function renderUsers() {
  const list = document.getElementById('user-list');
  if (!list) return;
  const users = await fetchUsers();
  list.innerHTML = '';
  users.forEach(u => {
    const li = document.createElement('li');
    const link = document.createElement('a');
    link.href = `edit_user.html?id=${u.id}`;
    link.textContent = 'Edit';
    li.textContent = `${u.name} (${u.email || ''} ${u.phone || ''}) `;
    li.appendChild(link);
    list.appendChild(li);
  });
}

async function renderLoans() {
  const list = document.getElementById('loan-list');
  if (!list) return;
  const loans = await fetchLoans();
  list.innerHTML = '';
  loans.forEach(l => {
    const li = document.createElement('li');
    const status = l.return_date ? 'returned' : `due ${l.due_date}`;
    li.textContent = `${l.title} -> ${l.user_name} (${status})`;
    list.appendChild(li);
  });
}

async function populateCheckout() {
  const bookSelect = document.getElementById('checkout-book');
  const userSelect = document.getElementById('checkout-user');
  if (!bookSelect && !userSelect) return;
  const books = await fetchBooks();
  const users = await fetchUsers();
  if (bookSelect) {
    bookSelect.innerHTML = '';
    books.forEach(b => {
      const opt = document.createElement('option');
      opt.value = b.id;
      opt.textContent = b.title;
      bookSelect.appendChild(opt);
    });
  }
  if (userSelect) {
    userSelect.innerHTML = '';
    users.forEach(u => {
      const opt = document.createElement('option');
      opt.value = u.id;
      opt.textContent = u.name;
      userSelect.appendChild(opt);
    });
  }
}

function show(id) {
  const el = document.getElementById(id);
  if (el) el.classList.remove('hidden');
}

function hide(id) {
  const el = document.getElementById(id);
  if (el) el.classList.add('hidden');
}

// Add book
const bookForm = document.getElementById('book-form');
if (bookForm) {
  bookForm.addEventListener('submit', async e => {
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
    hide('add-book-modal');
    renderBooks();
  });
}

const addBookBtn = document.getElementById('open-add-book');
const closeBookBtn = document.getElementById('close-add-book');
if (addBookBtn) addBookBtn.addEventListener('click', () => show('add-book-modal'));
if (closeBookBtn) closeBookBtn.addEventListener('click', () => hide('add-book-modal'));

// Add user
const userForm = document.getElementById('user-form');
if (userForm) {
  userForm.addEventListener('submit', async e => {
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
    hide('add-user-modal');
    renderUsers();
  });
}

const addUserBtn = document.getElementById('open-add-user');
const closeUserBtn = document.getElementById('close-add-user');
if (addUserBtn) addUserBtn.addEventListener('click', () => show('add-user-modal'));
if (closeUserBtn) closeUserBtn.addEventListener('click', () => hide('add-user-modal'));

// Edit user
const editForm = document.getElementById('edit-user-form');
if (editForm) {
  const params = new URLSearchParams(window.location.search);
  const id = params.get('id');
  if (id) {
    fetch(`/api/users/${id}`).then(r => r.json()).then(u => {
      document.getElementById('edit-user-name').value = u.name || '';
      document.getElementById('edit-user-email').value = u.email || '';
      document.getElementById('edit-user-phone').value = u.phone || '';
    });
  }
  editForm.addEventListener('submit', async e => {
    e.preventDefault();
    const name = document.getElementById('edit-user-name').value;
    const email = document.getElementById('edit-user-email').value;
    const phone = document.getElementById('edit-user-phone').value;
    await fetch(`/api/users/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, phone })
    });
    window.location.href = 'users.html';
  });
}

// Checkout form
const checkoutForm = document.getElementById('checkout-form');
if (checkoutForm) {
  checkoutForm.addEventListener('submit', async e => {
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
  });
  populateCheckout();
}

const checkoutBtn = document.getElementById('open-checkout');
const closeCheckoutBtn = document.getElementById('close-checkout');
if (checkoutBtn) checkoutBtn.addEventListener('click', () => {
  populateCheckout();
  show('checkout-modal');
});
if (closeCheckoutBtn) closeCheckoutBtn.addEventListener('click', () => hide('checkout-modal'));

// Initial rendering based on page
renderBooks();
renderUsers();
renderLoans();
populateCheckout();
