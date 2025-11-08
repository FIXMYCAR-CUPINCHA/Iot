#!/usr/bin/env python3
"""
Sistema de logging estruturado para VisionMoto
Fornece observabilidade e rastreabilidade
"""

import logging
import sys
from typing import Optional
from pathlib import Path
import json
from datetime import datetime


class StructuredLogger:
    """Logger estruturado com contexto"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # Remove handlers existentes
        self.logger.handlers.clear()
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        # Formato estruturado
        formatter = StructuredFormatter()
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
        
        # Handler para arquivo (opcional)
        self._setup_file_handler()
    
    def _setup_file_handler(self):
        """Configura handler de arquivo se necessário"""
        log_dir = Path("logs")
        if not log_dir.exists():
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                return  # Sem permissão, continua sem arquivo
        
        log_file = log_dir / f"visionmoto_{datetime.now().strftime('%Y%m%d')}.log"
        
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.INFO)
            file_handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(file_handler)
        except Exception:
            pass  # Continua sem arquivo se falhar
    
    def debug(self, message: str, **context):
        """Log debug com contexto"""
        self.logger.debug(message, extra={"context": context})
    
    def info(self, message: str, **context):
        """Log info com contexto"""
        self.logger.info(message, extra={"context": context})
    
    def warning(self, message: str, **context):
        """Log warning com contexto"""
        self.logger.warning(message, extra={"context": context})
    
    def error(self, message: str, error: Optional[Exception] = None, **context):
        """Log error com contexto e exceção"""
        if error:
            context["error_type"] = type(error).__name__
            context["error_message"] = str(error)
        self.logger.error(message, extra={"context": context}, exc_info=error)
    
    def critical(self, message: str, error: Optional[Exception] = None, **context):
        """Log critical com contexto e exceção"""
        if error:
            context["error_type"] = type(error).__name__
            context["error_message"] = str(error)
        self.logger.critical(message, extra={"context": context}, exc_info=error)


class StructuredFormatter(logging.Formatter):
    """Formatter que produz logs estruturados em JSON"""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata log record como JSON estruturado"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Adiciona contexto se existir
        if hasattr(record, "context"):
            log_data["context"] = record.context
        
        # Adiciona informação de exceção se existir
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Em desenvolvimento, formato legível
        # Em produção, JSON puro para agregação
        try:
            from src.config import get_config
            config = get_config()
            if config.DEBUG:
                return self._format_pretty(log_data)
        except Exception:
            pass
        
        return json.dumps(log_data)
    
    def _format_pretty(self, log_data: dict) -> str:
        """Formato legível para desenvolvimento"""
        timestamp = log_data["timestamp"]
        level = log_data["level"]
        logger = log_data["logger"]
        message = log_data["message"]
        
        # Cores ANSI
        colors = {
            "DEBUG": "\033[36m",    # Cyan
            "INFO": "\033[32m",     # Green
            "WARNING": "\033[33m",  # Yellow
            "ERROR": "\033[31m",    # Red
            "CRITICAL": "\033[35m", # Magenta
        }
        reset = "\033[0m"
        
        color = colors.get(level, "")
        
        output = f"{color}{timestamp} [{level}]{reset} {logger} - {message}"
        
        # Adiciona contexto se existir
        if "context" in log_data and log_data["context"]:
            context_str = json.dumps(log_data["context"], indent=2)
            output += f"\n  Context: {context_str}"
        
        # Adiciona exceção se existir
        if "exception" in log_data:
            output += f"\n  Exception:\n{log_data['exception']}"
        
        return output


# Singleton para loggers
_loggers = {}


def get_logger(name: str, level: Optional[str] = None) -> StructuredLogger:
    """
    Retorna logger estruturado (singleton por nome)
    
    Args:
        name: Nome do logger (geralmente __name__)
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        StructuredLogger configurado
    """
    if name not in _loggers:
        if level is None:
            try:
                from src.config import get_config
                level = get_config().LOG_LEVEL
            except Exception:
                level = "INFO"
        
        _loggers[name] = StructuredLogger(name, level)
    
    return _loggers[name]


# Logger padrão do sistema
system_logger = get_logger("visionmoto")
