"""
Modulo responsavel por configurar a conexao com o banco de dados
(engine) e fornecer sessoes SQLAlchemy para a aplicacao.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base


class Database:
    """
    Encapsula o engine SQLAlchemy e a fabrica de sessoes.

    Uso tipico:
        db = Database("ecommerce.db")
        db.create_all()          # cria as tabelas, se nao existirem
        session = db.get_session()
    """

    def __init__(self, database_name: str = "ecommerce.db", echo: bool = False):
        if not database_name:
            raise ValueError("database_name nao pode ser vazio")

        self.database_name = database_name
        self._engine = create_engine(
            f"sqlite:///{database_name}",
            echo=echo,
            future=True,
        )
        self._SessionFactory = sessionmaker(bind=self._engine, future=True)

    def create_all(self) -> None:
        """Cria todas as tabelas mapeadas em models.py, caso nao existam."""
        Base.metadata.create_all(self._engine)

    def drop_all(self) -> None:
        """Remove todas as tabelas mapeadas (util para resetar os testes)."""
        Base.metadata.drop_all(self._engine)

    def get_session(self) -> Session:
        """Retorna uma nova sessao SQLAlchemy vinculada ao engine."""
        return self._SessionFactory()

    @property
    def engine(self):
        return self._engine
