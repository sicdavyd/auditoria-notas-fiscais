"""
Classes entidade (ORM) mapeadas com SQLAlchemy Declarative, para o
dominio de e-commerce / estoque.

Relacionamentos implementados:
    - Categoria (1) ------ (N) Produto            -> 1:N
    - Produto (1) --------- (1) DetalheProduto     -> 1:1
    - Produto (N) --------- (M) Pedido             -> N:M (via ItemPedido,
                                                       modelada como "association
                                                       object" pois carrega
                                                       atributos proprios:
                                                       quantidade, preco_aplicado)

Nenhuma linha de SQL e escrita aqui: toda a estrutura das tabelas e
seus relacionamentos sao definidos por meio das classes e dos
construtores do SQLAlchemy (Column, ForeignKey, relationship, etc).
"""

from datetime import date

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nome_categoria = Column(String(100), nullable=False)
    departamento = Column(String(100), nullable=False)

    # 1:N -> uma categoria possui varios produtos
    produtos = relationship(
        "Produto",
        back_populates="categoria",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Categoria {self.nome_categoria} ({self.departamento})>"


class Produto(Base):
    __tablename__ = "produto"

    id_produto = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(200), nullable=False)
    preco_unitario = Column(Numeric(10, 2), nullable=False)
    quantidade_estoque = Column(Integer, nullable=False, default=0)
    id_categoria = Column(Integer, ForeignKey("categoria.id_categoria"), nullable=False)

    # N:1 -> muitos produtos para uma categoria (lado inverso do 1:N acima)
    categoria = relationship("Categoria", back_populates="produtos")

    # 1:1 -> um produto possui exatamente um registro de detalhe tecnico
    detalhe = relationship(
        "DetalheProduto",
        back_populates="produto",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # N:M (via ItemPedido, association object) -> um produto aparece em
    # varios itens de pedido, cada um ligado a um pedido
    itens_pedido = relationship(
        "ItemPedido",
        back_populates="produto",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Produto {self.nome} (id={self.id_produto})>"


class DetalheProduto(Base):
    __tablename__ = "detalhe_produto"

    id_detalhe = Column(Integer, primary_key=True, autoincrement=True)
    # unique=True garante a cardinalidade 1:1 no nivel do banco de dados
    id_produto = Column(
        Integer, ForeignKey("produto.id_produto"), nullable=False, unique=True
    )
    peso_kg = Column(Numeric(6, 3))
    dimensoes_cm = Column(String(50))
    garantia_meses = Column(Integer)

    produto = relationship("Produto", back_populates="detalhe")

    def __repr__(self) -> str:
        return f"<DetalheProduto produto_id={self.id_produto}>"


class Pedido(Base):
    __tablename__ = "pedido"

    id_pedido = Column(Integer, primary_key=True, autoincrement=True)
    data_pedido = Column(Date, default=date.today, nullable=False)
    status_pedido = Column(String(50), nullable=False, default="Processando")

    itens = relationship(
        "ItemPedido",
        back_populates="pedido",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Pedido id={self.id_pedido} status={self.status_pedido}>"


class ItemPedido(Base):
    """
    Tabela/classe associativa que resolve o relacionamento N:M entre
    Produto e Pedido. Modelada como "association object" (e nao apenas
    uma Table simples) porque carrega atributos proprios: quantidade e
    preco_aplicado.
    """

    __tablename__ = "item_pedido"
    __table_args__ = (
        UniqueConstraint(
            "id_produto", "id_pedido", name="uq_item_pedido_produto_pedido"
        ),
    )

    id_item_pedido = Column(Integer, primary_key=True, autoincrement=True)
    id_produto = Column(Integer, ForeignKey("produto.id_produto"), nullable=False)
    id_pedido = Column(Integer, ForeignKey("pedido.id_pedido"), nullable=False)
    quantidade = Column(Integer, nullable=False, default=1)
    preco_aplicado = Column(Numeric(10, 2), nullable=False)

    produto = relationship("Produto", back_populates="itens_pedido")
    pedido = relationship("Pedido", back_populates="itens")

    def __repr__(self) -> str:
        return (
            f"<ItemPedido produto_id={self.id_produto} "
            f"pedido_id={self.id_pedido} qtd={self.quantidade}>"
        )
