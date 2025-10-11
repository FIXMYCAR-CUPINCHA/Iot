# Integração .NET - VisionMoto

## ASP.NET Core Integration

Esta pasta contém os arquivos necessários para integração com aplicações .NET.

### Endpoints Disponíveis

#### 1. Dados das Motocicletas
```
GET /api/dotnet/Dashboard/GetMotorcycleData
```

**Resposta:**
```json
{
  "IsSuccess": true,
  "Data": {
    "Motorcycles": [
      {
        "Id": "MOTO001",
        "Model": "Honda CG 160",
        "LicensePlate": "ABC-1234",
        "Status": "disponivel",
        "BatteryLevel": 95,
        "LocationX": 10.5,
        "LocationY": 20.3,
        "Zone": "A1",
        "LastUpdate": "2025-10-11T20:40:00"
      }
    ],
    "Summary": {
      "TotalCount": 6,
      "AvailableCount": 3,
      "InUseCount": 2,
      "MaintenanceCount": 1
    }
  },
  "Message": "Data retrieved successfully",
  "Timestamp": "2025-10-11T20:40:00"
}
```

#### 2. Relatório de Uso
```
POST /api/dotnet/Reports/GenerateUsageReport
```

**Request:**
```json
{
  "StartDate": "2025-10-01T00:00:00",
  "EndDate": "2025-10-11T23:59:59"
}
```

### Exemplo de Integração ASP.NET Core

```csharp
[ApiController]
[Route("api/[controller]")]
public class MottuController : ControllerBase
{
    private readonly IVisionMotoService _visionMotoService;
    
    public MottuController(IVisionMotoService visionMotoService)
    {
        _visionMotoService = visionMotoService;
    }
    
    [HttpGet("motorcycles")]
    public async Task<ActionResult<MotorcycleResponse>> GetMotorcycles()
    {
        try
        {
            var response = await _visionMotoService.GetMotorcycleDataAsync();
            return Ok(response);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { Error = ex.Message });
        }
    }
    
    [HttpPost("reports/usage")]
    public async Task<ActionResult<UsageReportResponse>> GenerateUsageReport([FromBody] UsageReportRequest request)
    {
        try
        {
            var response = await _visionMotoService.GenerateUsageReportAsync(request);
            return Ok(response);
        }
        catch (Exception ex)
        {
            return StatusCode(500, new { Error = ex.Message });
        }
    }
}
```

### Configuração

1. Adicione no `appsettings.json`:
```json
{
  "VisionMoto": {
    "ApiUrl": "http://localhost:5001",
    "Timeout": 5000
  }
}
```

2. Configure o HttpClient:
```csharp
public void ConfigureServices(IServiceCollection services)
{
    services.AddHttpClient<IVisionMotoService, VisionMotoService>(client =>
    {
        client.BaseAddress = new Uri("http://localhost:5001");
        client.Timeout = TimeSpan.FromSeconds(5);
    });
}
```

### Models Recomendados

```csharp
public class MotorcycleDto
{
    public string Id { get; set; }
    public string Model { get; set; }
    public string LicensePlate { get; set; }
    public string Status { get; set; }
    public int BatteryLevel { get; set; }
    public double LocationX { get; set; }
    public double LocationY { get; set; }
    public string Zone { get; set; }
    public DateTime LastUpdate { get; set; }
}

public class MotorcycleResponse
{
    public bool IsSuccess { get; set; }
    public MotorcycleData Data { get; set; }
    public string Message { get; set; }
    public DateTime Timestamp { get; set; }
}

public class MotorcycleData
{
    public List<MotorcycleDto> Motorcycles { get; set; }
    public MotorcycleSummary Summary { get; set; }
}

public class MotorcycleSummary
{
    public int TotalCount { get; set; }
    public int AvailableCount { get; set; }
    public int InUseCount { get; set; }
    public int MaintenanceCount { get; set; }
}

public class UsageReportRequest
{
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }
}

public class UsageReportResponse
{
    public bool IsSuccess { get; set; }
    public List<UsageReportItem> ReportData { get; set; }
    public DateTime GeneratedAt { get; set; }
    public ReportPeriod Period { get; set; }
}
```

### Service Implementation

```csharp
public interface IVisionMotoService
{
    Task<MotorcycleResponse> GetMotorcycleDataAsync();
    Task<UsageReportResponse> GenerateUsageReportAsync(UsageReportRequest request);
}

public class VisionMotoService : IVisionMotoService
{
    private readonly HttpClient _httpClient;
    
    public VisionMotoService(HttpClient httpClient)
    {
        _httpClient = httpClient;
    }
    
    public async Task<MotorcycleResponse> GetMotorcycleDataAsync()
    {
        var response = await _httpClient.GetAsync("/api/dotnet/Dashboard/GetMotorcycleData");
        response.EnsureSuccessStatusCode();
        
        var content = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<MotorcycleResponse>(content);
    }
    
    public async Task<UsageReportResponse> GenerateUsageReportAsync(UsageReportRequest request)
    {
        var json = JsonSerializer.Serialize(request);
        var content = new StringContent(json, Encoding.UTF8, "application/json");
        
        var response = await _httpClient.PostAsync("/api/dotnet/Reports/GenerateUsageReport", content);
        response.EnsureSuccessStatusCode();
        
        var responseContent = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<UsageReportResponse>(responseContent);
    }
}
```
