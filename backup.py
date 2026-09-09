# import json
# import mysql.connector
# from datetime import date


# # ============================================================
# # 1. LOAD CONFIGURATION
# # ============================================================

# def load_config():

    # with open("config.json", "r") as file:
        # return json.load(file)


# # ============================================================
# # 2. CREATE DATABASE CONNECTION
# # ============================================================

# def create_connection(db_config, database=None):

    # connection = mysql.connector.connect(
        # host=db_config["host"],
        # port=db_config["port"],
        # user=db_config["user"],
        # password=db_config["password"],
        # database=database
    # )

    # return connection


# # ============================================================
# # 3. CREATE HISTORICAL DATABASE
# # ============================================================

# def create_history_database(connection, history_database):

    # cursor = connection.cursor()

    # cursor.execute(
        # f"CREATE DATABASE IF NOT EXISTS `{history_database}`"
    # )

    # connection.commit()

    # cursor.close()


# # ============================================================
# # 4. CREATE DATE TABLE
# # ============================================================

# def create_date_table(connection):

    # cursor = connection.cursor()

    # query = """
    # CREATE TABLE IF NOT EXISTS `date` (
        # date_id BIGINT PRIMARY KEY AUTO_INCREMENT,
        # `date` DATE NOT NULL UNIQUE
    # )
    # """

    # cursor.execute(query)

    # connection.commit()

    # cursor.close()


# # ============================================================
# # 5. GET DATE ID
# # ============================================================

# def get_date_id(connection):

    # # --------------------------------------------------------
    # # FOR TESTING
    # # --------------------------------------------------------
    # # today = date(2026, 9, 11)

    # # --------------------------------------------------------
    # # FOR ACTUAL DAILY BACKUP USE:
    # #
    # today = date.today()
    # # --------------------------------------------------------

    # cursor = connection.cursor()

    # cursor.execute(
        # """
        # SELECT date_id
        # FROM `date`
        # WHERE `date` = %s
        # """,
        # (today,)
    # )

    # result = cursor.fetchone()

    # if result:

        # date_id = result[0]

    # else:

        # cursor.execute(
            # """
            # INSERT INTO `date` (`date`)
            # VALUES (%s)
            # """,
            # (today,)
        # )

        # connection.commit()

        # date_id = cursor.lastrowid

    # cursor.close()

    # return date_id


# # ============================================================
# # 6. GET SOURCE TABLE COLUMNS
# # ============================================================

# def get_columns(connection, table_name):

    # cursor = connection.cursor()

    # cursor.execute(
        # f"SHOW COLUMNS FROM `{table_name}`"
    # )

    # columns = cursor.fetchall()

    # cursor.close()

    # return columns


# # ============================================================
# # 7. CREATE HISTORICAL TABLE
# # ============================================================

# def create_history_table(
    # history_connection,
    # source_connection,
    # table_name
# ):

    # cursor = history_connection.cursor()

    # # Check whether table already exists
    # cursor.execute(
        # f"SHOW TABLES LIKE '{table_name}'"
    # )

    # exists = cursor.fetchone()

    # if exists:

        # cursor.close()

        # return

    # # Get source table structure
    # columns = get_columns(
        # source_connection,
        # table_name
    # )

    # column_definitions = []

    # for column in columns:

        # column_name = column[0]
        # column_type = column[1]

        # column_definitions.append(
            # f"`{column_name}` {column_type}"
        # )

    # # Add snapshot_id
    # column_definitions.insert(
        # 0,
        # "`snapshot_id` BIGINT AUTO_INCREMENT PRIMARY KEY"
    # )

    # # Add date_id
    # column_definitions.append(
        # "`date_id` BIGINT NOT NULL"
    # )

    # create_query = f"""
    # CREATE TABLE `{table_name}` (
        # {', '.join(column_definitions)
    # }
    # """

    # cursor.execute(create_query)

    # history_connection.commit()

    # cursor.close()

    # print(
        # f"Created historical table: {table_name}"
    # )


# # ============================================================
# # 8. CHECK WHETHER SNAPSHOT ALREADY EXISTS
# # ============================================================

# def snapshot_exists(
    # history_connection,
    # table_name,
    # date_id
# ):

    # cursor = history_connection.cursor()

    # query = f"""
    # SELECT COUNT(*)
    # FROM `{table_name}`
    # WHERE date_id = %s
    # """

    # cursor.execute(
        # query,
        # (date_id,)
    # )

    # count = cursor.fetchone()[0]

    # cursor.close()

    # return count > 0


# # ============================================================
# # 9. BACKUP TABLE
# # ============================================================

# def backup_table(
    # source_connection,
    # history_connection,
    # table_name,
    # date_id
# ):

    # source_cursor = source_connection.cursor()

    # history_cursor = history_connection.cursor()

    # # --------------------------------------------------------
    # # Get source columns
    # # --------------------------------------------------------

    # columns = get_columns(
        # source_connection,
        # table_name
    # )

    # column_names = [
        # column[0]
        # for column in columns
    # ]

    # source_columns = ", ".join(
        # f"`{column}`"
        # for column in column_names
    # )

    # history_columns = ", ".join(
        # f"`{column}`"
        # for column in column_names
    # )

    # history_columns += ", `date_id`"

    # # --------------------------------------------------------
    # # Read source data
    # # --------------------------------------------------------

    # source_cursor.execute(
        # f"""
        # SELECT {source_columns}
        # FROM `{table_name}`
        # """
    # )

    # rows = source_cursor.fetchall()

    # if not rows:

        # print(
            # f"No data found in table: {table_name}"
        # )

        # source_cursor.close()
        # history_cursor.close()

        # return 0

    # # --------------------------------------------------------
    # # Prepare INSERT query
    # # --------------------------------------------------------

    # placeholders = ", ".join(
        # ["%s"] * (len(column_names) + 1)
    # )

    # insert_query = f"""
    # INSERT INTO `{table_name}`
    # ({history_columns})
    # VALUES ({placeholders})
    # """

    # # --------------------------------------------------------
    # # Add date_id to every row
    # # --------------------------------------------------------

    # rows_with_date = [
        # tuple(row) + (date_id,)
        # for row in rows
    # ]

    # # --------------------------------------------------------
    # # Insert snapshot
    # # --------------------------------------------------------

    # history_cursor.executemany(
        # insert_query,
        # rows_with_date
    # )

    # history_connection.commit()

    # source_cursor.close()
    # history_cursor.close()

    # print(
        # f"Backed up {len(rows)} rows from {table_name}"
    # )

    # return len(rows)


# # ============================================================
# # 10. DELETE OLD SNAPSHOTS
# # ============================================================

# def apply_snapshot_limit(
    # connection,
    # tables,
    # snapshot_limit
# ):

    # cursor = connection.cursor()

    # # --------------------------------------------------------
    # # Get all snapshot dates
    # # Oldest → Newest
    # # --------------------------------------------------------

    # cursor.execute(
        # """
        # SELECT date_id, `date`
        # FROM `date`
        # ORDER BY `date` ASC
        # """
    # )

    # snapshots = cursor.fetchall()

    # # --------------------------------------------------------
    # # If snapshots are within the limit, do nothing
    # # --------------------------------------------------------

    # if len(snapshots) <= snapshot_limit:

        # cursor.close()

        # print(
            # f"Snapshot limit is {snapshot_limit}. "
            # f"No old snapshots to delete."
        # )

        # return

    # # --------------------------------------------------------
    # # Find snapshots exceeding the limit
    # # --------------------------------------------------------

    # snapshots_to_delete = snapshots[:-snapshot_limit]

    # print(
        # f"\nSnapshot limit exceeded."
    # )

    # print(
        # f"Snapshots to delete: "
        # f"{len(snapshots_to_delete)}"
    # )

    # # --------------------------------------------------------
    # # Delete old snapshots
    # # --------------------------------------------------------

    # for date_id, snapshot_date in snapshots_to_delete:

        # print(
            # f"Deleting snapshot: "
            # f"{snapshot_date} "
            # f"(date_id={date_id})"
        # )

        # # Delete rows from every historical table
        # for table_name in tables:

            # cursor.execute(
                # f"""
                # DELETE FROM `{table_name}`
                # WHERE date_id = %s
                # """,
                # (date_id,)
            # )

        # # Delete date record
        # cursor.execute(
            # """
            # DELETE FROM `date`
            # WHERE date_id = %s
            # """,
            # (date_id,)
        # )

    # connection.commit()

    # cursor.close()

    # print(
        # "Old snapshots deleted successfully."
    # )


# # ============================================================
# # 11. MAIN FUNCTION
# # ============================================================

# def main():

    # print(
        # "=========================================="
    # )

    # print(
        # "   Historical Database Backup Tool"
    # )

    # print(
        # "=========================================="
    # )

    # print(
        # "\nStarting database backup..."
    # )

    # # --------------------------------------------------------
    # # Load configuration
    # # --------------------------------------------------------

    # config = load_config()

    # db_config = config["database"]

    # tables = config["backup_tables"]

    # snapshot_limit = config["snapshot_limit"]

    # print(
        # f"Snapshot limit: {snapshot_limit}"
    # )

    # # --------------------------------------------------------
    # # Connect to source database
    # # --------------------------------------------------------

    # source_connection = create_connection(
        # db_config,
        # db_config["source_database"]
    # )

    # print(
        # f"Source database connected: "
        # f"{db_config['source_database']}"
    # )

    # # --------------------------------------------------------
    # # Connect without selecting database
    # # --------------------------------------------------------

    # base_connection = create_connection(
        # db_config
    # )

    # history_database = db_config[
        # "history_database"
    # ]

    # # --------------------------------------------------------
    # # Create historical database
    # # --------------------------------------------------------

    # create_history_database(
        # base_connection,
        # history_database
    # )

    # base_connection.close()

    # # --------------------------------------------------------
    # # Connect to historical database
    # # --------------------------------------------------------

    # history_connection = create_connection(
        # db_config,
        # history_database
    # )

    # print(
        # f"Historical database connected: "
        # f"{history_database}"
    # )

    # # --------------------------------------------------------
    # # Create date table
    # # --------------------------------------------------------

    # create_date_table(
        # history_connection
    # )

    # # --------------------------------------------------------
    # # Get date_id
    # # --------------------------------------------------------

    # date_id = get_date_id(
        # history_connection
    # )

    # print(
        # f"Today's date_id: {date_id}"
    # )

    # # --------------------------------------------------------
    # # Check whether today's snapshot already exists
    # # --------------------------------------------------------

    # snapshot_already_exists = False

    # for table_name in tables:

        # if snapshot_exists(
            # history_connection,
            # table_name,
            # date_id
        # ):

            # snapshot_already_exists = True

            # break

    # # --------------------------------------------------------
    # # If snapshot already exists, don't backup again
    # # --------------------------------------------------------

    # if snapshot_already_exists:

        # print(
            # "\nSnapshot for this date already exists."
        # )

        # print(
            # "Backup skipped to prevent duplicate data."
        # )

    # else:

        # # ----------------------------------------------------
        # # Backup each configured table
        # # ----------------------------------------------------

        # for table_name in tables:

            # print(
                # f"\nProcessing table: {table_name}"
            # )

            # # Create historical table
            # create_history_table(
                # history_connection,
                # source_connection,
                # table_name
            # )

            # # Backup table
            # backup_table(
                # source_connection,
                # history_connection,
                # table_name,
                # date_id
            # )

        # # ----------------------------------------------------
        # # Apply snapshot retention limit
        # # ----------------------------------------------------

        # print(
            # "\nApplying snapshot retention policy..."
        # )

        # apply_snapshot_limit(
            # history_connection,
            # tables,
            # snapshot_limit
        # )

    # # --------------------------------------------------------
    # # Close connections
    # # --------------------------------------------------------

    # source_connection.close()

    # history_connection.close()

    # print(
        # "\nBackup completed successfully."
    # )

    # print(
        # "=========================================="
    # )


# # ============================================================
# # 12. RUN PROGRAM
# # ============================================================

# if __name__ == "__main__":

    # main()
    
    
    
    
    
    
    
    
    
    
    
    
    
    





import json
import mysql.connector
from datetime import date
import sys


# ============================================================
# 1. LOAD CONFIGURATION
# ============================================================

def load_config():
    try:
        with open("config.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("ERROR: config.json file not found!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in config.json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Unexpected error loading config: {e}")
        sys.exit(1)


# ============================================================
# 2. CREATE DATABASE CONNECTION
# ============================================================

def create_connection(db_config, database=None):
    try:
        connection = mysql.connector.connect(
            host=db_config["host"],
            port=db_config["port"],
            user=db_config["user"],
            password=db_config["password"],
            database=database
        )
        return connection
    except mysql.connector.Error as err:
        print(f"ERROR: Database connection failed: {err}")
        sys.exit(1)
    except KeyError as err:
        print(f"ERROR: Missing configuration key: {err}")
        sys.exit(1)
    except Exception as err:
        print(f"ERROR: Unexpected connection error: {err}")
        sys.exit(1)


# ============================================================
# 3. CREATE HISTORICAL DATABASE
# ============================================================

def create_history_database(connection, history_database):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{history_database}`"
        )
        connection.commit()
        print(f"Historical database '{history_database}' ready.")
    except mysql.connector.Error as err:
        print(f"ERROR: Failed to create database '{history_database}': {err}")
        raise
    except Exception as err:
        print(f"ERROR: Unexpected error creating database: {err}")
        raise
    finally:
        if cursor:
            cursor.close()


# ============================================================
# 4. CREATE DATE TABLE
# ============================================================

def create_date_table(connection):
    cursor = None
    try:
        cursor = connection.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS `date` (
            date_id BIGINT PRIMARY KEY AUTO_INCREMENT,
            `date` DATE NOT NULL UNIQUE
        )
        """
        cursor.execute(query)
        connection.commit()
    except mysql.connector.Error as err:
        print(f"ERROR: Failed to create date table: {err}")
        raise
    except Exception as err:
        print(f"ERROR: Unexpected error creating date table: {err}")
        raise
    finally:
        if cursor:
            cursor.close()


# ============================================================
# 5. GET DATE ID
# ============================================================

def get_date_id(connection):
    # --------------------------------------------------------
    # FOR TESTING
    # --------------------------------------------------------
    today = date(2026, 9, 12)

    # --------------------------------------------------------
    # FOR ACTUAL DAILY BACKUP USE:
    #
    # today = date.today()
    # --------------------------------------------------------

    cursor = None
    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT date_id
            FROM `date`
            WHERE `date` = %s
            """,
            (today,)
        )

        result = cursor.fetchone()

        if result:
            date_id = result[0]
        else:
            cursor.execute(
                """
                INSERT INTO `date` (`date`)
                VALUES (%s)
                """,
                (today,)
            )
            connection.commit()
            date_id = cursor.lastrowid

        return date_id

    except mysql.connector.Error as err:
        print(f"ERROR: Failed to get/create date_id: {err}")
        raise
    except Exception as err:
        print(f"ERROR: Unexpected error in get_date_id: {err}")
        raise
    finally:
        if cursor:
            cursor.close()


# ============================================================
# 6. GET SOURCE TABLE COLUMNS
# ============================================================

def get_columns(connection, table_name):
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
        columns = cursor.fetchall()
        return columns
    except mysql.connector.Error as err:
        print(f"ERROR: Failed to get columns for table '{table_name}': {err}")
        raise
    except Exception as err:
        print(f"ERROR: Unexpected error getting columns: {err}")
        raise
    finally:
        if cursor:
            cursor.close()


# ============================================================
# 7. CREATE HISTORICAL TABLE
# ============================================================

def create_history_table(history_connection, source_connection, table_name):
    cursor = None
    try:
        cursor = history_connection.cursor()

        # Check whether table already exists
        cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
        exists = cursor.fetchone()

        if exists:
            return

        # Get source table structure
        columns = get_columns(source_connection, table_name)

        column_definitions = []

        for column in columns:
            column_name = column[0]
            column_type = column[1]
            column_definitions.append(f"`{column_name}` {column_type}")

        # Add snapshot_id
        column_definitions.insert(0, "`snapshot_id` BIGINT AUTO_INCREMENT PRIMARY KEY")

        # Add date_id
        column_definitions.append("`date_id` BIGINT NOT NULL")

        create_query = f"""
        CREATE TABLE `{table_name}` (
            {', '.join(column_definitions)}
        )
        """

        cursor.execute(create_query)
        history_connection.commit()

        print(f"Created historical table: {table_name}")

    except mysql.connector.Error as err:
        print(f"ERROR: Failed to create historical table '{table_name}': {err}")
        if not history_connection.in_transaction:
            history_connection.rollback()
        raise
    except Exception as err:
        print(f"ERROR: Unexpected error creating historical table: {err}")
        if not history_connection.in_transaction:
            history_connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()


# ============================================================
# 8. CHECK WHETHER SNAPSHOT ALREADY EXISTS
# ============================================================

def snapshot_exists(history_connection, table_name, date_id):
    cursor = None
    try:
        cursor = history_connection.cursor()
        query = f"""
        SELECT COUNT(*)
        FROM `{table_name}`
        WHERE date_id = %s
        """
        cursor.execute(query, (date_id,))
        count = cursor.fetchone()[0]
        return count > 0
    except mysql.connector.Error as err:
        print(f"ERROR: Failed to check snapshot existence in '{table_name}': {err}")
        raise
    except Exception as err:
        print(f"ERROR: Unexpected error checking snapshot: {err}")
        raise
    finally:
        if cursor:
            cursor.close()


# ============================================================
# 9. BACKUP TABLE
# ============================================================

def backup_table(source_connection, history_connection, table_name, date_id):
    source_cursor = None
    history_cursor = None
    
    try:
        source_cursor = source_connection.cursor()
        history_cursor = history_connection.cursor()

        # --------------------------------------------------------
        # Get source columns
        # --------------------------------------------------------
        columns = get_columns(source_connection, table_name)
        column_names = [column[0] for column in columns]

        source_columns = ", ".join(f"`{column}`" for column in column_names)
        history_columns = ", ".join(f"`{column}`" for column in column_names)
        history_columns += ", `date_id`"

        # --------------------------------------------------------
        # Read source data
        # --------------------------------------------------------
        source_cursor.execute(f"""
            SELECT {source_columns}
            FROM `{table_name}`
        """)

        rows = source_cursor.fetchall()

        if not rows:
            print(f"No data found in table: {table_name}")
            return 0

        # --------------------------------------------------------
        # Prepare INSERT query
        # --------------------------------------------------------
        placeholders = ", ".join(["%s"] * (len(column_names) + 1))

        insert_query = f"""
        INSERT INTO `{table_name}`
        ({history_columns})
        VALUES ({placeholders})
        """

        # --------------------------------------------------------
        # Add date_id to every row
        # --------------------------------------------------------
        rows_with_date = [tuple(row) + (date_id,) for row in rows]

        # --------------------------------------------------------
        # Insert snapshot
        # --------------------------------------------------------
        # Use autocommit or manual commit without start_transaction
        # since we're using executemany which may already handle it
        history_cursor.executemany(insert_query, rows_with_date)
        history_connection.commit()

        row_count = len(rows)
        print(f"Backed up {row_count} rows from {table_name}")
        return row_count

    except mysql.connector.Error as err:
        print(f"ERROR: Backup failed for table '{table_name}': {err}")
        try:
            history_connection.rollback()
        except:
            pass
        raise
    except Exception as err:
        print(f"ERROR: Unexpected error during backup of '{table_name}': {err}")
        try:
            history_connection.rollback()
        except:
            pass
        raise
    finally:
        if source_cursor:
            source_cursor.close()
        if history_cursor:
            history_cursor.close()


# ============================================================
# 10. DELETE OLD SNAPSHOTS
# ============================================================

def apply_snapshot_limit(connection, tables, snapshot_limit):
    cursor = None
    try:
        cursor = connection.cursor()

        # --------------------------------------------------------
        # Get all snapshot dates (Oldest → Newest)
        # --------------------------------------------------------
        cursor.execute("""
            SELECT date_id, `date`
            FROM `date`
            ORDER BY `date` ASC
        """)
        snapshots = cursor.fetchall()

        # --------------------------------------------------------
        # If snapshots are within the limit, do nothing
        # --------------------------------------------------------
        if len(snapshots) <= snapshot_limit:
            print(f"Snapshot limit is {snapshot_limit}. No old snapshots to delete.")
            return

        # --------------------------------------------------------
        # Find snapshots exceeding the limit
        # --------------------------------------------------------
        snapshots_to_delete = snapshots[:-snapshot_limit]

        print(f"\nSnapshot limit exceeded.")
        print(f"Snapshots to delete: {len(snapshots_to_delete)}")

        # --------------------------------------------------------
        # Delete old snapshots
        # --------------------------------------------------------
        # Check if a transaction is already in progress
        if connection.in_transaction:
            # If in transaction, just execute without starting new one
            pass
        else:
            connection.start_transaction()

        for date_id, snapshot_date in snapshots_to_delete:
            print(f"Deleting snapshot: {snapshot_date} (date_id={date_id})")

            # Delete rows from every historical table
            for table_name in tables:
                cursor.execute(
                    f"""
                    DELETE FROM `{table_name}`
                    WHERE date_id = %s
                    """,
                    (date_id,)
                )

            # Delete date record
            cursor.execute(
                """
                DELETE FROM `date`
                WHERE date_id = %s
                """,
                (date_id,)
            )

        connection.commit()
        print("Old snapshots deleted successfully.")

    except mysql.connector.Error as err:
        print(f"ERROR: Failed to apply snapshot limit: {err}")
        try:
            connection.rollback()
        except:
            pass
        raise
    except Exception as err:
        print(f"ERROR: Unexpected error applying snapshot limit: {err}")
        try:
            connection.rollback()
        except:
            pass
        raise
    finally:
        if cursor:
            cursor.close()


# ============================================================
# 11. MAIN FUNCTION
# ============================================================

def main():
    try:
        print("==========================================")
        print("   Historical Database Backup Tool")
        print("==========================================")
        print("\nStarting database backup...")

        # --------------------------------------------------------
        # Load configuration
        # --------------------------------------------------------
        config = load_config()
        db_config = config["database"]
        tables = config["backup_tables"]
        snapshot_limit = config["snapshot_limit"]

        print(f"Snapshot limit: {snapshot_limit}")

        # --------------------------------------------------------
        # Connect to source database
        # --------------------------------------------------------
        source_connection = create_connection(db_config, db_config["source_database"])
        print(f"Source database connected: {db_config['source_database']}")

        # --------------------------------------------------------
        # Connect without selecting database
        # --------------------------------------------------------
        base_connection = create_connection(db_config)
        history_database = db_config["history_database"]

        # --------------------------------------------------------
        # Create historical database
        # --------------------------------------------------------
        create_history_database(base_connection, history_database)
        base_connection.close()

        # --------------------------------------------------------
        # Connect to historical database
        # --------------------------------------------------------
        history_connection = create_connection(db_config, history_database)
        print(f"Historical database connected: {history_database}")

        # --------------------------------------------------------
        # Create date table
        # --------------------------------------------------------
        create_date_table(history_connection)

        # --------------------------------------------------------
        # Get date_id
        # --------------------------------------------------------
        date_id = get_date_id(history_connection)
        print(f"Today's date_id: {date_id}")

        # --------------------------------------------------------
        # Check whether today's snapshot already exists
        # --------------------------------------------------------
        snapshot_already_exists = False
        for table_name in tables:
            if snapshot_exists(history_connection, table_name, date_id):
                snapshot_already_exists = True
                break

        # --------------------------------------------------------
        # If snapshot already exists, don't backup again
        # --------------------------------------------------------
        if snapshot_already_exists:
            print("\nSnapshot for this date already exists.")
            print("Backup skipped to prevent duplicate data.")
        else:
            # ----------------------------------------------------
            # Backup each configured table
            # ----------------------------------------------------
            for table_name in tables:
                print(f"\nProcessing table: {table_name}")
                
                # Create historical table
                create_history_table(history_connection, source_connection, table_name)
                
                # Backup table
                backup_table(source_connection, history_connection, table_name, date_id)

            # ----------------------------------------------------
            # Apply snapshot retention limit
            # ----------------------------------------------------
            print("\nApplying snapshot retention policy...")
            apply_snapshot_limit(history_connection, tables, snapshot_limit)

        # --------------------------------------------------------
        # Close connections
        # --------------------------------------------------------
        source_connection.close()
        history_connection.close()

        print("\nBackup completed successfully.")
        print("==========================================")

    except KeyboardInterrupt:
        print("\n\nBackup interrupted by user.")
        print("==========================================")
        sys.exit(1)
    except Exception as err:
        print(f"\nERROR: Backup failed: {err}")
        print("==========================================")
        sys.exit(1)


# ============================================================
# 12. RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()