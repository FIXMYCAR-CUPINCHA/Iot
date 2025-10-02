#!/usr/bin/env python3
"""
VisionMoto - Sistema Permanente
Script para rodar o sistema completo permanentemente sem parar
"""

import sys
import os
import time
import threading
import subprocess
import signal
from datetime import datetime

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.detection.moto_detector import MotoDetector
from src.utils.database import DatabaseManager
from src.iot.sensor_simulator import IoTDeviceSimulator
import requests

class VisionMotoPermanent:
    """Sistema VisionMoto rodando permanentemente"""
    
    def __init__(self):
        self.detector = MotoDetector()
        self.db = DatabaseManager()
        self.iot_simulator = IoTDeviceSimulator()
        self.backend_process = None
        self.running = False
        self.detection_thread = None
        self.stats = {
            'total_frames': 0,
            'total_detections': 0,
            'start_time': None,
            'last_detection': None
        }
        
        # Configura handler para CTRL+C
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handler para parar o sistema graciosamente"""
        print("\n🛑 Recebido sinal de parada...")
        self.stop_system()
        sys.exit(0)
        
    def start_backend(self):
        """Inicia o backend Flask"""
        print("🚀 Iniciando backend Flask...")
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, '-m', 'src.backend.app'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            time.sleep(3)
            
            try:
                response = requests.get("http://localhost:5000/metrics", timeout=2)
                if response.status_code == 200:
                    print("✅ Backend Flask iniciado com sucesso!")
                    return True
            except requests.exceptions.RequestException:
                pass
                
            print("❌ Falha ao iniciar backend Flask")
            return False
            
        except Exception as e:
            print(f"❌ Erro ao iniciar backend: {e}")
            return False
    
    def stop_backend(self):
        """Para o backend Flask"""
        if self.backend_process:
            print("🛑 Parando backend Flask...")
            self.backend_process.terminate()
            self.backend_process.wait()
            print("✅ Backend Flask parado!")
    
    def continuous_detection(self):
        """Executa detecção continuamente"""
        print("🔍 Iniciando detecção contínua...")
        
        video_path = "assets/sample_video.mp4"
        if not os.path.exists(video_path):
            print(f"❌ Vídeo não encontrado: {video_path}")
            return False
        
        import cv2
        
        while self.running:
            try:
                cap = cv2.VideoCapture(video_path)
                if not cap.isOpened():
                    print("❌ Erro ao abrir vídeo, tentando novamente em 5s...")
                    time.sleep(5)
                    continue
                
                print("📹 Processando vídeo em loop contínuo...")
                
                while self.running:
                    ret, frame = cap.read()
                    if not ret:
                        # Reinicia o vídeo
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        continue
                    
                    self.stats['total_frames'] += 1
                    
                    # Detecção
                    detections = self.detector.detect_motos(frame)
                    moto_detections = self.detector.filter_motos(detections)
                    
                    if moto_detections:
                        self.stats['total_detections'] += len(moto_detections)
                        self.stats['last_detection'] = datetime.now()
                    
                    # Calcula métricas
                    elapsed = time.time() - self.stats['start_time']
                    current_fps = self.stats['total_frames'] / elapsed if elapsed > 0 else 0
                    
                    # Desenha detecções
                    self._draw_detections(frame, moto_detections)
                    
                    # Salva dados
                    if moto_detections:
                        self.db.save_detections(self.stats['total_frames'], moto_detections, current_fps)
                        
                        # Envia para API
                        for det in moto_detections:
                            detection_data = {
                                'frame': self.stats['total_frames'],
                                'class': det['class'],
                                'class_name': det['class_name'],
                                'confidence': det['confidence'],
                                'bbox': det['bbox'],
                                'area': det['area'],
                                'metrics': {
                                    'avg_fps': current_fps,
                                    'total_detections': len(moto_detections),
                                    'unique_motos': len(set(f"{d['class']}_{d['bbox']}" for d in moto_detections)),
                                    'detection_rate': len(moto_detections) / elapsed if elapsed > 0 else 0
                                }
                            }
                            
                            try:
                                requests.post("http://localhost:5000/detections", 
                                            json=detection_data, timeout=1)
                            except requests.exceptions.RequestException:
                                pass
                    
                    # Adiciona informações na tela
                    self._draw_info(frame, self.stats['total_frames'], current_fps, len(moto_detections))
                    
                    # Exibe frame
                    cv2.imshow("VisionMoto - Sistema Permanente", frame)
                    
                    # Controles (ESC para sair)
                    key = cv2.waitKey(1) & 0xFF
                    if key == 27:  # ESC
                        self.running = False
                        break
                
                cap.release()
                
            except Exception as e:
                print(f"❌ Erro na detecção: {e}")
                print("🔄 Tentando reiniciar em 5 segundos...")
                time.sleep(5)
        
        cv2.destroyAllWindows()
        print("✅ Detecção contínua finalizada")
    
    def _draw_detections(self, frame, detections):
        """Desenha detecções no frame"""
        import cv2
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            class_name = det['class_name']
            
            color = (0, 255, 0) if det['class'] == 3 else (255, 0, 0)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            label = f"{class_name}: {conf:.2f}"
            cv2.putText(frame, label, (x1, y1-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
    
    def _draw_info(self, frame, frame_count, fps, detections_count):
        """Desenha informações na tela"""
        import cv2
        
        # Calcula tempo de execução
        elapsed = time.time() - self.stats['start_time']
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        
        info_text = [
            f"Frame: {frame_count}",
            f"FPS: {fps:.1f}",
            f"Detecções: {detections_count}",
            f"Total Detecções: {self.stats['total_detections']}",
            f"Tempo: {hours:02d}:{minutes:02d}:{seconds:02d}",
            f"Status: RODANDO PERMANENTE",
            f"ESC para sair"
        ]
        
        for i, text in enumerate(info_text):
            cv2.putText(frame, text, (10, 30 + i*25), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    def status_monitor(self):
        """Monitor de status do sistema"""
        while self.running:
            time.sleep(30)  # Atualiza a cada 30 segundos
            
            if not self.running:
                break
                
            elapsed = time.time() - self.stats['start_time']
            avg_fps = self.stats['total_frames'] / elapsed if elapsed > 0 else 0
            
            print(f"📊 STATUS - Frames: {self.stats['total_frames']}, "
                  f"Detecções: {self.stats['total_detections']}, "
                  f"FPS: {avg_fps:.1f}, "
                  f"Tempo: {elapsed/60:.1f}min")
    
    def start_system(self):
        """Inicia o sistema completo permanentemente"""
        print("🎯 VisionMoto - Sistema Permanente")
        print("=" * 50)
        print("Sistema rodando 24/7 - Pressione ESC na janela do vídeo para parar")
        print("Ou use CTRL+C no terminal")
        print("=" * 50)
        
        try:
            self.running = True
            self.stats['start_time'] = time.time()
            
            # Inicializa banco de dados
            print("🗄️ Inicializando banco de dados...")
            self.db.initialize()
            print("✅ Banco de dados inicializado")
            
            # Inicia backend
            if not self.start_backend():
                print("⚠️ Continuando sem backend...")
            
            # Inicia simulação IoT
            print("📡 Iniciando simulação IoT...")
            self.iot_simulator.start_simulation()
            
            # Inicia monitor de status em thread separada
            status_thread = threading.Thread(target=self.status_monitor, daemon=True)
            status_thread.start()
            
            # Inicia detecção contínua
            print("🔍 Iniciando detecção contínua...")
            print("🌐 Dashboard disponível em: http://localhost:5000")
            
            # Executa detecção na thread principal
            self.continuous_detection()
            
        except KeyboardInterrupt:
            print("\n⏹️ Sistema interrompido pelo usuário")
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            self.stop_system()
    
    def stop_system(self):
        """Para o sistema graciosamente"""
        if not self.running:
            return
            
        print("\n🧹 Parando sistema...")
        self.running = False
        
        # Para simulação IoT
        print("📡 Parando simulação IoT...")
        self.iot_simulator.stop_simulation()
        
        # Para backend
        self.stop_backend()
        
        # Mostra relatório final
        self._show_final_report()
        
        print("✅ Sistema parado com sucesso!")
    
    def _show_final_report(self):
        """Mostra relatório final"""
        elapsed = time.time() - self.stats['start_time']
        avg_fps = self.stats['total_frames'] / elapsed if elapsed > 0 else 0
        
        print("\n📊 RELATÓRIO FINAL:")
        print("=" * 40)
        print(f"Tempo total de execução: {elapsed/60:.1f} minutos")
        print(f"Frames processados: {self.stats['total_frames']}")
        print(f"Total de detecções: {self.stats['total_detections']}")
        print(f"FPS médio: {avg_fps:.2f}")
        if self.stats['last_detection']:
            print(f"Última detecção: {self.stats['last_detection'].strftime('%H:%M:%S')}")

def main():
    """Função principal"""
    system = VisionMotoPermanent()
    system.start_system()

if __name__ == "__main__":
    main()
