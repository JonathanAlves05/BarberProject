from typing import Optional, List
from datetime import datetime, date, time, timedelta

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

# --- Funções de horários e datas disponíveis ---

def gerar_horarios_disponiveis(barbeiro_id: int, data: date, session: Session):
    horarios = []
    hora_inicio = 9
    hora_fim = 21
    for h in range(hora_inicio, hora_fim):
        horario_dt = datetime.combine(data, time(h, 0))
        existe = session.exec(
            select(Agendamento).where(
                Agendamento.barbeiro_id == barbeiro_id,
                Agendamento.data_hora == horario_dt
            )
        ).first()
        if not existe:
            horarios.append(horario_dt.time())
    return horarios

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
    db_barbeiro = Barbeiro.from_orm(barbeiro)
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
    db_servico = Servico.from_orm(servico)
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
    db_horario = HorarioDisponivel.from_orm(horario)
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
    db_agendamento = Agendamento.from_orm(agendamento)
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
        query = query.where(Agendamento.data_hora >= datetime.combine(data, time(0, 0)),
                            Agendamento.data_hora < datetime.combine(data + timedelta(days=1), time(0, 0)))
    agendamentos = session.exec(query).all()
    return agendamentos

@app.get("/agendamentos/{agendamento_id}", response_model=AgendamentoPublic)
def get_agendamento(agendamento_id: int, session: Session = Depends(get_session)):
    agendamento = session.get(Agendamento, agendamento_id)
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    return agendamento

@app.put("/agendamentos/{agendamento_id}", response_model=AgendamentoPublic)
def update_agendamento(agendamento_id: int, agendamento: AgendamentoCreate, session: Session = Depends(get_session)):
    db_agendamento = session.get(Agendamento, agendamento_id)
    if not db_agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    for key, value in agendamento.dict().items():
        setattr(db_agendamento, key, value)
    session.add(db_agendamento)
    session.commit()
    session.refresh(db_agendamento)
    return db_agendamento

@app.delete("/agendamentos/{agendamento_id}")
def delete_agendamento(agendamento_id: int, session: Session = Depends(get_session)):
    agendamento = session.get(Agendamento, agendamento_id)
    if not agendamento:
        raise HTTPException(status_code=404, detail="Agendamento não encontrado")
    session.delete(agendamento)
    session.commit()
    return {"ok": True}

@app.get("/barbeiros/{barbeiro_id}/agendamentos/", response_model=List[AgendamentoPublic])
def agendamentos_barbeiro(barbeiro_id: int, session: Session = Depends(get_session)):
    agendamentos = session.exec(
        select(Agendamento).where(Agendamento.barbeiro_id == barbeiro_id)
    ).all()
    return agendamentos

# --- ENDPOINTS DE DATAS E HORÁRIOS DISPONÍVEIS ---

@app.get("/barbeiros/{barbeiro_id}/datas_disponiveis/", response_model=List[date])
def datas_disponiveis_barbeiro(barbeiro_id: int, session: Session = Depends(get_session)):
    datas = []
    hoje = date.today()
    for i in range(30):  # próximos 30 dias
        dia = hoje + timedelta(days=i)
        horarios = gerar_horarios_disponiveis(barbeiro_id, dia, session)
        if horarios:
            datas.append(dia)
    return datas

@app.get("/barbeiros/{barbeiro_id}/horarios_disponiveis/", response_model=List[str])
def horarios_disponiveis_barbeiro(barbeiro_id: int, data: date, session: Session = Depends(get_session)):
    horarios = gerar_horarios_disponiveis(barbeiro_id, data, session)
    # Retorna como string para facilitar o frontend
    return [h.strftime("%H:%M") for h in horarios]