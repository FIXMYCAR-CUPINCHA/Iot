// VisionMoto - Mapa Visual do Pátio
// Visualização em grid das motos no pátio

class PatioMap {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error('Canvas não encontrado:', canvasId);
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.motos = [];
        this.selectedMoto = null;
        
        // Configurações do mapa
        this.config = {
            gridSize: 50,
            padding: 40,
            motoRadius: 15,
            colors: {
                disponivel: '#4ade80',
                em_uso: '#f59e0b',
                manutencao: '#ef4444',
                parada: '#94a3b8',
                background: '#1e293b',
                grid: '#334155',
                text: '#e2e8f0',
                zone: '#475569'
            }
        };
        
        // Ajusta tamanho do canvas
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        
        // Eventos de mouse
        this.canvas.addEventListener('click', (e) => this.handleClick(e));
        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        
        // Inicia atualização
        this.startUpdating();
    }
    
    resizeCanvas() {
        const container = this.canvas.parentElement;
        this.canvas.width = container.clientWidth;
        this.canvas.height = Math.min(600, container.clientWidth * 0.6);
        this.render();
    }
    
    async loadMotos() {
        try {
            const response = await fetch('/api/mobile/motos');
            const data = await response.json();
            this.motos = data.motos || [];
            this.render();
        } catch (error) {
            console.error('Erro ao carregar motos:', error);
        }
    }
    
    startUpdating() {
        this.loadMotos();
        setInterval(() => this.loadMotos(), 3000);
    }
    
    render() {
        if (!this.ctx) return;
        
        const { width, height } = this.canvas;
        const { colors } = this.config;
        
        // Limpa canvas
        this.ctx.fillStyle = colors.background;
        this.ctx.fillRect(0, 0, width, height);
        
        // Desenha grid
        this.drawGrid();
        
        // Desenha zonas
        this.drawZones();
        
        // Desenha motos
        this.drawMotos();
        
        // Desenha legenda
        this.drawLegend();
        
        // Desenha info da moto selecionada
        if (this.selectedMoto) {
            this.drawMotoInfo();
        }
    }
    
    drawGrid() {
        const { width, height } = this.canvas;
        const { padding, gridSize, colors } = this.config;
        
        this.ctx.strokeStyle = colors.grid;
        this.ctx.lineWidth = 0.5;
        
        // Linhas verticais
        for (let x = padding; x < width - padding; x += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, padding);
            this.ctx.lineTo(x, height - padding);
            this.ctx.stroke();
        }
        
        // Linhas horizontais
        for (let y = padding; y < height - padding; y += gridSize) {
            this.ctx.beginPath();
            this.ctx.moveTo(padding, y);
            this.ctx.lineTo(width - padding, y);
            this.ctx.stroke();
        }
    }
    
    drawZones() {
        const { width, height } = this.canvas;
        const { padding, colors } = this.config;
        
        // Define zonas do pátio (A1, A2, B1, B2, C1, C2)
        const zoneWidth = (width - 2 * padding) / 3;
        const zoneHeight = (height - 2 * padding) / 2;
        
        const zones = [
            { name: 'A1', x: 0, y: 0 },
            { name: 'A2', x: 1, y: 0 },
            { name: 'A3', x: 2, y: 0 },
            { name: 'B1', x: 0, y: 1 },
            { name: 'B2', x: 1, y: 1 },
            { name: 'B3', x: 2, y: 1 }
        ];
        
        this.ctx.font = '14px Inter, sans-serif';
        this.ctx.fillStyle = colors.zone;
        
        zones.forEach(zone => {
            const x = padding + zone.x * zoneWidth;
            const y = padding + zone.y * zoneHeight;
            
            // Desenha borda da zona
            this.ctx.strokeStyle = colors.zone;
            this.ctx.lineWidth = 2;
            this.ctx.strokeRect(x, y, zoneWidth, zoneHeight);
            
            // Desenha nome da zona
            this.ctx.fillStyle = colors.text;
            this.ctx.fillText(zone.name, x + 10, y + 25);
        });
    }
    
    drawMotos() {
        const { width, height } = this.canvas;
        const { padding, motoRadius, colors } = this.config;
        
        const mapWidth = width - 2 * padding;
        const mapHeight = height - 2 * padding;
        
        this.motos.forEach((moto, index) => {
            // Calcula posição no canvas baseado em coordenadas ou zona
            let x, y;
            
            if (moto.localizacao_x !== undefined && moto.localizacao_y !== undefined) {
                // Usa coordenadas reais
                x = padding + (moto.localizacao_x / 100) * mapWidth;
                y = padding + (moto.localizacao_y / 100) * mapHeight;
            } else {
                // Distribui por zona
                const zoneMap = {
                    'A1': [0, 0], 'A2': [1, 0], 'A3': [2, 0],
                    'B1': [0, 1], 'B2': [1, 1], 'B3': [2, 1]
                };
                const zonePos = zoneMap[moto.zona] || [0, 0];
                const zoneWidth = mapWidth / 3;
                const zoneHeight = mapHeight / 2;
                
                // Posição baseada no index para consistência
                const seed = index * 123.456;
                x = padding + zonePos[0] * zoneWidth + (Math.sin(seed) * 0.5 + 0.5) * zoneWidth * 0.8 + zoneWidth * 0.1;
                y = padding + zonePos[1] * zoneHeight + (Math.cos(seed) * 0.5 + 0.5) * zoneHeight * 0.8 + zoneHeight * 0.1;
            }
            
            // Cor baseada no status
            const color = colors[moto.status] || colors.parada;
            
            // Desenha círculo da moto
            this.ctx.beginPath();
            this.ctx.arc(x, y, motoRadius, 0, Math.PI * 2);
            this.ctx.fillStyle = color;
            this.ctx.fill();
            
            // Borda
            this.ctx.strokeStyle = this.selectedMoto?.id === moto.id ? '#fff' : color;
            this.ctx.lineWidth = this.selectedMoto?.id === moto.id ? 3 : 1;
            this.ctx.stroke();
            
            // Ícone de bateria
            if (moto.bateria !== undefined) {
                this.drawBatteryIcon(x, y - motoRadius - 8, moto.bateria);
            }
            
            // Placa (se selecionada)
            if (this.selectedMoto?.id === moto.id) {
                this.ctx.fillStyle = colors.text;
                this.ctx.font = '10px Inter, sans-serif';
                this.ctx.textAlign = 'center';
                this.ctx.fillText(moto.placa, x, y + motoRadius + 12);
            }
            
            // Salva posição para detecção de clique
            moto._renderX = x;
            moto._renderY = y;
        });
    }
    
    drawBatteryIcon(x, y, level) {
        const width = 12;
        const height = 6;
        
        // Cor baseada no nível
        let color;
        if (level > 60) color = '#4ade80';
        else if (level > 30) color = '#f59e0b';
        else color = '#ef4444';
        
        // Desenha bateria
        this.ctx.fillStyle = color;
        this.ctx.fillRect(x - width/2, y - height/2, width * (level/100), height);
        
        this.ctx.strokeStyle = '#e2e8f0';
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(x - width/2, y - height/2, width, height);
    }
    
    drawLegend() {
        const { width } = this.canvas;
        const { colors } = this.config;
        
        const legendX = width - 150;
        const legendY = 20;
        const itemHeight = 25;
        
        const items = [
            { label: 'Disponível', color: colors.disponivel },
            { label: 'Em Uso', color: colors.em_uso },
            { label: 'Manutenção', color: colors.manutencao },
            { label: 'Parada', color: colors.parada }
        ];
        
        this.ctx.font = '12px Inter, sans-serif';
        
        items.forEach((item, index) => {
            const y = legendY + index * itemHeight;
            
            // Círculo
            this.ctx.beginPath();
            this.ctx.arc(legendX, y, 6, 0, Math.PI * 2);
            this.ctx.fillStyle = item.color;
            this.ctx.fill();
            
            // Label
            this.ctx.fillStyle = colors.text;
            this.ctx.textAlign = 'left';
            this.ctx.fillText(item.label, legendX + 15, y + 4);
        });
        
        // Total de motos
        this.ctx.fillStyle = colors.text;
        this.ctx.font = 'bold 14px Inter, sans-serif';
        this.ctx.fillText(`Total: ${this.motos.length} motos`, legendX - 10, legendY + items.length * itemHeight + 10);
    }
    
    drawMotoInfo() {
        const moto = this.selectedMoto;
        const { colors } = this.config;
        
        // Painel de informações
        const panelX = 10;
        const panelY = 10;
        const panelWidth = 250;
        const panelHeight = 180;
        
        // Fundo
        this.ctx.fillStyle = 'rgba(30, 41, 59, 0.95)';
        this.ctx.fillRect(panelX, panelY, panelWidth, panelHeight);
        
        // Borda
        this.ctx.strokeStyle = colors[moto.status] || colors.parada;
        this.ctx.lineWidth = 2;
        this.ctx.strokeRect(panelX, panelY, panelWidth, panelHeight);
        
        // Informações
        this.ctx.fillStyle = colors.text;
        this.ctx.font = 'bold 14px Inter, sans-serif';
        this.ctx.textAlign = 'left';
        
        let y = panelY + 25;
        const lineHeight = 22;
        
        this.ctx.fillText(`🏍️ ${moto.placa}`, panelX + 10, y);
        y += lineHeight;
        
        this.ctx.font = '12px Inter, sans-serif';
        this.ctx.fillText(`Modelo: ${moto.modelo}`, panelX + 10, y);
        y += lineHeight;
        
        // Status com cor
        this.ctx.fillText('Status: ', panelX + 10, y);
        this.ctx.fillStyle = colors[moto.status] || colors.parada;
        this.ctx.fillText(moto.status, panelX + 60, y);
        this.ctx.fillStyle = colors.text;
        y += lineHeight;
        
        this.ctx.fillText(`Bateria: ${moto.bateria}%`, panelX + 10, y);
        y += lineHeight;
        
        this.ctx.fillText(`Zona: ${moto.zona}`, panelX + 10, y);
        y += lineHeight;
        
        if (moto.setor) {
            this.ctx.fillText(`Setor: ${moto.setor}`, panelX + 10, y);
            y += lineHeight;
        }
        
        if (moto.vaga) {
            this.ctx.fillText(`Vaga: ${moto.vaga}`, panelX + 10, y);
        }
    }
    
    handleClick(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        // Verifica se clicou em alguma moto
        let clicked = false;
        for (const moto of this.motos) {
            if (moto._renderX && moto._renderY) {
                const dx = x - moto._renderX;
                const dy = y - moto._renderY;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance <= this.config.motoRadius) {
                    this.selectedMoto = moto;
                    clicked = true;
                    break;
                }
            }
        }
        
        if (!clicked) {
            this.selectedMoto = null;
        }
        
        this.render();
    }
    
    handleMouseMove(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        // Verifica se está sobre alguma moto
        let overMoto = false;
        for (const moto of this.motos) {
            if (moto._renderX && moto._renderY) {
                const dx = x - moto._renderX;
                const dy = y - moto._renderY;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance <= this.config.motoRadius) {
                    overMoto = true;
                    break;
                }
            }
        }
        
        this.canvas.style.cursor = overMoto ? 'pointer' : 'default';
    }
}

// Inicializa quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    const patioMap = new PatioMap('patio-canvas');
    window.patioMap = patioMap; // Expõe globalmente para debug
});
