from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import os
import hashlib
import uuid

from database import get_db, init_db, User, Message, OnlineUser

app = FastAPI()

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    print("✅ Database initialized!")

# Allow all origins for testing; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set your storage directory here
STORAGE_DIR = os.getenv("STORAGE_DIR", "./storage")
CHAT_FILES_DIR = "./chat_files"

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(CHAT_FILES_DIR, exist_ok=True)

# Pydantic models
class UserSignup(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class MessageCreate(BaseModel):
    from_user: str
    to_user: str
    message: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None

class MessageEdit(BaseModel):
    message: str

class BanUser(BaseModel):
    username: str

class ChangePassword(BaseModel):
    username: str
    new_password: str

class MakeAdmin(BaseModel):
    username: str
    secret_key: str = "admin_secret_2026"

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

# Authentication endpoints
@app.post("/signup")
def signup(user: UserSignup, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user
    hashed_pw = hash_password(user.password)
    new_user = User(
        username=user.username,
        password=hashed_pw,
        plain_password=user.password,  # Remove in production
        is_admin=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User created successfully", "username": user.username}

@app.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Find user
    db_user = get_user_by_username(db, user.username)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Check if banned
    if db_user.is_banned:
        raise HTTPException(status_code=403, detail="User is banned")
    
    # Verify password
    if db_user.password != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "message": "Login successful",
        "username": user.username,
        "admin": db_user.is_admin
    }

@app.post("/logout/{username}")
def logout(username: str, db: Session = Depends(get_db)):
    # Remove from online users
    online_user = db.query(OnlineUser).join(User).filter(User.username == username).first()
    if online_user:
        db.delete(online_user)
        db.commit()
    
    return {"message": "Logged out successfully"}

# Heartbeat for online status
@app.post("/heartbeat/{username}")
def heartbeat(username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update or create online status
    online_user = db.query(OnlineUser).filter(OnlineUser.user_id == user.id).first()
    if online_user:
        online_user.last_heartbeat = datetime.utcnow()
    else:
        online_user = OnlineUser(user_id=user.id, last_heartbeat=datetime.utcnow())
        db.add(online_user)
    
    db.commit()
    return {"status": "ok"}

# Get online users
@app.get("/all_online_status")
def get_online_status(db: Session = Depends(get_db)):
    # Consider users online if heartbeat within last 30 seconds
    cutoff_time = datetime.utcnow() - timedelta(seconds=30)
    
    online_users = db.query(User.username).join(OnlineUser).filter(
        OnlineUser.last_heartbeat >= cutoff_time
    ).all()
    
    return {username: True for username, in online_users}

# Messaging endpoints
@app.post("/send_message")
def send_message(msg: MessageCreate, db: Session = Depends(get_db)):
    # Get user IDs
    from_user = get_user_by_username(db, msg.from_user)
    to_user = get_user_by_username(db, msg.to_user)
    
    if not from_user or not to_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create message
    new_message = Message(
        id=str(uuid.uuid4()),
        from_user_id=from_user.id,
        to_user_id=to_user.id,
        message=msg.message,
        file_url=msg.file_url,
        file_name=msg.file_name,
        file_type=msg.file_type,
        timestamp=datetime.utcnow()
    )
    db.add(new_message)
    db.commit()
    
    return {"message": "Message sent", "id": new_message.id}

@app.get("/get_messages/{from_user}/{to_user}")
def get_messages(from_user: str, to_user: str, db: Session = Depends(get_db)):
    # Get user IDs
    user1 = get_user_by_username(db, from_user)
    user2 = get_user_by_username(db, to_user)
    
    if not user1 or not user2:
        return []
    
    # Get messages between the two users
    messages = db.query(Message).filter(
        ((Message.from_user_id == user1.id) & (Message.to_user_id == user2.id) & (Message.deleted_for_sender == False) & (Message.deleted_for_everyone == False)) |
        ((Message.from_user_id == user2.id) & (Message.to_user_id == user1.id) & (Message.deleted_for_receiver == False) & (Message.deleted_for_everyone == False))
    ).order_by(Message.timestamp).all()
    
    # Format response
    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.from_user_id).first()
        receiver = db.query(User).filter(User.id == msg.to_user_id).first()
        
        result.append({
            "id": msg.id,
            "from_user": sender.username,
            "to_user": receiver.username,
            "message": msg.message,
            "file_url": msg.file_url,
            "file_name": msg.file_name,
            "file_type": msg.file_type,
            "timestamp": msg.timestamp.isoformat(),
            "edited": msg.edited
        })
    
    return result

@app.get("/get_conversations/{username}")
def get_conversations(username: str, db: Session = Depends(get_db)):
    user = get_user_by_username(db, username)
    if not user:
        return []
    
    # Get all users this user has messaged with
    conversations = db.query(User.username).distinct().join(
        Message,
        ((Message.from_user_id == user.id) & (Message.to_user_id == User.id)) |
        ((Message.to_user_id == user.id) & (Message.from_user_id == User.id))
    ).filter(User.username != username).all()
    
    return [username for username, in conversations]

# Edit message
@app.put("/edit_message/{message_id}")
def edit_message(message_id: str, edit: MessageEdit, db: Session = Depends(get_db)):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    message.message = edit.message
    message.edited = True
    db.commit()
    
    return {"message": "Message edited successfully"}

# Delete message
@app.delete("/delete_message/{message_id}/{delete_type}")
def delete_message(message_id: str, delete_type: str, db: Session = Depends(get_db)):
    message = db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    if delete_type == "everyone":
        message.deleted_for_everyone = True
    elif delete_type == "me":
        # Determine if requester is sender or receiver
        # For simplicity, mark both as deleted
        message.deleted_for_sender = True
        message.deleted_for_receiver = True
    
    db.commit()
    return {"message": "Message deleted successfully"}

# File upload
@app.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_extension = os.path.splitext(file.filename)[1]
    file_path = os.path.join(CHAT_FILES_DIR, f"{file_id}{file_extension}")
    
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return {
        "file_url": f"/get_file/{file_id}{file_extension}",
        "file_name": file.filename
    }

@app.get("/get_file/{filename}")
def get_file(filename: str):
    file_path = os.path.join(CHAT_FILES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)

# Admin endpoints
@app.get("/admin/all_users")
def get_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [
        {
            "username": user.username,
            "password": user.plain_password,
            "admin": user.is_admin,
            "banned": user.is_banned
        }
        for user in users
    ]

@app.post("/admin/ban_user")
def ban_user(ban: BanUser, db: Session = Depends(get_db)):
    user = get_user_by_username(db, ban.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_banned = True
    db.commit()
    
    return {"message": f"User {ban.username} has been banned"}

@app.post("/admin/unban_user")
def unban_user(ban: BanUser, db: Session = Depends(get_db)):
    user = get_user_by_username(db, ban.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_banned = False
    db.commit()
    
    return {"message": f"User {ban.username} has been unbanned"}

@app.post("/admin/change_password")
def change_password(change: ChangePassword, db: Session = Depends(get_db)):
    user = get_user_by_username(db, change.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.password = hash_password(change.new_password)
    user.plain_password = change.new_password
    db.commit()
    
    return {"message": f"Password for {change.username} has been changed successfully"}

@app.post("/admin/promote_to_admin")
def promote_to_admin(request: MakeAdmin, db: Session = Depends(get_db)):
    # Simple secret key check for security
    if request.secret_key != "admin_secret_2026":
        raise HTTPException(status_code=403, detail="Invalid secret key")
    
    user = get_user_by_username(db, request.username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_admin = True
    db.commit()
    
    return {"message": f"User {request.username} is now an admin", "username": request.username, "is_admin": True}

@app.get("/admin/all_conversations")
def get_all_conversations(db: Session = Depends(get_db)):
    # Get all unique conversation pairs
    conversations = db.query(
        User.username.label("user1"),
        User.username.label("user2")
    ).select_from(Message).join(
        User, Message.from_user_id == User.id
    ).distinct().all()
    
    unique_pairs = set()
    for conv in conversations:
        pair = tuple(sorted([conv.user1, conv.user2]))
        unique_pairs.add(pair)
    
    return [{"user1": pair[0], "user2": pair[1]} for pair in unique_pairs]

@app.get("/admin/messages/{user1}/{user2}")
def get_admin_messages(user1: str, user2: str, db: Session = Depends(get_db)):
    u1 = get_user_by_username(db, user1)
    u2 = get_user_by_username(db, user2)
    
    if not u1 or not u2:
        return []
    
    messages = db.query(Message).filter(
        ((Message.from_user_id == u1.id) & (Message.to_user_id == u2.id)) |
        ((Message.from_user_id == u2.id) & (Message.to_user_id == u1.id))
    ).order_by(Message.timestamp).all()
    
    result = []
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.from_user_id).first()
        receiver = db.query(User).filter(User.id == msg.to_user_id).first()
        
        result.append({
            "id": msg.id,
            "from_user": sender.username,
            "to_user": receiver.username,
            "message": msg.message,
            "file_url": msg.file_url,
            "file_name": msg.file_name,
            "file_type": msg.file_type,
            "timestamp": msg.timestamp.isoformat(),
            "edited": msg.edited,
            "deleted_for_everyone": msg.deleted_for_everyone
        })
    
    return result

# Serve the chat.html frontend
@app.get("/", response_class=HTMLResponse)
@app.get("/chat", response_class=HTMLResponse)
async def serve_chat():
    try:
        with open("chat.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="chat.html not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
