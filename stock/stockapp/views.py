

# Create your views here.
from django.shortcuts import render, redirect

from .db import get_db_connection
from django.contrib import messages
import numpy as np
import matplotlib.pyplot as plt
import io, base64
import sqlite3
from django.db import connection
import mysql.connector
import numpy as np
import matplotlib.pyplot as plt
import base64
import io
from django.shortcuts import render, redirect
from django.db import connection
from scipy.optimize import minimize
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login



def get_db_connection():
    return mysql.connector.connect(
        host="localhost",       # Adjust host if necessary
        user="root",    # Replace with your DB username
        password="S1tty1$great",  # Replace with your DB password
        database="stock"  # Replace with your database name
    )
def home(request):
    return render(request, 'home.html')


def login_user(request):
    if request.method == 'POST':
        uname = request.POST['uname']
        password = request.POST['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM USER WHERE UNAME=%s AND PASSWORD=%s", (uname, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            request.session['user_id'] = user[0]     # Assuming user_id is in column 0
            request.session['uname'] = user[1] 
            print(request.session['user_id'])      # Assuming uname is in column 1
            return redirect('main_menu')
        else:
            messages.error(request, "Invalid username or password")

    return render(request, 'login.html')



def register(request):
    if request.method == 'POST':
        uname = request.POST['uname']
        email = request.POST['email']
        phone = request.POST['phone']
        password = request.POST['password']
        dob = request.POST['dob']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO USER(UNAME, EMAILID, PHONENUMBER, PASSWORD, DOB) VALUES (%s, %s, %s, %s, %s)",
                       (uname, email, phone, password, dob))
        conn.commit()
        conn.close()
        return redirect('login')

    return render(request, 'register.html')

def main_menu(request):
    return render(request, 'main_menu.html')
def add_stock(request):
    if request.method == 'POST':
        company_id = request.POST['company_id']
        cname = request.POST['cname']
        currdate = request.POST['currdate']
        openrate = request.POST['openrate']
        closerate = request.POST['closerate']
        dayhigh = request.POST['dayhigh']
        daylow = request.POST['daylow']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO COMPANY_STOCK (COMPANY_ID, CNAME, CURRDATE, OPENRATE, CLOSERATE, DAYHIGH, DAYLOW)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (company_id, cname, currdate, openrate, closerate, dayhigh, daylow))
        conn.commit()
        conn.close()

        return redirect('main_menu')

    return render(request, 'add_stock.html')

def user_portfolio(request):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COMPANY_ID, CNAME FROM COMPANY_STOCK GROUP BY COMPANY_ID")
    companies = cursor.fetchall()

    if request.method == 'POST':
        user_id = request.session.get('user_id')
        company_id = request.POST['company_id']
        tot_shares = request.POST['tot_shares']
        avg_price = request.POST['avg_price']
        total_price = float(tot_shares) * float(avg_price)

        cursor.execute("""
            INSERT INTO USER_SHARES (USER_ID, COMPANY_ID, TOT_SHARES, AVERAGE_PRICE, TOTAL_PRICE)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, company_id, tot_shares, avg_price, total_price))
        conn.commit()
        conn.close()
        return redirect('main_menu')

    conn.close()
    return render(request, 'user_portfolio.html', {'companies': companies})



def mean_variance_optimization(returns, cov_matrix, risk_free_rate=0.01):
    num_assets = len(returns)

    def portfolio_performance(weights):
        ret = np.dot(weights, returns)
        vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))

        if vol == 0:
            return float('inf')  # Avoid division by zero

        sharpe = (ret - risk_free_rate) / vol
        return -sharpe  # We minimize the negative Sharpe Ratio

    if num_assets == 0 or np.all(returns == 0) or np.all(cov_matrix == 0):
        # Sanity check to avoid nonsense optimization
        return np.array([])

    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0, 1) for _ in range(num_assets))
    initial_guess = num_assets * [1. / num_assets]

    result = minimize(portfolio_performance, initial_guess, method='SLSQP', bounds=bounds, constraints=constraints)

    if not result.success:
        return np.array([])

    return result.x

 
def create_portfolio(request):
    #print("User:", request.user)
    #user_id = request.user.id
   
    #print("User ID:", user_id)
    user_id = request.session.get('user_id')
    print("Session User:", request.session.get('uname'))
    print("Session User ID:", user_id)
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        print("POST data:", request.POST)
        print(">>> Trying to delete user shares for user_id =", user_id)

        cursor.execute("""
            DELETE FROM user_shares WHERE user_id = %s
            """, (user_id,))
        conn.commit()

        inserted_any = False
        error_messages = []
        stocks = fetch_company_stocks()

        for stock in stocks:
            company_id = stock['company_id']
            shares = request.POST.get(f'shares_{company_id}')
            print(f"Shares for company {company_id}: {shares}")

            if shares and shares.isdigit():
                shares = int(shares)

                cursor.execute("SELECT price FROM company_stock WHERE company_id = %s", (company_id,))
                data = cursor.fetchone()

                if data:
                    price = data[0]
                    total_price = shares * price
                    average_price = price

                    try:
                        print("Inserting into user_shares:", user_id, company_id, shares, average_price, total_price)
                        cursor.execute("""
                            INSERT INTO user_shares (USER_ID, COMPANY_ID, TOT_SHARES, AVERAGE_PRICE, TOTAL_PRICE)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (user_id, company_id, shares, average_price, total_price))
                        inserted_any = True
                    except Exception as e:
                        print(f"Error inserting data: {e}")
                        error_messages.append(f"Error with stock ID {company_id}: {str(e)}")
                else:
                    error_messages.append(f"No stock found for ID: {company_id}")
            elif shares:
                error_messages.append(f"Invalid number of shares for stock ID {company_id}")

        conn.commit()
        conn.close()

        if inserted_any:
            return redirect('portfolio_result')

        return render(request, 'create_portfolio.html', {
            'error': "No valid entries added. " + "; ".join(error_messages),
            'stocks': stocks
        })

    # GET request
    stocks = fetch_company_stocks()
    return render(request, 'create_portfolio.html', {'stocks': stocks})




def fetch_company_stocks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT company_id, cname FROM company_stock")
    stocks = [{'company_id': row[0], 'company_name': row[1]} for row in cursor.fetchall()]
    conn.close()
    return stocks


def portfolio_result(request):
    user_id = request.session.get('user_id')
    print("Session User:", request.session.get('uname'))
    print("Session User ID:", user_id)
    conn = get_db_connection()
    cursor = conn.cursor()
    print(">>> 1 achieved")
    
    # Get current portfolio from DB
    cursor.execute("""
        SELECT cs.company_id, cs.cname, cs.price, us.tot_shares
        FROM user_shares us
        JOIN company_stock cs ON us.company_id = cs.company_id
        WHERE us.user_id = %s
    """, (user_id,))
    rows = cursor.fetchall()
    print(rows)
    conn.close()

    if not rows:
        return render(request, 'portfolio_result.html', {
            'error': 'No portfolio data found. Please add stocks first.'
        })
    
    company_ids = [row[0] for row in rows]
    company_names = [row[1] for row in rows]
    prices = np.array([row[2] for row in rows])
    shares = np.array([row[3] for row in rows])
    portfolio_value = float(np.sum(prices * shares))

    # Simulate returns (replace with real historical returns if needed)
    returns = (np.random.normal(0.02, 0.01, len(prices)))
    cov_matrix = np.diag(np.random.uniform(0.01, 0.05, len(prices)))

    try:
        weights = mean_variance_optimization(returns, cov_matrix)

        if weights.size == 0:
            return render(request, 'portfolio_result.html', {
                'error': 'Portfolio optimization failed. Try with different stock combinations.'
            })

        allocation = {
            name: round(w * 100, 2)
            for name, w in zip(company_names, weights)
        }

        portfolio_summary = []
        for i in range(len(company_names)):
            value = prices[i] * shares[i]
            portfolio_summary.append({
                'name': company_names[i],
                'shares': int(shares[i]),
                'price': round(prices[i], 2),
                'value': round(value, 2),
                'allocation': allocation[company_names[i]]
            })

        # Generate pie chart
            fig, ax = plt.subplots()
        wedges, texts, autotexts = ax.pie(
            weights,
            labels=company_names,
            autopct='%1.1f%%',
            startangle=90,
            textprops=dict(color="black")  # <-- black text
        )

        # Add a white circle in the center to make it a donut
        centre_circle = plt.Circle((0, 0), 0.80, fc='white')
        fig.gca().add_artist(centre_circle)

        # Make sure it stays circular
        ax.axis('equal')

        # Improve visibility
        plt.setp(autotexts, size=10, weight="bold")
        plt.setp(texts, size=9)

        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        pie_img = base64.b64encode(buf.read()).decode('utf-8')


           
        return render(request, 'portfolio_result.html', {
        'portfolio_summary': portfolio_summary,
        'total': round(portfolio_value, 2),
        'pie_img': pie_img
        })

    except ZeroDivisionError:
        return render(request, 'portfolio_result.html', {
            'error': 'Optimization failed due to zero variance or invalid data.'
        })


def optimizer_info(request):
    return render(request, 'optimizer_info.html')
