import sqlite3
import json

def inspect_database():
    conn = sqlite3.connect("prodintel.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Print Table Names
    print("=== SQLITE TABLES ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for t in tables:
        print(f" - {t['name']}")
    
    # 2. Print Document Count
    print("\n=== DOCUMENTS COUNT ===")
    try:
        cursor.execute("SELECT COUNT(*) FROM documents")
        count = cursor.fetchone()[0]
        print(f"Total Documents: {count}")
    except Exception as e:
        print(f"Error querying documents: {e}")

    # 3. Print Session Memories
    print("\n=== PERSISTED SESSION MEMORIES ===")
    try:
        cursor.execute("SELECT * FROM memory")
        memories = cursor.fetchall()
        if not memories:
            print("No memory records found.")
        else:
            print(f"{'SESSION ID':<20} | {'TYPE':<12} | {'CONTENT'}")
            print("-" * 70)
            for m in memories:
                # Content is stored as a JSON string, let's load it
                try:
                    content_val = json.loads(m["content"])
                except Exception:
                    content_val = m["content"]
                print(f"{m['session_id']:<20} | {m['type']:<12} | {content_val}")
    except Exception as e:
        print(f"Error querying memory table: {e}")

    conn.close()

if __name__ == "__main__":
    inspect_database()
