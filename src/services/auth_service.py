#!/usr/bin/env python3
"""
Serviço de Autenticação - Implementação REAL com hash de senha
"""

import sqlite3
import uuid
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

logger = logging.getLogger(__name__)


class AuthService:
    """Serviço para autenticação de usuários"""
    
    def __init__(self, db_path: str, secret_key: str):
        self.db_path = db_path
        self.secret_key = secret_key
    
    def _get_connection(self) -> sqlite3.Connection:
        """Retorna conexão com banco"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_user(
        self,
        nome: str,
        email: str,
        senha: str,
        tipo: str = "usuario"
    ) -> str:
        """
        Cria novo usuário com senha hasheada
        
        Args:
            nome: Nome do usuário
            email: Email único
            senha: Senha em texto plano (será hasheada)
            tipo: Tipo de usuário
        
        Returns:
            ID do usuário criado
        
        Raises:
            ValueError: Se email já existe
        """
        try:
            user_id = str(uuid.uuid4())
            senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO usuarios (id, nome, email, senha_hash, tipo, criado_em, ativo)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            """, (
                user_id,
                nome,
                email.lower().strip(),
                senha_hash,
                tipo,
                datetime.now(timezone.utc).isoformat()
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"User created successfully: {email}")
            return user_id
            
        except sqlite3.IntegrityError:
            logger.warning(f"Attempt to create duplicate user: {email}")
            raise ValueError("Email já cadastrado")
        except sqlite3.Error as e:
            logger.error(f"Error creating user: {e}", exc_info=True)
            raise
    
    def authenticate(
        self,
        email: str,
        senha: str
    ) -> Optional[Dict[str, Any]]:
        """
        Autentica usuário e retorna token JWT
        
        Args:
            email: Email do usuário
            senha: Senha em texto plano
        
        Returns:
            Dict com token e dados do usuário, ou None se falhar
        """
        try:
            email = email.lower().strip()
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nome, email, senha_hash, tipo, ativo
                FROM usuarios
                WHERE email = ?
            """, (email,))
            
            user = cursor.fetchone()
            
            if not user:
                logger.warning(f"Login attempt for non-existent user: {email}")
                conn.close()
                return None
            
            if not user["ativo"]:
                logger.warning(f"Login attempt for inactive user: {email}")
                conn.close()
                return None
            
            # Verifica senha
            if not check_password_hash(user["senha_hash"], senha):
                logger.warning(f"Invalid password for user: {email}")
                conn.close()
                return None
            
            # Atualiza último acesso
            cursor.execute("""
                UPDATE usuarios
                SET ultimo_acesso = ?
                WHERE id = ?
            """, (datetime.now(timezone.utc).isoformat(), user["id"]))
            
            conn.commit()
            conn.close()
            
            # Gera token JWT
            exp_time = datetime.now(timezone.utc) + timedelta(hours=24)
            token = jwt.encode(
                {
                    "user_id": user["id"],
                    "email": user["email"],
                    "tipo": user["tipo"],
                    "exp": exp_time.timestamp(),
                    "iat": datetime.now(timezone.utc).timestamp()
                },
                self.secret_key,
                algorithm="HS256"
            )
            
            logger.info(f"Login successful for user: {email}")
            
            return {
                "token": token,
                "user": {
                    "id": user["id"],
                    "nome": user["nome"],
                    "email": user["email"],
                    "tipo": user["tipo"]
                },
                "expires_in": 86400
            }
            
        except sqlite3.Error as e:
            logger.error(f"Database error during authentication: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {e}", exc_info=True)
            return None
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica validade do token JWT
        
        Args:
            token: Token JWT
        
        Returns:
            Payload do token se válido, None caso contrário
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Expired token")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
