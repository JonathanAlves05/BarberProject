from typing import Optional, List
from datetime import datetime, date, time

from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, SQLModel, create_engine, Session, select
from fastapi.middleware.cors import CORSMiddleware

# --- Modelos de Dados (SQLModel) ---

class BarbeiroBase(SQLModel):
    nome: str
    especialidade: Optional[str] = None

class Barbeiro(BarbeiroBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class BarbeiroCreate(BarbeiroBase):
    pass

class BarbeiroPublic(BarbeiroBase):
    id: int

class ServicoBase(SQLModel):
    nome: str
    duracao_minutos: int
    preco: float

class Servico(ServicoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class ServicoCreate(ServicoBase):
    pass

class ServicoPublic(ServicoBase):
    id: int

class AgendamentoBase(SQLModel):
    cliente_nome: str
    cliente_telefone: Optional[str] = None
    data_hora: datetime
    barbeiro_id: int = Field(foreign_key="barbeiro.id")
    servico_id: int = Field(foreign_key="servico.id")
    observacoes: Optional[str] = None
    status: str = "confirmado"

class Agendamento(AgendamentoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class AgendamentoCreate(AgendamentoBase):
    pass

class AgendamentoPublic(AgendamentoBase):
    id: int

class HorarioDisponivelBase(SQLModel):
    barbeiro_id: int = Field(foreign_key="barbeiro.id")
    data: date
    hora_inicio: time
    hora_fim: time

class HorarioDisponivel(HorarioDisponivelBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

class HorarioDisponivelCreate(HorarioDisponivelBase):
    pass

class HorarioDisponivelPublic(HorarioDisponivelBase):
    id: int

# --- Configuração do Banco de Dados ---

DATABASE_FILE = "barbearia.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- Aplicação FastAPI ---

app = FastAPI(
    title="API de Agendamento da Barbearia",
    description="API simples para gerenciar agendamentos, barbeiros e serviços.",
    version="1.0.0"
)

origins = [
    "http://localhost",
    "http://127.0.0.1",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# --- Rotas da API ---

# Barbeiros
@app.post("/barbeiros/", response_model=BarbeiroPublic)
def create_barbeiro(*, session: Session = Depends(get_session), barbeiro: BarbeiroCreate):
    db_barbeiro = Barbeiro.model_validate(barbeiro)
    session.add(db_barbeiro)
    session.commit()
    session.refresh(db_barbeiro)
    return db_barbeiro

@app.get("/barbeiros/", response_model=List[BarbeiroPublic])
def read_barbeiros(*, session: Session = Depends(get_session)):
    barbeiros = session.exec(select(Barbeiro)).all()
    return barbeiros

# Serviços
@app.post("/servicos/", response_model=ServicoPublic)
def create_servico(*, session: Session = Depends(get_session), servico: ServicoCreate):
    db_servico = Servico.model_validate(servico)
    session.add(db_servico)
    session.commit()
    session.refresh(db_servico)
    return db_servico

@app.get("/servicos/", response_model=List[ServicoPublic])
def read_servicos(*, session: Session = Depends(get_session)):
    servicos = session.exec(select(Servico)).all()
    return servicos

# Horários Disponíveis
@app.post("/horarios_disponiveis/", response_model=HorarioDisponivelPublic)
def create_horario_disponivel(*, session: Session = Depends(get_session), horario: HorarioDisponivelCreate):
    db_horario = HorarioDisponivel.model_validate(horario)
    session.add(db_horario)
    session.commit()
    session.refresh(db_horario)
    return db_horario

@app.get("/horarios_disponiveis/", response_model=List[HorarioDisponivelPublic])
def read_horarios_disponiveis(
    barbeiro_id: Optional[int] = None,
    data: Optional[date] = None,
    session: Session = Depends(get_session)
):
    query = select(HorarioDisponivel)
    if barbeiro_id:
        query = query.where(HorarioDisponivel.barbeiro_id == barbeiro_id)
    if data:
        query = query.where(HorarioDisponivel.data == data)
    horarios = session.exec(query).all()
    return horarios

# Agendamentos
@app.post("/agendamentos/", response_model=AgendamentoPublic)
def create_agendamento(*, session: Session = Depends(get_session), agendamento: AgendamentoCreate):
    barbeiro = session.get(Barbeiro, agendamento.barbeiro_id)
    servico = session.get(Servico, agendamento.servico_id)
    if not barbeiro:
        raise HTTPException(status_code=404, detail="Barbeiro não encontrado")
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    requested_date = agendamento.data_hora.date()
    requested_time = agendamento.data_hora.time()
    available_slot = session.exec(
        select(HorarioDisponivel).where(
            HorarioDisponivel.barbeiro_id == agendamento.barbeiro_id,
            HorarioDisponivel.data == requested_date,
            HorarioDisponivel.hora_inicio <= requested_time,
            HorarioDisponivel.hora_fim >= requested_time
        )
    ).first()
    if not available_slot:
        raise HTTPException(status_code=400, detail="Horário não disponível para este barbeiro.")
    db_agendamento = Agendamento.model_validate(agendamento)
    session.add(db_agendamento)
    session.commit()
    session.refresh(db_agendamento)
    return db_agendamento

@app.get("/agendamentos/", response_model=List[AgendamentoPublic])
def read_agendamentos(
    barbeiro_id: Optional[int] = None,
    data: Optional[date] = None,
    session: Session = Depends(get_session)
):
    query = select(Agendamento)
    if barbeiro_id:
        query = query.where(Agendamento.barbeiro_id == barbeiro_id)
    if data:
        query = query.where(Agendamento.data_hora.cast(date) == data)
    agendamentos = session.exec(query).all()
    return agendamentos

@app.get("/agendamentos/{agendamento_id}", response_model=AgendamentoPublic)
def read_agendamento(*, session: Session = Depends(get_session), agendamento_id: int):
    agendamento = session.get(Agendamento, agendamento_id)
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return agendamento

@app.put("/agendamentos/{agendamento_id}", response_model=AgendamentoPublic)
def update_agendamento(
    *,
    session: Session = Depends(get_session),
    agendamento_id: int,
    agendamento_update: AgendamentoCreate
):
    agendamento = session.get(Agendamento, agendamento_id)
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    update_data = agendamento_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(agendamento, key, value)
    session.add(agendamento)
    session.commit()
    session.refresh(agendamento)
    return agendamento

@app.delete("/agendamentos/{agendamento_id}")
def delete_agendamento(*, session: Session = Depends(get_session), agendamento_id: int):
    agendamento = session.get(Agendamento, agendamento_id)
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    session.delete(agendamento)
    session.commit()
    return {"message": "Agendamento deletado com sucesso!"}
@app.get("/barbeiros/{barbeiro_id}/agendamentos/", response_model=List[AgendamentoPublic])
def listar_agendamentos_barbeiro(barbeiro_id: int, session: Session = Depends(get_session)):
    agendamentos = session.exec(
        select(Agendamento).where(Agendamento.barbeiro_id == barbeiro_id)
    ).all()
    return agendamentos