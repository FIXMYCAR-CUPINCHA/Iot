#!/usr/bin/env python3
"""
Formatador de respostas para Java/Spring Boot
"""

from typing import Dict, Any, List
from datetime import datetime


class JavaFormatter:
    """Formata respostas para o padrão Java (camelCase)"""
    
    @staticmethod
    def format_moto(moto: Dict[str, Any]) -> Dict[str, Any]:
        """Formata dados de moto para Java"""
        formatted = {
            "motoId": moto.get("id"),
            "modelo": moto.get("modelo"),
            "placa": moto.get("placa"),
            "status": moto.get("status"),
            "nivelBateria": moto.get("bateria"),
            "latitude": moto.get("localizacao_x"),
            "longitude": moto.get("localizacao_y"),
            "zona": moto.get("zona"),
            "endereco": moto.get("endereco"),
            "setor": moto.get("setor"),
            "andar": moto.get("andar"),
            "vaga": moto.get("vaga"),
            "descricaoLocalizacao": moto.get("descricao_localizacao"),
            "ultimaAtualizacao": moto.get("ultima_atualizacao"),
            "emUsoPor": moto.get("em_uso_por"),
        }
        
        # Adiciona localização completa se disponível
        if "localizacao_completa" in moto:
            loc = moto["localizacao_completa"]
            formatted["localizacaoCompleta"] = {
                "endereco": loc.get("endereco"),
                "setor": loc.get("setor"),
                "andar": loc.get("andar"),
                "vaga": loc.get("vaga"),
                "descricao": loc.get("descricao"),
                "coordenadas": {
                    "latitude": loc.get("coordenadas", {}).get("x"),
                    "longitude": loc.get("coordenadas", {}).get("y")
                },
                "zona": loc.get("zona")
            }
        
        # Adiciona instruções se disponíveis
        if "instrucoes_localizacao" in moto:
            instrucoes_text = moto["instrucoes_localizacao"]
            formatted["instrucoesLocalizacao"] = instrucoes_text.split("\n")
        
        return formatted
    
    @staticmethod
    def format_moto_list(motos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Formata lista de motos para Java"""
        formatted_motos = [JavaFormatter.format_moto(m) for m in motos]
        
        return {
            "success": True,
            "data": {
                "motos": formatted_motos,
                "resumo": {
                    "total": len(motos),
                    "disponiveis": len([m for m in motos if m.get("status") == "disponivel"]),
                    "emUso": len([m for m in motos if m.get("status") == "em_uso"]),
                    "manutencao": len([m for m in motos if m.get("status") == "manutencao"]),
                },
            },
            "timestamp": datetime.now().isoformat(),
        }
    
    @staticmethod
    def format_moto_detail(moto: Dict[str, Any]) -> Dict[str, Any]:
        """Formata detalhes de moto para Java"""
        return {
            "success": True,
            "data": {
                "moto": JavaFormatter.format_moto(moto),
                "encontrada": True
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def format_error(message: str) -> Dict[str, Any]:
        """Formata erro para Java"""
        return {
            "success": False,
            "error": message,
            "timestamp": datetime.now().isoformat()
        }
