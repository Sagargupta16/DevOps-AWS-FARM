import bcrypt


class Hash:
    @staticmethod
    def bcrypt(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
