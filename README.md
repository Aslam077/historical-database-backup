# Historical Database Backup Tool

A Python-based MySQL backup tool that creates **date-wise historical snapshots** of selected database tables.

The tool reads database connection details and backup settings from `config.json`, automatically creates the historical database and tables, stores each snapshot with a `date_id`, and removes older snapshots when the configured retention limit is exceeded.

---

## Features

* Date-wise database snapshots
* Backup multiple MySQL tables
* Tables configurable through `config.json`
* Database connection configurable through `config.json`
* Automatically creates the historical database
* Automatically creates historical tables
* Automatically creates a `date` table
* Adds `date_id` to every historical record
* Prevents duplicate backup for the same date
* Configurable snapshot retention limit
* Automatically deletes the oldest snapshots when the limit is exceeded
* Keeps the latest N snapshots only

---

# Project Structure

```text
Historical Database Project/
│
├── backup.py
├── config.json
├── requirements.txt
└── README.md
```

---

# Requirements

Before using this tool, make sure the following are installed:

* Python 3.x
* MySQL Server
* MySQL database
* MySQL user with appropriate permissions

The Python dependency is listed in `requirements.txt`.

---

# Installation

Open Command Prompt or Terminal inside the project folder.

Install the required Python package:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file contains:

```text
mysql-connector-python
```

---

# Configuration

All database information and backup settings are stored in `config.json`.

Example:

```json
{
    "snapshot_limit": 3,

    "database": {
        "host": "localhost",
        "port": 3306,
        "user": "root",
        "password": "your_password",
        "source_database": "ecommerce_db",
        "history_database": "ecommerce_history"
    },

    "backup_tables": [
        "customers",
        "products",
        "orders",
        "order_items"
    ]
}
```

---

# Configuration Parameters

## `snapshot_limit`

Defines how many historical snapshots should be retained.

Example:

```json
"snapshot_limit": 3
```

This means the historical database will keep only the **latest 3 snapshots**.

When a new snapshot causes the limit to be exceeded, the oldest snapshot is automatically deleted.

---

## Database Configuration

| Parameter          | Description                                        |
| ------------------ | -------------------------------------------------- |
| `host`             | MySQL server hostname or IP address                |
| `port`             | MySQL server port, normally `3306`                 |
| `user`             | MySQL username                                     |
| `password`         | MySQL password                                     |
| `source_database`  | Database containing the original/source tables     |
| `history_database` | Database where historical snapshots will be stored |

Example:

```json
"database": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "your_password",
    "source_database": "ecommerce_db",
    "history_database": "ecommerce_history"
}
```

---

# Backup Tables

The tables to be backed up are specified in the `backup_tables` list.

Example:

```json
"backup_tables": [
    "customers",
    "products",
    "orders",
    "order_items"
]
```

To add another table:

```json
"backup_tables": [
    "customers",
    "products",
    "orders",
    "order_items",
    "payments"
]
```

The Python script will automatically process the configured tables.

> Make sure the configured tables exist in the source database before running the backup.

---

# How the Backup Works

The backup process follows these steps:

```text
                config.json
                     │
                     ▼
                 backup.py
                     │
                     ▼
             Connect to MySQL
                     │
                     ▼
          Create/Get snapshot date
                     │
                     ▼
                Get date_id
                     │
                     ▼
          Read configured tables
                     │
                     ▼
       Create historical tables if needed
                     │
                     ▼
          Copy source table records
                     │
                     ▼
        Add date_id to every record
                     │
                     ▼
          Apply snapshot retention
                     │
                     ▼
          Delete old snapshots
                     │
                     ▼
             Backup completed
```

---

# Historical Database Structure

The tool creates a separate historical database.

For example:

```text
ecommerce_db
│
├── customers
├── products
├── orders
└── order_items
```

The historical database:

```text
ecommerce_history
│
├── date
├── customers
├── products
├── orders
└── order_items
```

The historical tables contain an additional `date_id` column.

---

# Date Table

The historical database contains a special `date` table:

```sql
CREATE TABLE `date` (
    date_id BIGINT PRIMARY KEY AUTO_INCREMENT,
    `date` DATE NOT NULL UNIQUE
);
```

Example:

```text
date_id    date
-------    ----------
1          2026-09-09
2          2026-09-10
3          2026-09-11
```

Each backup date receives a unique `date_id`.

That `date_id` is stored with every record in the historical tables.

---

# Snapshot Example

Suppose the configuration contains:

```json
"snapshot_limit": 3
```

The first three backup runs produce:

```text
Snapshot 1 → 2026-09-09
Snapshot 2 → 2026-09-10
Snapshot 3 → 2026-09-11
```

The historical database contains:

```text
2026-09-09
2026-09-10
2026-09-11
```

When the next backup runs:

```text
Snapshot 4 → 2026-09-12
```

The retention limit is now exceeded.

The oldest snapshot:

```text
2026-09-09
```

is automatically deleted.

The database will contain:

```text
2026-09-10
2026-09-11
2026-09-12
```

The same old snapshot is removed from **all configured historical tables**.

---

# Rolling Snapshot Retention

The retention policy works like this:

| Backup Run | New Snapshot | Snapshots Retained     |
| ---------: | ------------ | ---------------------- |
|          1 | Sep 9        | Sep 9                  |
|          2 | Sep 10       | Sep 9, Sep 10          |
|          3 | Sep 11       | Sep 9, Sep 10, Sep 11  |
|          4 | Sep 12       | Sep 10, Sep 11, Sep 12 |
|          5 | Sep 13       | Sep 11, Sep 12, Sep 13 |

If:

```json
"snapshot_limit": 3
```

the database will always retain the latest three snapshots.

---

# Running the Backup

After configuring `config.json`, run:

```bash
python backup.py
```

Example output:

```text
==========================================
   Historical Database Backup Tool
==========================================

Starting database backup...
Snapshot limit: 3

Source database connected: ecommerce_db
Historical database connected: ecommerce_history

Today's date_id: 2

Processing table: customers
Backed up 4 rows from customers

Processing table: products
Backed up 5 rows from products

Processing table: orders
Backed up 4 rows from orders

Processing table: order_items
Backed up 6 rows from order_items

Applying snapshot retention policy...

Snapshot limit is 3. No old snapshots to delete.

Backup completed successfully.
==========================================
```

---

# Duplicate Snapshot Protection

The tool checks whether a snapshot for the current backup date already exists.

If the same date is processed again, the backup is skipped to prevent duplicate data.

Example:

```text
Snapshot for this date already exists.
Backup skipped to prevent duplicate data.
```

---

# Testing With a Fixed Date

For testing, `backup.py` can use a fixed date:

```python
today = date(2026, 9, 10)
```

You can change the date manually to simulate different backup days.

For example:

```python
today = date(2026, 9, 11)
```

Run:

```bash
python backup.py
```

Then change it again:

```python
today = date(2026, 9, 12)
```

This allows you to test the snapshot retention functionality without waiting for actual days to pass.

---

# Production Date

After testing is complete, change the fixed test date:

```python
today = date(2026, 9, 10)
```

to:

```python
today = date.today()
```

The tool will then automatically use the current system date for each backup.

---

# Verify Snapshots in MySQL

Select the historical database:

```sql
USE ecommerce_history;
```

Check available snapshots:

```sql
SELECT *
FROM `date`
ORDER BY `date`;
```

Check the number of records for each snapshot:

```sql
SELECT
    date_id,
    COUNT(*) AS record_count
FROM customers
GROUP BY date_id
ORDER BY date_id;
```

To view records from a specific snapshot:

```sql
SELECT *
FROM customers
WHERE date_id = 2;
```

---

# Important Notes

### 1. Source Database

The source database must already exist.

Example:

```text
ecommerce_db
```

### 2. Historical Database

You do not need to manually create the historical database.

The Python script creates it automatically if it does not exist.

### 3. Historical Tables

You do not need to manually create the historical tables.

The script creates them automatically based on the source tables.

### 4. Database Permissions

The MySQL user must have sufficient permissions to:

* Read source tables
* Create the historical database
* Create historical tables
* Insert historical records
* Delete old historical records

### 5. Backup Limit

`snapshot_limit` must be a positive number.

Example:

```json
"snapshot_limit": 3
```

Avoid setting it to `0`.

### 6. Password Security

Do not commit a real database password to a public GitHub repository.

For example, avoid publishing:

```json
"password": "MyRealPassword123"
```

Use an appropriate secret-management method when deploying this tool in a real environment.

---

# Troubleshooting

## `ModuleNotFoundError: No module named 'mysql'`

Run:

```bash
pip install -r requirements.txt
```

---

## MySQL Connection Error

Check:

* MySQL Server is running
* Host is correct
* Port is correct
* Username is correct
* Password is correct
* MySQL user has the required permissions

---

## Table Does Not Exist

Check:

```json
"backup_tables": [
    "customers",
    "products",
    "orders",
    "order_items"
]
```

Make sure these tables exist in the configured `source_database`.

---

## Backup Already Exists

If you see:

```text
Snapshot for this date already exists.
Backup skipped to prevent duplicate data.
```

the script has already created a snapshot for that date.

Change the test date if you are testing multiple snapshots.

---

# Future Improvements

Possible improvements for future versions include:

* Backup logging
* Snapshot status (`STARTED`, `COMPLETED`, `FAILED`)
* Error logging
* Transaction-based backup
* Email notifications
* Automatic daily scheduling
* Command-line options
* Incremental/delta backups
* Backup compression
* Encryption
* Better handling of table schema changes
* Detailed backup reports

---

# Summary

This tool provides a configurable historical snapshot mechanism for MySQL databases.

The user only needs to configure:

```text
1. Database connection
2. Source database
3. Historical database
4. Tables to backup
5. Snapshot retention limit
```

The tool then automatically:

```text
Read configuration
       ↓
Connect to source database
       ↓
Create historical database
       ↓
Create historical tables
       ↓
Create snapshot date
       ↓
Copy table data
       ↓
Store date_id with records
       ↓
Check snapshot limit
       ↓
Delete oldest snapshots if required
       ↓
Backup completed
```
