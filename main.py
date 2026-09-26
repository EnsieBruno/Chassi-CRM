import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from passlib.context import CryptContext
import jwt

# Configuracoes e Variaveis de Ambiente
SECRET_KEY = "sua_chave_secreta_jwt_para_o_mvp"
ALGORITHM = "HS256"
DATABASE_URL = "sqlite:///./chassi_crm.db"

# Inicializacao da Base de Dados
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------
# MODELOS DO BANCO DE DADOS (SQLAlchemy)
# ---------------------------------------------------------
class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    cargo = Column(String, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow)

    chamados = relationship("ChamadoDB", back_populates="autor")


class ChamadoDB(Base):
    __tablename__ = "chamados"

    id_chamado = Column(Integer, primary_key=True, index=True, autoincrement=True)
    titulo = Column(String, nullable=False)
    descricao = Column(String, nullable=False)
    alcance = Column(Float, nullable=False)
    impacto = Column(Float, nullable=False)
    confianca = Column(Float, nullable=False)
    esforco = Column(Float, nullable=False)
    score_rice = Column(Float, nullable=False)
    status = Column(String, default="Pendente", nullable=False)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"), nullable=False)
    autor = relationship("UsuarioDB", back_populates="chamados")

Base.metadata.create_all(bind=engine)

# ---------------------------------------------------------
# ESQUEMAS DE VALIDACAO (Pydantic)
# ---------------------------------------------------------
class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    cargo: str

class LoginSchema(BaseModel):
    email: EmailStr
    senha: str

class ChamadoCreate(BaseModel):
    titulo: str
    descricao: str
    alcance: float
    impacto: float
    confianca: float
    esforco: float

class ChamadoResponse(BaseModel):
    id_chamado: int
    titulo: str
    descricao: str
    alcance: float
    impacto: float
    confianca: float
    esforco: float
    score_rice: float
    status: str
    data_criacao: datetime

    class Config:
        from_attributes = True

# ---------------------------------------------------------
# APLICACAO FASTAPI E ENDPOINTS
# ---------------------------------------------------------
app = FastAPI(title="CHASSI - CRM API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/usuarios", status_code=status.HTTP_201_CREATED)
def cadastrar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_user = db.query(UsuarioDB).filter(UsuarioDB.email == usuario.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="E-mail ja cadastrado")
    
    senha_hash = pwd_context.hash(usuario.senha)
    novo_usuario = UsuarioDB(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=senha_hash,
        cargo=usuario.cargo
    )
    db.add(novo_usuario)
    db.commit()
    return {"message": "Usuario cadastrado com sucesso"}

@app.post("/login")
def login(dados: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(UsuarioDB).filter(UsuarioDB.email == dados.email).first()
    if not user or not pwd_context.verify(dados.senha, user.senha_hash):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    
    token = jwt.encode({"sub": str(user.id_usuario), "nome": user.nome}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/chamados", response_model=ChamadoResponse, status_code=status.HTTP_201_CREATED)
def criar_chamado(chamado: ChamadoCreate, db: Session = Depends(get_db)):
    if chamado.esforco <= 0:
        raise HTTPException(status_code=400, detail="O valor do esforco deve ser estritamente maior que zero")
    
    # Calculo da Matriz RICE: (Reach * Impact * Confidence) / Effort
    # Notar que Confianca entra na formula como decimal (ex: 80% = 0.8)
    confianca_decimal = chamado.confianca / 100.0 if chamado.confianca > 1 else chamado.confianca
    score_rice = (chamado.alcance * chamado.impacto * confianca_decimal) / chamado.esforco

    novo_chamado = ChamadoDB(
        titulo=chamado.titulo,
        descricao=chamado.descricao,
        alcance=chamado.alcance,
        impacto=chamado.impacto,
        confianca=chamado.confianca,
        esforco=chamado.esforco,
        score_rice=round(score_rice, 2),
        id_usuario=1 # Atribuido ao ID 1 do MVP para demonstracao
    )
    db.add(novo_chamado)
    db.commit()
    db.refresh(novo_chamado)
    return novo_chamado

@app.get("/chamados", response_model=List[ChamadoResponse])
def listar_backlog_priorizado(db: Session = Depends(get_db)):
    # Ordenacao decrescente pelo Score RICE
    chamados = db.query(ChamadoDB).order_by(ChamadoDB.score_rice.desc()).all()
    return chamados

@app.patch("/chamados/{id_chamado}/status")
def atualizar_status(id_chamado: int, novo_status: str, db: Session = Depends(get_db)):
    chamado = db.query(ChamadoDB).filter(ChamadoDB.id_chamado == id_chamado).first()
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado nao encontrado")
    
    chamado.status = novo_status
    db.commit()
    return {"message": "Status atualizado com sucesso", "status": novo_status}
