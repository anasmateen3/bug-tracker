from fastapi import FastAPI, APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
import base64

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 168  # 7 days

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

security = HTTPBearer()

# ============= MODELS =============

class UserRole(BaseModel):
    ADMIN: str = "admin"
    MANAGER: str = "manager"
    DEVELOPER: str = "developer"
    VIEWER: str = "viewer"

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    name: str
    role: str = "developer"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    role: str = "developer"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    token: str
    user: User

class Project(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    key: str  # Like "PROJ"
    members: List[str] = []  # User IDs
    created_by: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    key: str

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class AddMemberRequest(BaseModel):
    user_id: str

class Ticket(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str = ""
    priority: str = "medium"  # low, medium, high, critical
    status: str = "todo"  # todo, inprogress, done
    project_id: str
    assignee_id: Optional[str] = None
    reporter_id: str
    attachments: List[dict] = []  # [{"filename": str, "data": str}]
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class TicketCreate(BaseModel):
    title: str
    description: str = ""
    priority: str = "medium"
    status: str = "todo"
    project_id: str
    assignee_id: Optional[str] = None

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    assignee_id: Optional[str] = None

class Comment(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    ticket_id: str
    user_id: str
    user_name: str
    text: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CommentCreate(BaseModel):
    ticket_id: str
    text: str

# ============= AUTH UTILITIES =============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    token = credentials.credentials
    payload = decode_token(token)
    user_id = payload.get("user_id")
    
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(**user_doc)

# ============= AUTH ROUTES =============

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    # Check if user exists
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = User(
        email=user_data.email,
        name=user_data.name,
        role=user_data.role
    )
    
    user_doc = user.model_dump()
    user_doc["password"] = hash_password(user_data.password)
    
    await db.users.insert_one(user_doc)
    
    token = create_token(user.id)
    return TokenResponse(token=token, user=user)

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user_doc = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user_doc:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(credentials.password, user_doc["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = User(**user_doc)
    token = create_token(user.id)
    return TokenResponse(token=token, user=user)

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# ============= PROJECT ROUTES =============

@api_router.post("/projects", response_model=Project)
async def create_project(project_data: ProjectCreate, current_user: User = Depends(get_current_user)):
    # Check if key already exists
    existing = await db.projects.find_one({"key": project_data.key.upper()}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Project key already exists")
    
    project = Project(
        name=project_data.name,
        description=project_data.description,
        key=project_data.key.upper(),
        created_by=current_user.id,
        members=[current_user.id]
    )
    
    await db.projects.insert_one(project.model_dump())
    return project

@api_router.get("/projects", response_model=List[Project])
async def get_projects(current_user: User = Depends(get_current_user)):
    projects = await db.projects.find(
        {"members": current_user.id},
        {"_id": 0}
    ).to_list(1000)
    return projects

@api_router.get("/projects/{project_id}", response_model=Project)
async def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user.id not in project["members"]:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    
    return Project(**project)

@api_router.put("/projects/{project_id}", response_model=Project)
async def update_project(project_id: str, update_data: ProjectUpdate, current_user: User = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user.id not in project["members"]:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    
    update_fields = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if update_fields:
        await db.projects.update_one({"id": project_id}, {"$set": update_fields})
        project.update(update_fields)
    
    return Project(**project)

@api_router.delete("/projects/{project_id}")
async def delete_project(project_id: str, current_user: User = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project["created_by"] != current_user.id:
        raise HTTPException(status_code=403, detail="Only project creator can delete")
    
    await db.projects.delete_one({"id": project_id})
    await db.tickets.delete_many({"project_id": project_id})
    return {"message": "Project deleted"}

@api_router.post("/projects/{project_id}/members")
async def add_member(project_id: str, member_data: AddMemberRequest, current_user: User = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if current_user.id not in project["members"]:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    
    # Check if user exists
    user = await db.users.find_one({"id": member_data.user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if member_data.user_id not in project["members"]:
        await db.projects.update_one(
            {"id": project_id},
            {"$push": {"members": member_data.user_id}}
        )
    
    return {"message": "Member added"}

@api_router.delete("/projects/{project_id}/members/{user_id}")
async def remove_member(project_id: str, user_id: str, current_user: User = Depends(get_current_user)):
    project = await db.projects.find_one({"id": project_id}, {"_id": 0})
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project["created_by"] != current_user.id:
        raise HTTPException(status_code=403, detail="Only project creator can remove members")
    
    await db.projects.update_one(
        {"id": project_id},
        {"$pull": {"members": user_id}}
    )
    
    return {"message": "Member removed"}

# ============= TICKET ROUTES =============

@api_router.post("/tickets", response_model=Ticket)
async def create_ticket(ticket_data: TicketCreate, current_user: User = Depends(get_current_user)):
    # Verify project membership
    project = await db.projects.find_one({"id": ticket_data.project_id}, {"_id": 0})
    if not project or current_user.id not in project["members"]:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    
    ticket = Ticket(
        title=ticket_data.title,
        description=ticket_data.description,
        priority=ticket_data.priority,
        status=ticket_data.status,
        project_id=ticket_data.project_id,
        assignee_id=ticket_data.assignee_id,
        reporter_id=current_user.id
    )
    
    await db.tickets.insert_one(ticket.model_dump())
    return ticket

@api_router.get("/tickets", response_model=List[Ticket])
async def get_tickets(
    project_id: Optional[str] = None,
    status: Optional[str] = None,
    assignee_id: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    query = {}
    
    if project_id:
        # Verify access
        project = await db.projects.find_one({"id": project_id}, {"_id": 0})
        if not project or current_user.id not in project["members"]:
            raise HTTPException(status_code=403, detail="Not a member of this project")
        query["project_id"] = project_id
    else:
        # Get all projects user is member of
        projects = await db.projects.find({"members": current_user.id}, {"_id": 0}).to_list(1000)
        project_ids = [p["id"] for p in projects]
        query["project_id"] = {"$in": project_ids}
    
    if status:
        query["status"] = status
    
    if assignee_id:
        query["assignee_id"] = assignee_id
    
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    tickets = await db.tickets.find(query, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return tickets

@api_router.get("/tickets/{ticket_id}", response_model=Ticket)
async def get_ticket(ticket_id: str, current_user: User = Depends(get_current_user)):
    ticket = await db.tickets.find_one({"id": ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Verify access
    project = await db.projects.find_one({"id": ticket["project_id"]}, {"_id": 0})
    if not project or current_user.id not in project["members"]:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    
    return Ticket(**ticket)

@api_router.put("/tickets/{ticket_id}", response_model=Ticket)
async def update_ticket(ticket_id: str, update_data: TicketUpdate, current_user: User = Depends(get_current_user)):
    ticket = await db.tickets.find_one({"id": ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Verify access
    project = await db.projects.find_one({"id": ticket["project_id"]}, {"_id": 0})
    if not project or current_user.id not in project["members"]:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    
    update_fields = {k: v for k, v in update_data.model_dump().items() if v is not None}
    if update_fields:
        update_fields["updated_at"] = datetime.now(timezone.utc).isoformat()
        await db.tickets.update_one({"id": ticket_id}, {"$set": update_fields})
        ticket.update(update_fields)
    
    return Ticket(**ticket)

@api_router.delete("/tickets/{ticket_id}")
async def delete_ticket(ticket_id: str, current_user: User = Depends(get_current_user)):
    ticket = await db.tickets.find_one({"id": ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Verify access
    project = await db.projects.find_one({"id": ticket["project_id"]}, {"_id": 0})
    if not project or current_user.id not in project["members"]:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    
    await db.tickets.delete_one({"id": ticket_id})
    await db.comments.delete_many({"ticket_id": ticket_id})
    return {"message": "Ticket deleted"}

@api_router.post("/tickets/{ticket_id}/attachments")
async def add_attachment(
    ticket_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    ticket = await db.tickets.find_one({"id": ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    # Verify access
    project = await db.projects.find_one({"id": ticket["project_id"]}, {"_id": 0})
    if not project or current_user.id not in project["members"]:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    
    # Read file and convert to base64
    contents = await file.read()
    base64_data = base64.b64encode(contents).decode('utf-8')
    
    attachment = {
        "id": str(uuid.uuid4()),
        "filename": file.filename,
        "data": base64_data,
        "content_type": file.content_type,
        "uploaded_by": current_user.id,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.tickets.update_one(
        {"id": ticket_id},
        {"$push": {"attachments": attachment}}
    )
    
    return {"message": "Attachment added", "attachment": attachment}

# ============= COMMENT ROUTES =============

@api_router.post("/comments", response_model=Comment)
async def create_comment(comment_data: CommentCreate, current_user: User = Depends(get_current_user)):
    # Verify access to ticket
    ticket = await db.tickets.find_one({"id": comment_data.ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    project = await db.projects.find_one({"id": ticket["project_id"]}, {"_id": 0})
    if not project or current_user.id not in project["members"]:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    
    comment = Comment(
        ticket_id=comment_data.ticket_id,
        user_id=current_user.id,
        user_name=current_user.name,
        text=comment_data.text
    )
    
    await db.comments.insert_one(comment.model_dump())
    return comment

@api_router.get("/comments", response_model=List[Comment])
async def get_comments(ticket_id: str, current_user: User = Depends(get_current_user)):
    # Verify access
    ticket = await db.tickets.find_one({"id": ticket_id}, {"_id": 0})
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    project = await db.projects.find_one({"id": ticket["project_id"]}, {"_id": 0})
    if not project or current_user.id not in project["members"]:
        raise HTTPException(status_code=403, detail="Not a member of this project")
    
    comments = await db.comments.find(
        {"ticket_id": ticket_id},
        {"_id": 0}
    ).sort("created_at", 1).to_list(1000)
    
    return comments

@api_router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str, current_user: User = Depends(get_current_user)):
    comment = await db.comments.find_one({"id": comment_id}, {"_id": 0})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if comment["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="Can only delete your own comments")
    
    await db.comments.delete_one({"id": comment_id})
    return {"message": "Comment deleted"}

# ============= USER ROUTES =============

@api_router.get("/users", response_model=List[User])
async def get_users(current_user: User = Depends(get_current_user)):
    users = await db.users.find({}, {"_id": 0, "password": 0}).to_list(1000)
    return users

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
