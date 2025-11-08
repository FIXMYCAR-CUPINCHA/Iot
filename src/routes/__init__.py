"""API Routes package"""
from .mobile_routes import mobile_bp
from .java_routes import java_bp
from .dotnet_routes import dotnet_bp
from .iot_routes import iot_bp
from .database_routes import database_bp

__all__ = ["mobile_bp", "java_bp", "dotnet_bp", "iot_bp", "database_bp"]
