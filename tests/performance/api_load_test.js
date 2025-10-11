// Teste de carga para VisionMoto API usando k6
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Métricas customizadas
export const errorRate = new Rate('errors');

// Configuração do teste
export const options = {
  stages: [
    { duration: '30s', target: 5 },   // Ramp up para 5 usuários
    { duration: '1m', target: 10 },   // Mantém 10 usuários
    { duration: '30s', target: 20 },  // Ramp up para 20 usuários
    { duration: '1m', target: 20 },   // Mantém 20 usuários
    { duration: '30s', target: 0 },   // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% das requisições devem ser < 500ms
    http_req_failed: ['rate<0.1'],    // Taxa de erro < 10%
    errors: ['rate<0.1'],             // Taxa de erro customizada < 10%
  },
};

const BASE_URL = 'http://localhost:5001';

export default function () {
  // Teste 1: Health Check
  let response = http.get(`${BASE_URL}/health`);
  let success = check(response, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 200ms': (r) => r.timings.duration < 200,
  });
  errorRate.add(!success);

  sleep(1);

  // Teste 2: Java API - Status das motos
  response = http.get(`${BASE_URL}/api/java/motos/status`);
  success = check(response, {
    'java motos status is 200': (r) => r.status === 200,
    'java motos has data': (r) => {
      try {
        const data = JSON.parse(r.body);
        return data.success === true && data.data.motos.length > 0;
      } catch {
        return false;
      }
    },
  });
  errorRate.add(!success);

  sleep(1);

  // Teste 3: .NET API - Motorcycle Data
  response = http.get(`${BASE_URL}/api/dotnet/Dashboard/GetMotorcycleData`);
  success = check(response, {
    'dotnet motorcycle data is 200': (r) => r.status === 200,
    'dotnet has motorcycles': (r) => {
      try {
        const data = JSON.parse(r.body);
        return data.IsSuccess === true && data.Data.Motorcycles.length > 0;
      } catch {
        return false;
      }
    },
  });
  errorRate.add(!success);

  sleep(1);

  // Teste 4: Mobile API - Login
  const loginPayload = JSON.stringify({
    email: 'test@mottu.com',
    senha: '123456'
  });

  response = http.post(`${BASE_URL}/api/mobile/auth/login`, loginPayload, {
    headers: { 'Content-Type': 'application/json' },
  });
  
  success = check(response, {
    'mobile login is 200': (r) => r.status === 200,
    'mobile login returns token': (r) => {
      try {
        const data = JSON.parse(r.body);
        return data.token && data.user;
      } catch {
        return false;
      }
    },
  });
  errorRate.add(!success);

  sleep(1);

  // Teste 5: Mobile API - Lista motos
  response = http.get(`${BASE_URL}/api/mobile/motos`);
  success = check(response, {
    'mobile motos is 200': (r) => r.status === 200,
    'mobile motos has data': (r) => {
      try {
        const data = JSON.parse(r.body);
        return data.motos && data.total > 0;
      } catch {
        return false;
      }
    },
  });
  errorRate.add(!success);

  sleep(1);

  // Teste 6: IoT API - Devices
  response = http.get(`${BASE_URL}/api/iot/devices`);
  success = check(response, {
    'iot devices is 200': (r) => r.status === 200,
    'iot devices has data': (r) => {
      try {
        const data = JSON.parse(r.body);
        return data.devices && data.total > 0;
      } catch {
        return false;
      }
    },
  });
  errorRate.add(!success);

  sleep(1);

  // Teste 7: Database API - Analytics
  response = http.get(`${BASE_URL}/api/database/analytics`);
  success = check(response, {
    'database analytics is 200': (r) => r.status === 200,
    'database analytics has data': (r) => {
      try {
        const data = JSON.parse(r.body);
        return data.success === true && data.analytics;
      } catch {
        return false;
      }
    },
  });
  errorRate.add(!success);

  sleep(2);
}

export function handleSummary(data) {
  return {
    'performance-report.json': JSON.stringify(data),
    'performance-report.html': htmlReport(data),
  };
}

function htmlReport(data) {
  return `
<!DOCTYPE html>
<html>
<head>
    <title>VisionMoto Performance Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .metric { margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }
        .pass { background: #d4edda; color: #155724; }
        .fail { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>VisionMoto API Performance Report</h1>
    <h2>Test Summary</h2>
    <div class="metric">
        <strong>Total Requests:</strong> ${data.metrics.http_reqs.values.count}
    </div>
    <div class="metric">
        <strong>Failed Requests:</strong> ${data.metrics.http_req_failed.values.rate * 100}%
    </div>
    <div class="metric">
        <strong>Average Response Time:</strong> ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms
    </div>
    <div class="metric">
        <strong>95th Percentile:</strong> ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms
    </div>
    <div class="metric ${data.metrics.http_req_duration.values['p(95)'] < 500 ? 'pass' : 'fail'}">
        <strong>Performance Threshold:</strong> ${data.metrics.http_req_duration.values['p(95)'] < 500 ? 'PASSED' : 'FAILED'}
    </div>
</body>
</html>
  `;
}
