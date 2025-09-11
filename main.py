#!/usr/bin/env python3
"""
VisionMoto - Sistema de Detecção de Motos
Sistema principal de demonstração

Autor: VisionMoto Team
Data: 2024
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.detection.moto_detector import MotoDetector
from src.utils.database import DatabaseManager
from src.utils.metrics import MetricsCollector
import cv2
import time
import requests
import threading
from datetime import datetime

class VisionMotoSystem:
    """Sistema principal do VisionMoto"""
    
    def __init__(self):
        self.detector = MotoDetector()
        self.db = DatabaseManager()
        self.metrics = MetricsCollector()
        self.running = False
        self.api_url = "http://localhost:5000"
        self.total_detections = 0
        self.unique_motos = set()
        self.backend_running = False
        
    def initialize(self):
        """Inicializa o sistema"""
        print("🚀 Inicializando VisionMoto...")
        
        # Inicializa componentes
        self.db.initialize()
        print("✅ Banco de dados inicializado")
        
        # Verifica se o backend está rodando
        self._check_backend()
        
        print("✅ Sistema inicializado com sucesso!")
        
    def _check_backend(self):
        """Verifica se o backend está rodando"""
        try:
            response = requests.get(f"{self.api_url}/metrics", timeout=2)
            if response.status_code == 200:
                self.backend_running = True
                print("✅ Backend API conectado")
            else:
                print("⚠️ Backend API não disponível - executando modo offline")
        except requests.exceptions.RequestException:
            print("⚠️ Backend API não disponível - executando modo offline")
    
    def _send_to_api(self, detection_data):
        """Envia dados para a API"""
        if not self.backend_running:
            return
            
        try:
            response = requests.post(f"{self.api_url}/detections", 
                                  json=detection_data, timeout=1)
            if response.status_code != 201:
                print(f"⚠️ Erro ao enviar dados para API: {response.status_code}")
        except requests.exceptions.RequestException:
            # Silenciosamente falha se API não estiver disponível
            pass
        
    def run_detection(self, video_path="assets/sample_video.mp4", max_frames=200):
        """Executa detecção de motos"""
        print(f"🔍 Iniciando detecção em: {video_path}")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print("❌ Erro ao abrir vídeo")
            return False
        
        self.running = True
        frame_count = 0
        start_time = time.time()
        
        print("📹 Processando vídeo...")
        print("Controles: 'q' = sair, 's' = salvar frame")
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            
            # Detecção
            detections = self.detector.detect_motos(frame)
            moto_detections = self.detector.filter_motos(detections)
            
            # Calcula métricas
            elapsed = time.time() - start_time
            current_fps = frame_count / elapsed if elapsed > 0 else 0
            
            # Desenha detecções
            self._draw_detections(frame, moto_detections)
            
            # Atualiza contadores
            if moto_detections:
                self.total_detections += len(moto_detections)
                for det in moto_detections:
                    self.unique_motos.add(f"{det['class']}_{det['bbox']}")
                
                # Calcula taxa de detecção
                detection_rate = len(moto_detections) / elapsed if elapsed > 0 else 0
                
                # Salva dados localmente
                self.db.save_detections(frame_count, moto_detections, current_fps, 
                                     self.total_detections, len(self.unique_motos), detection_rate)
                
                # Envia para API em thread separada
                for det in moto_detections:
                    detection_data = {
                        'frame': frame_count,
                        'class': det['class'],
                        'class_name': det['class_name'],
                        'confidence': det['confidence'],
                        'bbox': det['bbox'],
                        'area': det['area'],
                        'metrics': {
                            'avg_fps': current_fps,
                            'total_detections': self.total_detections,
                            'unique_motos': len(self.unique_motos),
                            'detection_rate': detection_rate,
                            'elapsed_time': elapsed
                        }
                    }
                    threading.Thread(target=self._send_to_api, args=(detection_data,), daemon=True).start()
            
            # Adiciona informações na tela
            self._draw_info(frame, frame_count, current_fps, len(moto_detections))
            
            # Exibe frame
            cv2.imshow("VisionMoto - Sistema de Detecção", frame)
            
            # Controles
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite(f"frame_{frame_count}.jpg", frame)
                print(f"📸 Frame {frame_count} salvo!")
            
            # Limite de frames
            if frame_count >= max_frames:
                print(f"📊 Limite de frames atingido ({max_frames})")
                break
        
        # Limpeza
        cap.release()
        cv2.destroyAllWindows()
        
        # Relatório final
        self._show_report(frame_count, time.time() - start_time)
        
        return True
    
    def _draw_detections(self, frame, detections):
        """Desenha detecções no frame"""
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            class_name = det['class_name']
            
            # Cor baseada na classe
            color = (0, 255, 0) if det['class'] == 3 else (255, 0, 0)
            
            # Desenha bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Desenha label
            label = f"{class_name}: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    def _draw_info(self, frame, frame_count, fps, detections_count):
        """Desenha informações na tela"""
        info_text = [
            f"Frame: {frame_count}",
            f"FPS: {fps:.1f}",
            f"Detecções: {detections_count}",
            f"Status: {'Ativo' if self.running else 'Parado'}"
        ]
        
        for i, text in enumerate(info_text):
            cv2.putText(frame, text, (10, 30 + i*25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    def _show_report(self, frame_count, elapsed_time):
        """Mostra relatório final"""
        stats = self.db.get_statistics()
        
        print("\n📊 RELATÓRIO FINAL:")
        print("=" * 40)
        print(f"Frames processados: {frame_count}")
        print(f"Tempo total: {elapsed_time:.2f}s")
        print(f"FPS médio: {frame_count/elapsed_time:.2f}")
        print(f"Total de detecções: {stats['total_detections']}")
        print(f"Classes detectadas: {stats['unique_classes']}")
        
        print("\n📋 ÚLTIMAS DETECÇÕES:")
        print("=" * 30)
        
        recent = self.db.get_recent_detections(5)
        for i, det in enumerate(recent, 1):
            print(f"{i}. Frame {det['frame']} - {det['class_name']} "
                  f"(conf: {det['confidence']:.2f})")
    
    def stop(self):
        """Para o sistema"""
        self.running = False
        print("🛑 Sistema parado")

def main():
    """Função principal"""
    print("🎯 VisionMoto - Sistema de Detecção de Motos")
    print("=" * 50)
    
    system = VisionMotoSystem()
    
    try:
        # Inicializa sistema
        system.initialize()
        
        # Executa detecção
        success = system.run_detection()
        
        if success:
            print("\n✅ Sistema executado com sucesso!")
            print("🎉 VisionMoto funcionando perfeitamente!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Sistema interrompido pelo usuário")
        system.stop()
    except Exception as e:
        print(f"❌ Erro: {e}")
    finally:
        print("\n🧹 Limpeza concluída")

if __name__ == "__main__":
    main()
