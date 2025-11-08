#!/usr/bin/env python3
"""
Formatador de respostas para Mobile App
"""

from typing import Dict, Any, List
from datetime import datetime


class MobileFormatter:
    """Formata respostas para o padrão Mobile"""
    
    @staticmethod
    def format_moto(moto: Dict[str, Any]) -> Dict[str, Any]:
        """Formata dados de moto para mobile"""
        return {
            "id": moto.get("id"),
            "modelo": moto.get("modelo"),
            "placa": moto.get("placa"),
            "status": moto.get("status"),
            "bateria": moto.get("bateria"),
            "zona": moto.get("zona"),
            "endereco": moto.get("endereco"),
            "setor": moto.get("setor"),
            "andar": moto.get("andar"),
            "vaga": moto.get("vaga"),
            "descricao_localizacao": moto.get("descricao_localizacao"),
            "ultima_atualizacao": moto.get("ultima_atualizacao"),
            "localizacao_completa": moto.get("localizacao_completa"),
            "instrucoes_localizacao": moto.get("instrucoes_localizacao"),
        }
    
    @staticmethod
    def format_moto_list(motos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Formata lista de motos para mobile"""
        return {
            "motos": motos,
            "total": len(motos),
            "disponiveis": len([m for m in motos if m.get("status") == "disponivel"]),
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def format_moto_detail(moto: Dict[str, Any]) -> Dict[str, Any]:
        """Formata detalhes de moto para mobile"""
        return {
            "moto": MobileFormatter.format_moto(moto),
            "encontrada": True,
            "timestamp": datetime.now().isoformat()
        }
