import os
import shutil

def reorganize_workspace():
    print("=== REORGANIZING WORKSPACE ===")
    
    # 1. Create backend directory
    backend_dir = "backend"
    if not os.path.exists(backend_dir):
        os.makedirs(backend_dir)
        print(f"Created directory: {backend_dir}")
        
    # Directories to move
    dirs_to_move = ["app", "tests", "chroma_db"]
    for d in dirs_to_move:
        if os.path.exists(d):
            dest = os.path.join(backend_dir, d)
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.move(d, dest)
            print(f"Moved directory {d} to {dest}")
            
    # Files to move
    files_to_move = [
        "verify_phase1.py",
        "verify_phase2.py",
        "verify_phase3.py",
        "inspect_db.py",
        "read_docx.py",
        "requirements.txt",
        ".env",
        "prodintel.db",
        "Dockerfile"
    ]
    
    for f in files_to_move:
        if os.path.exists(f):
            dest = os.path.join(backend_dir, f)
            if os.path.exists(dest):
                os.remove(dest)
            shutil.move(f, dest)
            print(f"Moved file {f} to {dest}")
            
    print("\n✔ Workspace reorganized successfully! Backend files are consolidated under ./backend/")

if __name__ == "__main__":
    reorganize_workspace()
