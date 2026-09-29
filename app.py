import os
import csv
import re
import base64
from datetime import datetime

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from matplotlib import colors

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# FILE / FOLDER CONFIGURATION
# ============================================================

TRANSACTION_FOLDER = "Transation_data"
PASSWORD_FOLDER = "password_management"
PASSWORD_FILE = os.path.join(
    PASSWORD_FOLDER,
    "password_csv.csv"
)

BACKGROUND_FOLDER = "assets"
BACKGROUND_IMAGE = os.path.join(
    BACKGROUND_FOLDER,
    "background.jpg"
)

os.makedirs(
    TRANSACTION_FOLDER,
    exist_ok=True
)

os.makedirs(
    PASSWORD_FOLDER,
    exist_ok=True
)

os.makedirs(
    BACKGROUND_FOLDER,
    exist_ok=True
)

ph = PasswordHasher()


# ============================================================
# SESSION STATE
# ============================================================

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if "page" not in st.session_state:
    st.session_state.page = "Login"


# ============================================================
# BACKGROUND IMAGE
# ============================================================

if os.path.exists(BACKGROUND_IMAGE):

    with open(
        BACKGROUND_IMAGE,
        "rb"
    ) as image_file:

        encoded_image = base64.b64encode(
            image_file.read()
        ).decode()

    st.markdown(
        f"""
        <style>

        .stApp {{
            background-image:
                linear-gradient(
                    rgba(0,0,0,0.25),
                    rgba(0,0,0,0.25)
                ),
                url(
                    "data:image/jpeg;base64,{encoded_image}"
                );

            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        """
        <style>

        .stApp {
            background:
                linear-gradient(
                    135deg,
                    #141e30,
                    #243b55
                );
        }

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    [data-testid="stSidebar"] {
        display: none;
    }

    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    .brand {
        font-size: 30px;
        font-weight: 800;
        color: white;
        text-shadow:
            0 3px 10px rgba(0,0,0,0.6);
    }

    .page-title {
        color: white;
        font-size: 34px;
        font-weight: 800;
        text-shadow:
            0 3px 10px rgba(0,0,0,0.6);
        margin-top: 20px;
        margin-bottom: 25px;
    }

    .auth-card {
        background: rgba(255,255,255,0.95);
        padding: 30px;
        border-radius: 22px;
        box-shadow: 0 15px 40px rgba(0,0,0,0.30);
        margin-top: 35px;
        margin-bottom: 15px;
    }

    .auth-title {
        text-align: center;
        font-size: 32px;
        font-weight: 800;
        color: #222;
    }

    .auth-subtitle {
        text-align: center;
        color: #666;
        margin-top: 5px;
        margin-bottom: 20px;
    }

    .profile-container {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 12px;
    }

    .profile-avatar {
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 21px;
        font-weight: bold;
        box-shadow: 0 5px 15px rgba(0,0,0,0.30);
    }

    .profile-name {
        color: white;
        font-weight: 700;
        font-size: 15px;
        text-align: right;
    }

    .profile-role {
        color: white;
        opacity: 0.8;
        font-size: 12px;
        text-align: right;
    }

    .metric-card {
        background: rgba(255,255,255,0.94);
        padding: 22px;
        border-radius: 18px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.20);
    }

    .metric-title {
        color: #666;
        font-size: 15px;
    }

    .metric-value {
        color: #222;
        font-size: 28px;
        font-weight: 800;
        margin-top: 7px;
    }

    .content-card {
        background: rgba(255,255,255,0.94);
        padding: 25px;
        border-radius: 18px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.20);
        margin-top: 20px;
        margin-bottom: 20px;
    }

    .footer-space {
        height: 80px;
    }

    .footer-title {
        text-align: center;
        color: white;
        font-size: 13px;
        margin-bottom: 8px;
        text-shadow: 0 2px 5px black;
    }

    .info-card {
        background: rgba(255,255,255,0.90);
        padding: 18px;
        border-radius: 15px;
        margin-top: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_transaction_file(user_id):
    return os.path.join(TRANSACTION_FOLDER, f"{user_id}.csv")


def create_transaction_file(user_id):
    file_path = get_transaction_file(user_id)
    if not os.path.exists(file_path):
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Date", "Transation_Type", "Description", "Amount"])
    return file_path


def load_transactions(user_id):
    file_path = create_transaction_file(user_id)
    try:
        df = pd.read_csv(file_path)
        if df.empty:
            return pd.DataFrame(columns=["Date", "Transation_Type", "Description", "Amount"])
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df = df.dropna(subset=["Date", "Amount"])
        return df
    except Exception:
        return pd.DataFrame(columns=["Date", "Transation_Type", "Description", "Amount"])


def get_users():
    if not os.path.exists(PASSWORD_FILE):
        return {}
    users = {}
    try:
        with open(PASSWORD_FILE, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if len(row) >= 2:
                    users[row[0]] = row[1]
    except Exception:
        return {}
    return users


def save_user(username, hashed_password):
    file_exists = os.path.exists(PASSWORD_FILE)
    with open(PASSWORD_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists or os.path.getsize(PASSWORD_FILE) == 0:
            writer.writerow(["username", "password"])
        writer.writerow([username, hashed_password])


def validate_password(password):
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain an uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain a lowercase letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain a number."
    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "Password must contain a special character."
    return True, ""


def calculate_balance(df):
    if df.empty:
        return 0, 0, 0
    income = df[df["Transation_Type"] == "INCOME"]["Amount"].sum()
    expense = df[df["Transation_Type"] == "EXPANCE"]["Amount"].sum()
    balance = income - expense
    return income, expense, balance


def profile_initial(username):
    if not username:
        return "U"
    return username[0].upper()


# ============================================================
# REGISTRATION PAGE
# ============================================================

def registration_page():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
            <div class="auth-card">
                <div class="auth-title">💰 Create Account</div>
                <div class="auth-subtitle">Start managing your money easily and securely</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        username = st.text_input("👤 Username", placeholder="Enter your username", key="register_username")
        password = st.text_input("🔒 Password", type="password", placeholder="Create a strong password", key="register_password")
        confirm_password = st.text_input("🔐 Confirm Password", type="password", placeholder="Re-enter your password", key="register_confirm_password")

        st.write("")

        if st.button("📝 Create Account", use_container_width=True, key="create_account_button"):
            username = username.strip()

            if not username:
                st.error("Please enter a username.")
            elif not password:
                st.error("Please enter a password.")
            elif password != confirm_password:
                st.error("Passwords do not match.")
            else:
                users = get_users()
                if username in users:
                    st.error("Username already exists.")
                else:
                    valid, message = validate_password(password)
                    if not valid:
                        st.error(message)
                    else:
                        hashed_password = ph.hash(password)
                        save_user(username, hashed_password)
                        create_transaction_file(username)
                        st.success("Registration successful!")
                        st.session_state.page = "Login"
                        st.rerun()


# ============================================================
# LOGIN PAGE
# ============================================================

def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            """
            <div class="auth-card">
                <div class="auth-title">👋 Welcome Back</div>
                <div class="auth-subtitle">Login to your Expense Tracker</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        username = st.text_input("👤 Username", placeholder="Enter your username", key="login_username")
        password = st.text_input("🔒 Password", type="password", placeholder="Enter your password", key="login_password")

        st.write("")

        if st.button("🔑 Login", use_container_width=True, key="login_form_button"):
            username = username.strip()
            users = get_users()

            if not username:
                st.error("Please enter your username.")
            elif not password:
                st.error("Please enter your password.")
            elif username not in users:
                st.error("Username not found. Please register first.")
            else:
                try:
                    ph.verify(users[username], password)
                    st.session_state.logged_in_user = username
                    st.session_state.page = "Home"
                    create_transaction_file(username)
                    st.success("Login successful!")
                    st.rerun()
                except (VerifyMismatchError, VerificationError):
                    st.error("Incorrect password.")


# ============================================================
# HOME PAGE
# ============================================================

def home_page():
    username = st.session_state.logged_in_user
    df = load_transactions(username)
    income, expense, balance = calculate_balance(df)

    st.markdown(
        f"""
        <div class="page-title">🏠 Welcome, {username}</div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">💵 Total Income</div>
                <div class="metric-value">₹{income:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">💸 Total Expense</div>
                <div class="metric-value">₹{expense:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-title">💰 Current Balance</div>
                <div class="metric-value">₹{balance:,.2f}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        """
        <div class="content-card">
            <h3>📋 Recent Transactions</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    if df.empty:
        st.info("No transactions available.")
    else:
        recent = df.sort_values("Date", ascending=False).head(5)
        display_df = recent.copy()
        display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
        display_df["Amount"] = display_df["Amount"].apply(lambda x: f"₹{x:,.2f}")

        st.dataframe(display_df, use_container_width=True, hide_index=True)


# ============================================================
# ADD TRANSACTION
# ============================================================

def add_transaction_page():
    st.markdown(
        """
        <div class="page-title">➕ Add Transaction</div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        transaction_type = st.selectbox("Transaction Type", ["INCOME", "EXPANCE"], key="transaction_type")
        description = st.text_input("📝 Description", placeholder="Example: Salary, Food, Travel...", key="transaction_description")
        amount = st.number_input("💰 Amount", min_value=0.0, step=100.0, format="%.2f", key="transaction_amount")
        transaction_date = st.date_input("📅 Date", value=datetime.now().date(), key="transaction_date")

        if st.button("💾 Save Transaction", use_container_width=True, key="save_transaction_button"):
            if not description.strip():
                st.error("Please enter a description.")
            elif amount <= 0:
                st.error("Amount must be greater than zero.")
            else:
                file_path = create_transaction_file(st.session_state.logged_in_user)

                with open(file_path, "a", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow([
                        transaction_date.strftime("%Y-%m-%d"),
                        transaction_type,
                        description.strip().lower(),
                        amount
                    ])

                st.success("Transaction added successfully!")
                st.rerun()


# ============================================================
# TRANSACTIONS PAGE
# ============================================================

def transactions_page():
    st.markdown(
        """
        <div class="page-title">📋 Transactions</div>
        """,
        unsafe_allow_html=True
    )

    df = load_transactions(st.session_state.logged_in_user)

    if df.empty:
        st.info("No transactions available.")
        return

    col1, col2 = st.columns(2)

    with col1:
        transaction_filter = st.selectbox("🔎 Transaction Type", ["ALL", "INCOME", "EXPANCE"], key="transaction_filter")

    with col2:
        search = st.text_input("🔍 Search Description", key="transaction_search")

    filtered_df = df.copy()

    if transaction_filter != "ALL":
        filtered_df = filtered_df[filtered_df["Transation_Type"] == transaction_filter]

    if search.strip():
        filtered_df = filtered_df[
            filtered_df["Description"].astype(str).str.contains(search.strip(), case=False, na=False)
        ]

    filtered_df = filtered_df.sort_values("Date", ascending=False)

    st.dataframe(filtered_df, use_container_width=True, hide_index=True)


# ============================================================
# ANALYTICS PAGE
# ============================================================

def analytics_page():
    st.markdown(
        """
        <div class="page-title">📊 Analytics</div>
        """,
        unsafe_allow_html=True
    )

    df = load_transactions(st.session_state.logged_in_user)

    if df.empty:
        st.info("Add transactions to view analytics.")
        return

    # --------------------------------------------------------
    # FILTER WIDGETS
    # --------------------------------------------------------

    st.markdown(
        """
        <div class="content-card">
            <h3>🔎 Filters</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    filter_col1, filter_col2 = st.columns(2)

    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()

    with filter_col1:
        date_range = st.date_input(
            "📅 Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
            key="analytics_date_range"
        )

    with filter_col2:
        all_categories = sorted(df["Description"].dropna().unique().tolist())
        selected_categories = st.multiselect(
            "🏷️ Categories",
            options=all_categories,
            default=all_categories,
            key="analytics_category_filter"
        )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    df = df[
        (df["Date"].dt.date >= start_date)
        & (df["Date"].dt.date <= end_date)
    ]

    if selected_categories:
        df = df[df["Description"].isin(selected_categories)]

    if df.empty:
        st.info("No transactions match the selected filters.")
        return

    st.markdown(
        """
        <div class="content-card">
            <h3>📈 Daily Transaction Trend</h3>
            <p>Income and expense are calculated separately for each day.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    daily_income = df[df["Transation_Type"] == "INCOME"].groupby("Date")["Amount"].sum()
    daily_expense = df[df["Transation_Type"] == "EXPANCE"].groupby("Date")["Amount"].sum()

    daily_trend = pd.DataFrame({"Income": daily_income, "Expense": daily_expense}).fillna(0)
    daily_trend = daily_trend.sort_index()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(daily_trend.index, daily_trend["Income"], marker="o", linewidth=2, label="Income")
    ax.plot(daily_trend.index, daily_trend["Expense"], marker="o", linewidth=2, label="Expense")
    ax.set_title("Daily Income vs Expense")
    ax.set_xlabel("Date")
    ax.set_ylabel("Amount (₹)")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.markdown(
        """
        <div class="content-card">
            <h3>📅 Daily Summary</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    daily_display = daily_trend.reset_index()
    daily_display["Date"] = daily_display["Date"].dt.strftime("%Y-%m-%d")

    st.dataframe(daily_display, use_container_width=True, hide_index=True)

    total_income = daily_trend["Income"].sum()
    total_expense = daily_trend["Expense"].sum()

    st.markdown(
        """
        <div class="content-card">
            <h3>Expense Categories</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    expense_by_category = (
        df[df["Transation_Type"] == "EXPANCE"]
        .groupby("Description")["Amount"]
        .sum()
        .sort_values(ascending=False)
    )

    if expense_by_category.empty:
        st.info("No expense data available to chart.")
    else:
        category_colors = [
            "orange",
            "aqua",
            "aquamarine","brown",
            "red",
            "cyan",
            "darkcyan",
            "darkgreen",
            "darkorange",
        ]
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.pie(
            expense_by_category.values,
            labels=expense_by_category.index,
            autopct="%1.1f%%",
            colors=category_colors[: len(expense_by_category)],
            startangle=90
        )
        ax.set_title("Expenses by Category")
        ax.axis("equal")

        st.pyplot(fig)
        plt.close(fig)
    st.markdown(
        """
        <div class="content-card">
            <h3>💰 Total Income vs Expense</h3>
        </div>
        """,
        unsafe_allow_html=True
    )



    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(["Income", "Expense"], [total_income, total_expense],color=["green","red"])
    ax.set_title("Total Income vs Total Expense")
    ax.set_ylabel("Amount (₹)")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.pie([total_income, total_expense], labels=["Income", "Expense"], autopct="%1.1f%%")
    ax.set_title("Income / Expense Distribution")
    st.pyplot(fig)
    plt.close(fig)

    st.markdown(
        """
        <div class="content-card">
            <h3>📅 Monthly Analysis</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    df["Month"] = df["Date"].dt.to_period("M").astype(str)

    monthly = df.groupby(["Month", "Transation_Type"])["Amount"].sum().unstack(fill_value=0)

    if "INCOME" not in monthly.columns:
        monthly["INCOME"] = 0
    if "EXPANCE" not in monthly.columns:
        monthly["EXPANCE"] = 0

    monthly = monthly.rename(columns={"INCOME": "Income", "EXPANCE": "Expense"})

    st.dataframe(monthly, use_container_width=True)

    fig, ax = plt.subplots(figsize=(12, 5))
    monthly[["Income", "Expense"]].plot(kind="bar", ax=ax)
    ax.set_title("Monthly Income and Expense")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount (₹)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


# ============================================================
# PROFILE PAGE
# ============================================================

def profile_page():
    username = st.session_state.logged_in_user
    initial = profile_initial(username)

    st.markdown(
        """
        <div class="page-title">👤 Profile</div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(
            f"""
            <div class="content-card" style="text-align:center;">
                <div class="profile-avatar" style="width:90px; height:90px; margin:auto; font-size:40px;">
                    {initial}
                </div>
                <h2>{username}</h2>
                <p>Expense Tracker User</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("🚪 Logout", use_container_width=True, key="logout_button"):
            st.session_state.logged_in_user = None
            st.session_state.page = "Login"
            st.rerun()


# ============================================================
# DELETE DATA PAGE
# ============================================================

def delete_data_page():
    st.markdown(
        """
        <div class="page-title">🗑️ Delete Transaction Data</div>
        """,
        unsafe_allow_html=True
    )

    st.warning("⚠️ This will permanently delete all your transaction records.")

    confirmation = st.checkbox("I understand that this action cannot be undone.", key="delete_confirmation")

    if confirmation:
        if st.button("🗑️ Delete All Transactions", type="primary", key="delete_all_button"):
            file_path = get_transaction_file(st.session_state.logged_in_user)

            if os.path.exists(file_path):
                os.remove(file_path)
                create_transaction_file(st.session_state.logged_in_user)
                st.success("All transaction data deleted.")
                st.rerun()
            else:
                st.info("No transaction data found.")


# ============================================================
# FOOTER NAVIGATION
# ============================================================

def footer_navigation():
    st.markdown('<div class="footer-space"></div>', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="footer-title">Expense Tracker Navigation</div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🏠 Home", use_container_width=True, key="footer_home"):
            st.session_state.page = "Home"
            st.rerun()

    with col2:
        if st.button("➕ Add", use_container_width=True, key="footer_add"):
            st.session_state.page = "Add"
            st.rerun()

    with col3:
        if st.button("📋 Transactions", use_container_width=True, key="footer_transactions"):
            st.session_state.page = "Transactions"
            st.rerun()

    col4, col5, col6 = st.columns(3)

    with col4:
        if st.button("📊 Analytics", use_container_width=True, key="footer_analytics"):
            st.session_state.page = "Analytics"
            st.rerun()

    with col5:
        if st.button("👤 Profile", use_container_width=True, key="footer_profile"):
            st.session_state.page = "Profile"
            st.rerun()

    with col6:
        if st.button("🗑️ Delete", use_container_width=True, key="footer_delete"):
            st.session_state.page = "Delete"
            st.rerun()


# ============================================================
# LOGGED OUT SCREEN
# ============================================================

if st.session_state.logged_in_user is None:

    header_left, header_right = st.columns([8, 2])

    with header_left:
        st.markdown(
            """
            <div class="brand">💰 Expense Tracker</div>
            """,
            unsafe_allow_html=True
        )

    with header_right:
        if st.button("🔑 Login", use_container_width=True, key="top_right_login"):
            st.session_state.page = "Login"
            st.rerun()

    if st.session_state.page == "Register":
        registration_page()
    else:
        login_page()

        st.write("")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown(
                """
                <p style="text-align:center; color:white;">Don't have an account?</p>
                """,
                unsafe_allow_html=True
            )

            if st.button("📝 Create New Account", use_container_width=True, key="new_account_button"):
                st.session_state.page = "Register"
                st.rerun()


# ============================================================
# LOGGED IN SCREEN
# ============================================================

else:
    username = st.session_state.logged_in_user
    initial = profile_initial(username)

    header_left, header_right = st.columns([7, 3])

    with header_left:
        st.markdown(
            """
            <div class="brand">💰 Expense Tracker</div>
            """,
            unsafe_allow_html=True
        )

    with header_right:
        st.markdown(
            f"""
            <div class="profile-container">
                <div>
                    <div class="profile-name">{username}</div>
                    <div class="profile-role">Personal Account</div>
                </div>
                <div class="profile-avatar">{initial}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    if st.session_state.page == "Home":
        home_page()
    elif st.session_state.page == "Add":
        add_transaction_page()
    elif st.session_state.page == "Transactions":
        transactions_page()
    elif st.session_state.page == "Analytics":
        analytics_page()
    elif st.session_state.page == "Profile":
        profile_page()
    elif st.session_state.page == "Delete":
        delete_data_page()
    else:
        home_page()

    footer_navigation()