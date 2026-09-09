import json
import argparse
from datetime import datetime
import os
import csv

def format_dt(iso_str):
    return datetime.fromisoformat(iso_str).strftime('%Y-%m-%d')

def setlimit(args):
    if os.path.isfile('limit.json'):
        with open('limit.json', 'r', encoding="UTF-8") as file_in:
            limit = json.load(file_in)
    else:
        limit = ["nothing"]
    limit[0] = args.limit
    with open('limit.json', 'w', encoding="UTF-8") as f:
        json.dump(limit, f)
    
    if os.path.isfile('expenses.json'):
        with open('expenses.json', 'r', encoding="UTF-8") as file_in:
            monthly_expenses = json.load(file_in)
    else:
        monthly_expenses = None
    
    time = datetime.now()
    month = str(time.month)
    if monthly_expenses and monthly_expenses[month] and limit[0] < monthly_expenses[month]:
        print(f"You have already reached this limit on this month +{monthly_expenses[month] - limit[0]}")
    return (f'You have set a monthly budget {limit[0]}')

def add(args):
    if os.path.isfile('data.json'):
        with open("data.json", 'r', encoding="UTF-8") as file_in:
            records = json.load(file_in)
    else:
        records = []
    
    if os.path.isfile('expenses.json'):
        with open('expenses.json', 'r', encoding="UTF-8") as file_in:
            monthly_expenses = json.load(file_in)
    else:
        monthly_expenses = {}
        
    expense_id = max((int(t['id']) for t in records), default=0) + 1
    description = " ".join(args.description)
    amount = args.amount
    time = datetime.now()
    month = str(time.month)
    category = args.category
    created_at = datetime.now().isoformat()
    
    if month not in monthly_expenses.keys():
        monthly_expenses[month] = amount
    else:
        monthly_expenses[month] += amount

    expense = {
        'id': expense_id,
        'description': description,
        'amount': amount,
        'created_at': created_at,
        'month': month,
        'category': category
    }
    records.append(expense)
    
    if os.path.isfile('limit.json'):
        with open('limit.json', 'r', encoding="UTF-8") as file_in:
            limit = json.load(file_in)
    else:
        limit = None
        
    if monthly_expenses[month] and limit and monthly_expenses[month] > float(limit[0]):
        print(f"You already reached your monthly limit +{monthly_expenses[month] - limit[0]}")
        
    with open('expenses.json', 'w', encoding='UTF-8') as file_out:
        json.dump(monthly_expenses, file_out, ensure_ascii=False, indent=2)

    with open('data.json', 'w', encoding='UTF-8') as file_out:
        json.dump(records, file_out, ensure_ascii=False, indent=2)
    
    return (f'Expense added successfully (ID: {expense_id})')

def delete(args):
    expense_id = args.id
    
    if os.path.isfile('data.json'):
        with open("data.json", 'r', encoding="UTF-8") as file_in:
            records = json.load(file_in)
    else:
        return (f"You haven't added any expense")
    
    if os.path.isfile('expenses.json'):
        with open('expenses.json', 'r', encoding="UTF-8") as file_in:
            monthly_expenses = json.load(file_in)
    else:
        return (f"You haven't added any expense")
    
    needed_id = next((t for t in range(len(records)) if records[t]['id'] == expense_id), None)
    if needed_id is None:
        return f"Task with id {expense_id} doesn't exist"
    monthly_expenses[records[needed_id]['month']] -= records[needed_id]['amount']
    
    records.pop(needed_id)
    
    with open("data.json", 'w', encoding="UTF-8") as file_out:
        json.dump(records, file_out, ensure_ascii=False, indent=2)
    with open('expenses.json', 'w', encoding='UTF-8') as file_out:
        json.dump(monthly_expenses, file_out, ensure_ascii=False, indent=2)

    return (f'Expense deleted successfully (ID: {expense_id})')
    
def list(args):
    category = args.category
    month = args.month
    
    if os.path.isfile('data.json'):
        with open("data.json", 'r', encoding="UTF-8") as file_in:
            records = json.load(file_in)
    else:
        return (f"You haven't added any expense")
    headers = ['ID', 'Date', 'Description', 'Amount']
    rows = []
    
    for t in records:
        if month and t['month'] == month:
            if category is not None and t['category'] == category:
                rows.append([
                    str(t['id']),
                    format_dt(t['created_at']),
                    t['description'],
                    str(t['amount'])
                ])
        else:
            if category is not None and t['category'] == category:
                rows.append([
                    str(t['id']),
                    format_dt(t['created_at']),
                    t['description'],
                    str(t['amount'])
                ])
            elif category is None:
                rows.append([
                    str(t['id']),
                    format_dt(t['created_at']),
                    t['description'],
                    str(t['amount'])
                ])
 
    widths = [max(len(h), max((len(r[i]) for r in rows), default=0)) for i, h in enumerate(headers)]
 
    def fmt_row(cols):
        return "  ".join(c.ljust(w) for c, w in zip(cols, widths))
 
    lines = [fmt_row(headers), fmt_row(['-' * w for w in widths])]
    lines.extend(fmt_row(r) for r in rows)
    return "\n".join(lines)

def summary(args):
    month = args.month
    category = args.category
    if os.path.isfile('data.json'):
        with open("data.json", 'r', encoding="UTF-8") as file_in:
            records = json.load(file_in)
    else:
        return (f"You haven't added any expense")
    
    monthly_expenses = records
    if month is not None:
        monthly_expenses = [t for t in records if t['month'] == month]
        if not monthly_expenses:
            return (f"You haven't bought anything during the month {month}") 
    if category is not None:
        monthly_expenses = [t for t in monthly_expenses if t['category'] == category]
    sum_of_amount = 0
    for i in monthly_expenses:
        sum_of_amount += i['amount']
    
    if month and category:
        return (f'Total expenses for {month} in category {category}: {sum_of_amount}')
    elif month:
        return (f'Total expenses for {month}: {sum_of_amount}')
    else:
        return (f'Total expenses: {sum_of_amount}')

def expense_csv(args):
    month = args.month 
    category = args.category
    
    if os.path.isfile('data.json'):
        with open("data.json", 'r', encoding="UTF-8") as file_in:
            records = json.load(file_in)
    else:
        return (f"You haven't added any expense")
    
    expense = [
        t for t in records
        if (month is None or t['month'] == month)
    ]
    if not expense:
        return f"No expenses found for the given filters"
    
    with open('expense.csv', 'w', newline='', encoding="UTF-8") as file_o:
        columns = ['id', 'description', 'amount', 'month', 'category']
        csv_writer = csv.DictWriter(file_o, fieldnames=columns, extrasaction='ignore')
        csv_writer.writeheader()
        csv_writer.writerows(expense)

parser = argparse.ArgumentParser(
    description="Expense Tracker - track, list, and summarize your personal expenses from the command line."
)
subparsers = parser.add_subparsers(
    dest='command',
    title='commands',
    description="Available commands. Run '<command> -h' for command-specific help.",
    help='command to run'
)

# ============== add =============
parser_add = subparsers.add_parser(
    'add',
    help='Add a new expense',
    description='Add a new expense record with a description, amount, and category.'
)
parser_add.add_argument(
    "-d", "--description", type=str, nargs='+', required=True,
    help="Short description of the expense, e.g. 'Groceries at Walmart' (multiple words allowed)"
)
parser_add.add_argument(
    "-a", "--amount", type=float, required=True,
    help="Amount spent, e.g. 25.50"
)
parser_add.add_argument(
    "-c", "--category", type=str, required=True,
    help="Category of the expense, e.g. food, transport, rent"
)
parser_add.set_defaults(func=add)

# ============== delete =============
parser_delete = subparsers.add_parser(
    'delete',
    help='Delete an existing expense',
    description='Delete an expense by its ID.'
)
parser_delete.add_argument(
    "-i", "--id", type=int, required=True,
    help="ID of the expense to delete (see 'list' to find IDs)"
)
parser_delete.set_defaults(func=delete)

# ============== list ============= 
parser_list = subparsers.add_parser(
    'list',
    help='List recorded expenses',
    description='List expenses in a table, optionally filtered by month and/or category.'
)
parser_list.add_argument(
    "-m", "--month", type=str,
    help="Month to filter by, as a number 1-12 (e.g. 9 for September)"
)
parser_list.add_argument(
    "-c", "--category", type=str,
    help="Category to filter by, e.g. food, transport, rent (optional; shows all categories if omitted)"
)
parser_list.set_defaults(func=list)

# ============== summary =============
parser_summary = subparsers.add_parser(
    'summary',
    help='Show total spending',
    description='Show the total amount spent, optionally filtered by month and/or category.'
)
parser_summary.add_argument(
    "-m", "--month", type=str,
    help="Month to filter by, as a number 1-12 (optional; totals across all months if omitted)"
)
parser_summary.add_argument(
    "-c", "--category", type=str,
    help="Category to filter by, e.g. food, transport, rent (optional; totals all categories if omitted)"
)
parser_summary.set_defaults(func=summary)

# ============== setlimit =============
parser_limit = subparsers.add_parser(
    'setlimit',
    help='Set a monthly spending limit',
    description="Set (or update) your monthly budget limit and warn if you've already exceeded it."
)
parser_limit.add_argument(
    "-l", "--limit", type=float, required=True,
    help="Monthly budget limit amount, e.g. 500"
)
parser_limit.set_defaults(func=setlimit)

# ============== expense_csv =============
parser_csv = subparsers.add_parser(
    'expense_csv',
    help='Export expenses to a CSV file',
    description="Export expenses to 'expense.csv', optionally filtered by month."
)
parser_csv.add_argument(
    '-m', '--month', type=str,
    help='Month to filter by, as a number 1-12 (optional; exports all months if omitted)'
)
parser_csv.set_defaults(func=expense_csv)

args = parser.parse_args()
print(args.func(args))