from app.repositories.base_repo import BaseRepository
from app.models.user import User


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, email: str):
        return User.query.filter_by(email=email).first()

    def get_by_google_id(self, google_id: str):
        return User.query.filter_by(google_id=google_id).first()

    def find_or_create_google_user(self, google_id: str, email: str, name: str, avatar_url: str = None):
        """
        Busca un usuario por google_id; si no existe lo crea.
        Usado en el callback de Google OAuth.
        """
        user = self.get_by_google_id(google_id)
        if not user:
            # Podria existir un usuario con ese email registrado manualmente
            user = self.get_by_email(email)
            if user:
                user.google_id  = google_id
                user.avatar_url = avatar_url
            else:
                user = User(
                    name=name,
                    email=email,
                    google_id=google_id,
                    avatar_url=avatar_url,
                )
            self.save(user)
        return user
