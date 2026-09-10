"""
Camada de Repositorio (padrao Repository) para o dominio de
e-commerce / estoque, implementada com SQLAlchemy ORM.

Nenhuma linha de SQL bruto e utilizada: todas as operacoes (create,
read, update, delete) sao feitas por meio da Session e das classes
mapeadas em models.py.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from .database import Database
from .models import Categoria, Produto, DetalheProduto, Pedido, ItemPedido


class BaseRepository:
    """Repositorio generico com operacoes CRUD comuns a todas as entidades."""

    model = None  # definido nas subclasses

    def __init__(self, database: Database):
        self.database = database

    def create(self, obj):
        session: Session = self.database.get_session()
        try:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj
        finally:
            session.close()

    def load_from_id(self, id_value: int):
        session: Session = self.database.get_session()
        try:
            return session.get(self.model, id_value)
        finally:
            session.close()

    def load_all(self) -> List:
        session: Session = self.database.get_session()
        try:
            return session.query(self.model).all()
        finally:
            session.close()

    def update(self, obj):
        session: Session = self.database.get_session()
        try:
            merged = session.merge(obj)
            session.commit()
            return merged
        finally:
            session.close()

    def delete(self, obj) -> None:
        session: Session = self.database.get_session()
        try:
            merged = session.merge(obj)
            session.delete(merged)
            session.commit()
        finally:
            session.close()


class CategoriaRepository(BaseRepository):
    model = Categoria


class ProdutoRepository(BaseRepository):
    model = Produto

    def load_by_categoria(self, id_categoria: int) -> List[Produto]:
        session: Session = self.database.get_session()
        try:
            return (
                session.query(Produto)
                .filter(Produto.id_categoria == id_categoria)
                .all()
            )
        finally:
            session.close()

    def baixar_estoque(self, id_produto: int, quantidade: int) -> Produto:
        """Decrementa a quantidade em estoque de um produto (ex.: apos uma venda)."""
        session: Session = self.database.get_session()
        try:
            produto = session.get(Produto, id_produto)
            if produto is None:
                raise ValueError(f"Produto {id_produto} nao encontrado")
            produto.quantidade_estoque -= quantidade
            session.commit()
            session.refresh(produto)
            return produto
        finally:
            session.close()


class DetalheProdutoRepository(BaseRepository):
    model = DetalheProduto

    def load_by_produto(self, id_produto: int) -> Optional[DetalheProduto]:
        session: Session = self.database.get_session()
        try:
            return (
                session.query(DetalheProduto)
                .filter(DetalheProduto.id_produto == id_produto)
                .first()
            )
        finally:
            session.close()


class PedidoRepository(BaseRepository):
    model = Pedido


class ItemPedidoRepository(BaseRepository):
    model = ItemPedido

    def adicionar_item(
        self,
        id_produto: int,
        id_pedido: int,
        quantidade: int,
        preco_aplicado,
    ) -> ItemPedido:
        """Cria um vinculo N:M entre um Produto e um Pedido."""
        item = ItemPedido(
            id_produto=id_produto,
            id_pedido=id_pedido,
            quantidade=quantidade,
            preco_aplicado=preco_aplicado,
        )
        return self.create(item)

    def load_by_produto(self, id_produto: int) -> List[ItemPedido]:
        session: Session = self.database.get_session()
        try:
            return (
                session.query(ItemPedido)
                .filter(ItemPedido.id_produto == id_produto)
                .all()
            )
        finally:
            session.close()

    def load_by_pedido(self, id_pedido: int) -> List[ItemPedido]:
        session: Session = self.database.get_session()
        try:
            return (
                session.query(ItemPedido)
                .filter(ItemPedido.id_pedido == id_pedido)
                .all()
            )
        finally:
            session.close()
