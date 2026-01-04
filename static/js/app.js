const BASE_URL = "http://127.0.0.1:5000";

/* =====================
   REGISTER
===================== */
function registerUser() {
    fetch(`${BASE_URL}/api/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            full_name: reg_name.value,
            mobile: reg_mobile.value,
            email: reg_email.value,
            password: reg_password.value
        })
    })
    .then(res => res.json())
    .then(data => {
        reg_message.innerText = data.message || data.error;
        if (data.message) {
            setTimeout(() => {
                window.location.href = "/login";
            }, 1500);
        }
    });
}

/* =====================
   LOGIN + REDIRECT
===================== */
function loginUser() {
    fetch(`${BASE_URL}/api/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            email: login_email.value,
            password: login_password.value
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.user_id) {
            // ✅ Save login info
            localStorage.setItem("user_id", data.user_id);
            localStorage.setItem("full_name", data.full_name);

            // ✅ Redirect to dashboard
            window.location.href = "/dashboard";
        } else {
            login_message.innerText = data.error;
        }
    });
}


/* =====================
   SESSION GUARD (3.1)
===================== */
function requireLogin() {
    if (!localStorage.getItem("user_id")) {
        window.location.href = "/login";
    }
}

/* =====================
   LOGOUT
===================== */
function logout() {
    localStorage.clear();
    window.location.href = "/login";
}

/* =====================
   DASHBOARD NAV (4.2)
===================== */
function goToAccount() {
    window.location.href = "/account";
}

function goToTransfer() {
    window.location.href = "/fund-transfer";
}

function goToHistory() {
    window.location.href = "/transactions";
}

/* =====================
   CREATE ACCOUNT
===================== */
function createAccount() {
    const accountType = document.getElementById("account_type").value;
    const msg = document.getElementById("account_message");

    msg.innerText = "";

    if (!accountType) {
        msg.innerText = "Please select account type";
        return;
    }

    fetch("/api/account/create", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            account_type: accountType
        })
    })
    .then(res => res.json())
    .then(data => {
        msg.innerText = data.message || data.error;
    })
    .catch(() => {
        msg.innerText = "Server error";
    });
}


/* =====================
   FUND TRANSFER
===================== */
function transferFunds() {
    const from_account = document.getElementById("from_account").value;
    const to_account = document.getElementById("to_account").value;
    const amount = document.getElementById("amount").value;
    const msg = document.getElementById("transfer_message");

    if (!from_account || !to_account || !amount) {
        msg.innerText = "All fields are required";
        return;
    }

    fetch("/api/account/transfer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            from_account: from_account,
            to_account: to_account,
            amount: amount
        })
    })
    .then(res => res.json())
    .then(data => {
        msg.innerText = data.message || data.error;
    })
    .catch(() => {
        msg.innerText = "Server error";
    });
}



/* =====================
   TRANSACTION HISTORY
===================== */
function getTransactions() {
    const accId = account_id.value;

    fetch(`${BASE_URL}/api/account/${accId}/transactions`)
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("transactions");
            container.innerHTML = "";

            if (!data.transactions || data.transactions.length === 0) {
                container.innerHTML = "<p>No transactions found</p>";
                return;
            }

            data.transactions.forEach(tx => {
                container.innerHTML += `
                    <p>
                        <strong>${tx.transaction_type}</strong><br>
                        Amount: ${tx.amount}<br>
                        Date: ${tx.created_at}
                    </p>
                    <hr>
                `;
            });
        });
}

function depositMoney() {
    const account_id = document.getElementById("deposit_account").value;
    const amount = document.getElementById("deposit_amount").value;

    fetch(`${BASE_URL}/api/account/deposit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ account_id, amount })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("deposit_message").innerText =
            data.message || data.error;
    });
}

function loadAccounts() {
    fetch(`${BASE_URL}/api/accounts`)
        .then(res => res.json())
        .then(data => {
            const container = document.getElementById("accounts");
            container.innerHTML = "";

            if (!data.accounts || data.accounts.length === 0) {
                container.innerHTML = "<p>No accounts found</p>";
                return;
            }

            data.accounts.forEach(acc => {
                container.innerHTML += `
                    <div class="account-box">
                        <strong>${acc.account_type}</strong><br>
                        Account ID: ${acc.account_id}<br>
                        Balance: ₹${acc.balance}
                    </div>
                `;
            });
        });
}

window.onload = loadAccounts;
