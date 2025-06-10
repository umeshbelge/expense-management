from ..extensions import db # Changed from ..app import db

class Category(db.Model):
    __tablename__ = 'category' # Explicitly setting table name

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True) # Initially global, unique names
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Null for global, set for user-specific

    # Relationship to Transaction model
    transactions = db.relationship('Transaction', backref='category_ref', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'
