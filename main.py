from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from typing import List, Optional
from starlette.status import HTTP_401_UNAUTHORIZED
import secrets
from datetime import datetime
import hashlib
import uuid


app = FastAPI()
security = HTTPBasic()

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
USERS_FILE = "./users.json"
MESSAGES_FILE = "./messages.json"
ONLINE_USERS_FILE = "./online_users.json"
BANNED_USERS_FILE = "./banned_users.json"
USERNAME = os.getenv("API_USERNAME", "admin")
PASSWORD = os.getenv("API_PASSWORD", "password")
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(CHAT_FILES_DIR, exist_ok=True)

# Initialize data files
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(MESSAGES_FILE):
    with open(MESSAGES_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(ONLINE_USERS_FILE):
    with open(ONLINE_USERS_FILE, "w") as f:
        json.dump({}, f)

if not os.path.exists(BANNED_USERS_FILE):
    with open(BANNED_USERS_FILE, "w") as f:
        json.dump([], f)

# Pydantic models
class UserSignup(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Message(BaseModel):
    from_user: str
    to_user: str
    message: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None
    file_type: Optional[str] = None

class MessageEdit(BaseModel):
    message: str

class MessageDelete(BaseModel):
    username: str

class BanUser(BaseModel):
    username: str

class ChangePassword(BaseModel):
    username: str
    new_password: str

class UserSession(BaseModel):
    username: str
    token: str

# Helper functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def load_messages():
    with open(MESSAGES_FILE, "r") as f:
        messages = json.load(f)
    
    # Ensure all messages have required fields for backwards compatibility
    needs_save = False
    for msg in messages:
        if "id" not in msg:
            msg["id"] = str(uuid.uuid4())
            needs_save = True
        if "edited" not in msg:
            msg["edited"] = False
            needs_save = True
        if "deleted_for" not in msg:
            msg["deleted_for"] = []
            needs_save = True
    
    # Save updated messages if we added any fields
    if needs_save:
        save_messages(messages)
    
    return messages

def save_messages(messages):
    with open(MESSAGES_FILE, "w") as f:
        json.dump(messages, f, indent=2)

def load_online_users():
    with open(ONLINE_USERS_FILE, "r") as f:
        return json.load(f)

def save_online_users(online_users):
    with open(ONLINE_USERS_FILE, "w") as f:
        json.dump(online_users, f, indent=2)

def load_banned_users():
    with open(BANNED_USERS_FILE, "r") as f:
        return json.load(f)

def save_banned_users(banned_users):
    with open(BANNED_USERS_FILE, "w") as f:
        json.dump(banned_users, f, indent=2)

def update_user_status(username: str, status: str):
    online_users = load_online_users()
    if status == "offline":
        # Remove user completely when they go offline
        if username in online_users:
            del online_users[username]
    else:
        # Add/update user when they're online
        online_users[username] = {
            "status": status,
            "last_seen": datetime.now().isoformat()
        }
    save_online_users(online_users)

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, USERNAME)
    correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.get("/files", response_model=List[str])
def list_files():
    return os.listdir(STORAGE_DIR)

@app.post("/upload")
def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(STORAGE_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    return {"filename": file.filename}

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(STORAGE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)

@app.delete("/delete/{filename}")
def delete_file(filename: str, user: str = Depends(authenticate)):
    file_path = os.path.join(STORAGE_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return {"detail": "File deleted"}

# ===== CHAT APPLICATION ENDPOINTS =====

@app.post("/signup")
def signup(user: UserSignup):
    users = load_users()
    
    if user.username in users:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if len(user.username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    
    users[user.username] = {
        "password": hash_password(user.password),
        "plain_password": user.password,  # WARNING: Security risk! Storing plain password for admin view
        "created_at": datetime.now().isoformat(),
        "is_admin": False
    }
    save_users(users)
    
    # Generate a simple session token
    token = secrets.token_urlsafe(32)
    
    # Set user online
    update_user_status(user.username, "online")
    
    return {"message": "User created successfully", "username": user.username, "token": token}

@app.post("/login")
def login(user: UserLogin):
    # Check for admin login
    if user.username == ADMIN_USERNAME and user.password == ADMIN_PASSWORD:
        token = secrets.token_urlsafe(32)
        update_user_status(user.username, "online")
        # Return both keys for compatibility
        return {"message": "Admin login successful", "username": user.username, "token": token, "is_admin": True, "admin": True}
    
    users = load_users()
    banned_users = load_banned_users()
    
    # Check if user is banned
    if user.username in banned_users:
        raise HTTPException(status_code=403, detail="Your account has been banned")
    
    if user.username not in users:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    stored_password = users[user.username]["password"]
    if stored_password != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Generate a simple session token
    token = secrets.token_urlsafe(32)
    
    # Set user online
    update_user_status(user.username, "online")
    
    # Default: not admin
    is_admin_flag = False
    users = load_users()
    if user.username in users:
        is_admin_flag = users[user.username].get('is_admin', False)

    # Return both keys for compatibility with older frontends
    return {"message": "Login successful", "username": user.username, "token": token, "is_admin": is_admin_flag, "admin": is_admin_flag}


class PromoteAdmin(BaseModel):
    username: str
    secret_key: str


@app.post("/admin/promote_to_admin")
def promote_to_admin(req: PromoteAdmin):
    # Simple secret key check
    if req.secret_key != "admin_secret_2026":
        raise HTTPException(status_code=403, detail="Invalid secret key")

    users = load_users()
    if req.username not in users:
        raise HTTPException(status_code=404, detail="User not found")

    users[req.username]["is_admin"] = True
    save_users(users)
    return {"message": f"User {req.username} promoted to admin", "username": req.username, "is_admin": True}

@app.get("/search_users/{query}")
def search_users(query: str):
    users = load_users()
    
    # Find users that match the query
    matching_users = [username for username in users.keys() if query.lower() in username.lower()]
    
    return {"users": matching_users}

@app.post("/send_message")
def send_message(msg: Message):
    users = load_users()
    
    # Verify both users exist
    if msg.from_user not in users:
        raise HTTPException(status_code=404, detail="Sender not found")
    if msg.to_user not in users:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    messages = load_messages()
    
    new_message = {
        "id": str(uuid.uuid4()),
        "from": msg.from_user,
        "to": msg.to_user,
        "message": msg.message,
        "timestamp": datetime.now().isoformat(),
        "edited": False,
        "deleted_for": []
    }
    
    # Add file info if present
    if msg.file_url:
        new_message["file_url"] = msg.file_url
        new_message["file_name"] = msg.file_name
        new_message["file_type"] = msg.file_type
    
    messages.append(new_message)
    save_messages(messages)
    
    return {"message": "Message sent successfully", "message_id": new_message["id"]}

@app.get("/get_messages/{user1}/{user2}")
def get_messages(user1: str, user2: str):
    messages = load_messages()
    
    # Get all messages between user1 and user2
    conversation = [
        msg for msg in messages
        if (msg["from"] == user1 and msg["to"] == user2) or (msg["from"] == user2 and msg["to"] == user1)
    ]
    
    # Filter out messages deleted for this user or deleted for everyone
    filtered_conversation = []
    for msg in conversation:
        # Skip if message was deleted for everyone
        if msg.get("deleted_for_everyone", False):
            continue
        
        # Skip if message was deleted for this specific user
        if user1 in msg.get("deleted_for", []):
            continue
        
        filtered_conversation.append(msg)
    
    return {"messages": filtered_conversation}

@app.get("/get_conversations/{username}")
def get_conversations(username: str):
    messages = load_messages()
    
    # Find all unique users this user has chatted with
    contacts = set()
    for msg in messages:
        if msg["from"] == username:
            contacts.add(msg["to"])
        elif msg["to"] == username:
            contacts.add(msg["from"])
    
    return {"conversations": list(contacts)}

@app.post("/upload_chat_file")
async def upload_chat_file(file: UploadFile = File(...)):
    # Check file size (200MB = 200 * 1024 * 1024 bytes)
    MAX_FILE_SIZE = 200 * 1024 * 1024
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 200MB limit")
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(CHAT_FILES_DIR, filename)
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Determine file type
    file_type = "file"
    if file.content_type:
        if file.content_type.startswith("image/"):
            file_type = "image"
        elif file.content_type.startswith("video/"):
            file_type = "video"
    
    return {
        "file_url": f"/download_chat_file/{filename}",
        "file_name": file.filename,
        "file_type": file_type,
        "file_size": file_size
    }

@app.get("/download_chat_file/{filename}")
def download_chat_file(filename: str):
    file_path = os.path.join(CHAT_FILES_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename.split("_", 2)[-1] if "_" in filename else filename)

@app.get("/online_status/{username}")
def get_online_status(username: str):
    online_users = load_online_users()
    
    if username not in online_users:
        return {"username": username, "status": "offline", "last_seen": None}
    
    return {
        "username": username,
        "status": online_users[username]["status"],
        "last_seen": online_users[username]["last_seen"]
    }

@app.get("/all_online_status")
def get_all_online_status():
    online_users = load_online_users()
    
    # Clean up stale users (no heartbeat in 60+ seconds)
    current_time = datetime.now()
    users_to_remove = []
    
    for username, data in online_users.items():
        last_seen = datetime.fromisoformat(data["last_seen"])
        time_diff = (current_time - last_seen).total_seconds()
        
        # Remove users who haven't sent heartbeat in 60 seconds
        if time_diff > 60:
            users_to_remove.append(username)
    
    for username in users_to_remove:
        del online_users[username]
    
    # Save cleaned up list
    if users_to_remove:
        save_online_users(online_users)
    
    # Only return users with "online" status (shouldn't be any offline ones now)
    return {k: v for k, v in online_users.items() if v.get("status") == "online"}

@app.post("/logout/{username}")
def logout(username: str):
    update_user_status(username, "offline")
    return {"message": "Logged out successfully"}

@app.post("/heartbeat/{username}")
def heartbeat(username: str):
    # Check if user is banned
    banned_users = load_banned_users()
    if username in banned_users:
        raise HTTPException(status_code=403, detail="User has been banned")
    
    # Update user's last seen time
    update_user_status(username, "online")
    return {"status": "ok", "is_banned": False}

@app.get("/check_ban_status/{username}")
def check_ban_status(username: str):
    """Check if a user is currently banned"""
    banned_users = load_banned_users()
    is_banned = username in banned_users
    return {"username": username, "is_banned": is_banned}

@app.put("/edit_message/{message_id}")
def edit_message(message_id: str, msg_edit: MessageEdit):
    messages = load_messages()
    
    # Find the message
    message_found = False
    for msg in messages:
        if msg.get("id") == message_id:
            # Only allow editing if message has text content
            msg["message"] = msg_edit.message
            msg["edited"] = True
            msg["edited_at"] = datetime.now().isoformat()
            message_found = True
            break
    
    if not message_found:
        raise HTTPException(status_code=404, detail="Message not found")
    
    save_messages(messages)
    return {"message": "Message edited successfully"}

@app.delete("/delete_message/{message_id}/{delete_type}")
def delete_message(message_id: str, delete_type: str, delete_data: MessageDelete):
    messages = load_messages()
    
    # Find the message
    message_found = False
    for msg in messages:
        if msg.get("id") == message_id:
            message_found = True
            
            if delete_type == "everyone":
                # Verify the user deleting is the sender
                if msg.get("from") != delete_data.username:
                    raise HTTPException(status_code=403, detail="Only sender can delete for everyone")
                # Mark as deleted for everyone
                msg["deleted_for_everyone"] = True
            elif delete_type == "me":
                # Add user to deleted_for list
                if "deleted_for" not in msg:
                    msg["deleted_for"] = []
                if delete_data.username not in msg["deleted_for"]:
                    msg["deleted_for"].append(delete_data.username)
            else:
                raise HTTPException(status_code=400, detail="Invalid delete type")
            
            break
    
    if not message_found:
        raise HTTPException(status_code=404, detail="Message not found")
    
    save_messages(messages)
    return {"message": "Message deleted successfully"}

# ===== ADMIN ENDPOINTS =====

@app.get("/admin/all_users")
def get_all_users():
    """Get all registered users for admin"""
    users = load_users()
    banned_users = load_banned_users()
    
    user_list = []
    for username in users.keys():
        user_list.append({
            "username": username,
            "is_banned": username in banned_users,
            "created_at": users[username].get("created_at"),
            "password": users[username].get("plain_password", "[Old user - no password stored]"),  # Plain password
            "password_hash": users[username].get("password")[:16] + "..."  # Show first 16 chars of hash
        })
    
    return {"users": user_list}

@app.get("/admin/all_conversations")
def get_all_conversations():
    """Get all conversations for admin panel"""
    messages = load_messages()
    
    # Find all unique pairs of users who have chatted
    conversations = {}
    for msg in messages:
        user1 = msg["from"]
        user2 = msg["to"]
        pair = tuple(sorted([user1, user2]))
        
        if pair not in conversations:
            conversations[pair] = {
                "users": list(pair),
                "last_message": msg["timestamp"],
                "message_count": 1
            }
        else:
            conversations[pair]["message_count"] += 1
            if msg["timestamp"] > conversations[pair]["last_message"]:
                conversations[pair]["last_message"] = msg["timestamp"]
    
    return {"conversations": list(conversations.values())}

@app.get("/admin/messages/{user1}/{user2}")
def get_admin_messages(user1: str, user2: str):
    """Get all messages between two users (admin view - no filtering)"""
    messages = load_messages()
    
    # Get all messages between user1 and user2 (no deletion filtering for admin)
    conversation = [
        msg for msg in messages
        if (msg["from"] == user1 and msg["to"] == user2) or (msg["from"] == user2 and msg["to"] == user1)
    ]
    
    return {"messages": conversation}

@app.post("/admin/ban_user")
def ban_user(ban_data: BanUser):
    """Ban a user"""
    banned_users = load_banned_users()
    
    if ban_data.username not in banned_users:
        banned_users.append(ban_data.username)
        save_banned_users(banned_users)
        
        # Remove user from online status
        update_user_status(ban_data.username, "offline")
    
    return {"message": f"User {ban_data.username} has been banned"}

@app.post("/admin/unban_user")
def unban_user(ban_data: BanUser):
    """Unban a user"""
    banned_users = load_banned_users()
    
    if ban_data.username in banned_users:
        banned_users.remove(ban_data.username)
        save_banned_users(banned_users)
    
    return {"message": f"User {ban_data.username} has been unbanned"}

@app.get("/admin/banned_users")
def get_banned_users():
    """Get list of all banned users"""
    banned_users = load_banned_users()
    return {"banned_users": banned_users}

@app.post("/admin/change_password")
def admin_change_password(change_data: ChangePassword):
    """Admin can change any user's password"""
    users = load_users()
    
    if change_data.username not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update both hashed and plain password
    users[change_data.username]["password"] = hash_password(change_data.new_password)
    users[change_data.username]["plain_password"] = change_data.new_password
    
    save_users(users)
    return {"message": f"Password for {change_data.username} has been changed successfully"}

