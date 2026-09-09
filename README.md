# Expense Tracker

A simple command-line tool to track personal expenses — add, delete, list, summarize, and export your spending, with optional monthly budget limits.

## Requirements

- Python 3.9+

## Usage

### Add an expense
```
python main.py add -d "Coffee" -a 4.5 -c food
```
- `-d` / `--description` — short description of the expense
- `-a` / `--amount` — amount spent
- `-c` / `--category` — category (e.g. food, transport, rent)

### Delete an expense
```
python main.py delete -i 3
```
- `-i` / `--id` — ID of the expense to delete

### List expenses
```
python main.py list -m 9
```
- `-m` / `--month` — month to filter by (1–12)
- `-c` / `--category` — optional category filter

### View a spending summary
```
python main.py summary -m 9 -c food
```
- `-m` / `--month` — optional month filter
- `-c` / `--category` — optional category filter

### Set a monthly budget limit
```
python main.py setlimit -l 500
```
- `-l` / `--limit` — your monthly budget amount; you'll get a warning if you've already exceeded it

### Export to CSV
```
python main.py expense_csv -m 9
```
- `-m` / `--month` — optional month filter
- Exports to `expense.csv` in the current folder

## Data storage

Expense records and budget data are stored locally in `data.json`, `expenses.json`, and `limit.json`. These files are excluded from version control via `.gitignore` since they contain your personal financial data.

## License

MIT
