from app.repositories.base_repo import BaseRepository
from app.models.product import Product


class ProductRepository(BaseRepository):
    def __init__(self):
        super().__init__(Product)

    def get_active(self, user_id=None):
        q = Product.query.filter_by(is_active=True)
        if user_id:
            q = q.filter_by(created_by=user_id)
        return q.all()

    def get_low_stock(self, user_id=None):
        q = (
            Product.query
            .filter(Product.is_active == True)
            .filter(Product.quantity <= Product.min_stock)
        )
        if user_id:
            q = q.filter(Product.created_by == user_id)
        return q.all()

    def get_by_category(self, category_id: int, user_id=None):
        q = Product.query.filter_by(category_id=category_id, is_active=True)
        if user_id:
            q = q.filter_by(created_by=user_id)
        return q.all()

    def search(self, term: str, user_id=None):
        like = f"%{term}%"
        q = (
            Product.query
            .filter(Product.is_active == True)
            .filter(Product.name.ilike(like) | Product.sku.ilike(like))
        )
        if user_id:
            q = q.filter(Product.created_by == user_id)
        return q.all()

    def update_quantity(self, product: Product, delta: int):
        product.quantity += delta
        self.commit()
        return product
