from passlib.context import CryptContext


pass_context = CryptContext(schemes = ['bcrypt'],deprecated='auto')

def get_hashed_password(password):
    return pass_context.hash(password)
