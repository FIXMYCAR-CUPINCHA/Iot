# Integração Java - VisionMoto

## Spring Boot Integration

Esta pasta contém os arquivos necessários para integração com aplicações Java Spring Boot.

### Endpoints Disponíveis

#### 1. Status das Motos
```
GET /api/java/motos/status
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "motos": [
      {
        "motoId": "MOTO001",
        "modelo": "Honda CG 160",
        "placa": "ABC-1234",
        "status": "disponivel",
        "nivelBateria": 95,
        "latitude": 10.5,
        "longitude": 20.3,
        "zona": "A1",
        "ultimaAtualizacao": "2025-10-11T20:40:00"
      }
    ],
    "resumo": {
      "total": 6,
      "disponiveis": 3,
      "emUso": 2,
      "manutencao": 1
    }
  },
  "timestamp": "2025-10-11T20:40:00"
}
```

#### 2. Gerenciamento de Alertas
```
GET /api/java/alertas
POST /api/java/alertas
```

### Exemplo de Integração Spring Boot

```java
@RestController
@RequestMapping("/api/mottu")
public class MottuController {
    
    @Autowired
    private VisionMotoService visionMotoService;
    
    @GetMapping("/motos")
    public ResponseEntity<MotosResponse> getMotos() {
        try {
            MotosResponse response = visionMotoService.getMotosStatus();
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(500).build();
        }
    }
    
    @PostMapping("/alertas")
    public ResponseEntity<String> criarAlerta(@RequestBody AlertaRequest request) {
        try {
            visionMotoService.criarAlerta(request);
            return ResponseEntity.ok("Alerta criado com sucesso");
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Erro ao criar alerta");
        }
    }
}
```

### Configuração

1. Adicione no `application.properties`:
```properties
visionmoto.api.url=http://localhost:5001
visionmoto.api.timeout=5000
```

2. Configure o cliente HTTP:
```java
@Configuration
public class VisionMotoConfig {
    
    @Bean
    public RestTemplate restTemplate() {
        RestTemplate restTemplate = new RestTemplate();
        restTemplate.setRequestFactory(new HttpComponentsClientHttpRequestFactory());
        return restTemplate;
    }
}
```

### DTOs Recomendados

```java
public class MotoDto {
    private String motoId;
    private String modelo;
    private String placa;
    private String status;
    private Integer nivelBateria;
    private Double latitude;
    private Double longitude;
    private String zona;
    private LocalDateTime ultimaAtualizacao;
    
    // getters e setters
}

public class AlertaDto {
    private String tipo;
    private String severidade;
    private String titulo;
    private String descricao;
    private String motoId;
    private String zona;
    
    // getters e setters
}
```
