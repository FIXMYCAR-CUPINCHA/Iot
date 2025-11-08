#!/usr/bin/env python3
"""
Formatador de respostas para .NET/C#
"""

from typing import Dict, Any, List
from datetime import datetime


class DotNetFormatter:
    """Formata respostas para o padrão .NET (PascalCase)"""
    
    @staticmethod
    def format_moto(moto: Dict[str, Any]) -> Dict[str, Any]:
        """Formata dados de moto para .NET"""
        formatted = {
            "Id": moto.get("id"),
            "Model": moto.get("modelo"),
            "LicensePlate": moto.get("placa"),
            "Status": moto.get("status"),
            "BatteryLevel": moto.get("bateria"),
            "LocationX": moto.get("localizacao_x"),
            "LocationY": moto.get("localizacao_y"),
            "Zone": moto.get("zona"),
            "Address": moto.get("endereco"),
            "Sector": moto.get("setor"),
            "Floor": moto.get("andar"),
            "ParkingSpot": moto.get("vaga"),
            "LocationDescription": moto.get("descricao_localizacao"),
            "LastUpdate": moto.get("ultima_atualizacao"),
            "InUseBy": moto.get("em_uso_por"),
        }
        
        # Adiciona localização completa se disponível
        if "localizacao_completa" in moto:
            loc = moto["localizacao_completa"]
            formatted["LocationDetails"] = {
                "Address": loc.get("endereco"),
                "Sector": loc.get("setor"),
                "Floor": loc.get("andar"),
                "ParkingSpot": loc.get("vaga"),
                "Description": loc.get("descricao"),
                "Coordinates": {
                    "X": loc.get("coordenadas", {}).get("x"),
                    "Y": loc.get("coordenadas", {}).get("y")
                },
                "Zone": loc.get("zona")
            }
        
        # Adiciona instruções se disponíveis
        if "instrucoes_localizacao" in moto:
            instrucoes_text = moto["instrucoes_localizacao"]
            formatted["LocationInstructions"] = instrucoes_text.split("\n")
        
        return formatted
    
    @staticmethod
    def format_moto_list(motos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Formata lista de motos para .NET"""
        formatted_motos = [DotNetFormatter.format_moto(m) for m in motos]
        
        return {
            "IsSuccess": True,
            "Data": {
                "Motorcycles": formatted_motos,
                "Summary": {
                    "TotalCount": len(motos),
                    "AvailableCount": len([m for m in motos if m.get("status") == "disponivel"]),
                    "InUseCount": len([m for m in motos if m.get("status") == "em_uso"]),
                    "MaintenanceCount": len([m for m in motos if m.get("status") == "manutencao"]),
                },
            },
            "Message": "Data retrieved successfully",
            "Timestamp": datetime.now().isoformat(),
        }
    
    @staticmethod
    def format_moto_detail(moto: Dict[str, Any]) -> Dict[str, Any]:
        """Formata detalhes de moto para .NET"""
        return {
            "IsSuccess": True,
            "Data": {
                "Motorcycle": DotNetFormatter.format_moto(moto),
                "Found": True
            },
            "Message": "Motorcycle found successfully",
            "Timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def format_error(message: str) -> Dict[str, Any]:
        """Formata erro para .NET"""
        return {
            "IsSuccess": False,
            "Error": message,
            "Message": "Operation failed",
            "Timestamp": datetime.now().isoformat()
        }
