# Integração Mobile App - VisionMoto

## React Native / Flutter Integration

Esta pasta contém os arquivos necessários para integração com aplicativos mobile.

### Endpoints Disponíveis

#### 1. Autenticação
```
POST /api/mobile/auth/login
```

**Request:**
```json
{
  "email": "usuario@mottu.com",
  "senha": "123456"
}
```

**Response:**
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user123",
    "nome": "Usuário Demo",
    "email": "usuario@mottu.com",
    "tipo": "usuario"
  },
  "expires_in": 86400
}
```

#### 2. Listar Motos Disponíveis
```
GET /api/mobile/motos
```

**Response:**
```json
{
  "motos": [
    {
      "id": "MOTO001",
      "modelo": "Honda CG 160",
      "placa": "ABC-1234",
      "status": "disponivel",
      "bateria": 95,
      "zona": "A1",
      "ultima_atualizacao": "2025-10-11T20:40:00"
    }
  ],
  "total": 6,
  "disponiveis": 3
}
```

#### 3. Reservar Moto
```
POST /api/mobile/motos/{moto_id}/reservar
```

**Request:**
```json
{
  "usuario_id": "user123"
}
```

**Response:**
```json
{
  "message": "Moto reservada com sucesso",
  "moto_id": "MOTO001"
}
```

### Exemplo React Native

```javascript
// services/VisionMotoAPI.js
class VisionMotoAPI {
  constructor() {
    this.baseURL = 'http://localhost:5001/api/mobile';
    this.token = null;
  }

  async login(email, senha) {
    try {
      const response = await fetch(`${this.baseURL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, senha }),
      });

      const data = await response.json();
      
      if (data.token) {
        this.token = data.token;
        await AsyncStorage.setItem('auth_token', data.token);
      }
      
      return data;
    } catch (error) {
      throw new Error('Erro ao fazer login: ' + error.message);
    }
  }

  async getMotos() {
    try {
      const response = await fetch(`${this.baseURL}/motos`, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
        },
      });

      return await response.json();
    } catch (error) {
      throw new Error('Erro ao buscar motos: ' + error.message);
    }
  }

  async reservarMoto(motoId, usuarioId) {
    try {
      const response = await fetch(`${this.baseURL}/motos/${motoId}/reservar`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ usuario_id: usuarioId }),
      });

      return await response.json();
    } catch (error) {
      throw new Error('Erro ao reservar moto: ' + error.message);
    }
  }
}

export default new VisionMotoAPI();
```

### Exemplo de Componente React Native

```javascript
// components/MotosList.js
import React, { useState, useEffect } from 'react';
import { View, Text, FlatList, TouchableOpacity, Alert } from 'react-native';
import VisionMotoAPI from '../services/VisionMotoAPI';

const MotosList = ({ userId }) => {
  const [motos, setMotos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMotos();
  }, []);

  const loadMotos = async () => {
    try {
      const response = await VisionMotoAPI.getMotos();
      setMotos(response.motos);
    } catch (error) {
      Alert.alert('Erro', error.message);
    } finally {
      setLoading(false);
    }
  };

  const reservarMoto = async (motoId) => {
    try {
      await VisionMotoAPI.reservarMoto(motoId, userId);
      Alert.alert('Sucesso', 'Moto reservada com sucesso!');
      loadMotos(); // Recarrega a lista
    } catch (error) {
      Alert.alert('Erro', error.message);
    }
  };

  const renderMoto = ({ item }) => (
    <View style={styles.motoCard}>
      <Text style={styles.motoModelo}>{item.modelo}</Text>
      <Text style={styles.motoPlaca}>{item.placa}</Text>
      <Text style={styles.motoBateria}>Bateria: {item.bateria}%</Text>
      <Text style={styles.motoZona}>Zona: {item.zona}</Text>
      
      {item.status === 'disponivel' && (
        <TouchableOpacity
          style={styles.reservarButton}
          onPress={() => reservarMoto(item.id)}
        >
          <Text style={styles.reservarButtonText}>Reservar</Text>
        </TouchableOpacity>
      )}
      
      {item.status === 'em_uso' && (
        <Text style={styles.statusEmUso}>Em Uso</Text>
      )}
    </View>
  );

  if (loading) {
    return <Text>Carregando motos...</Text>;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Motos Disponíveis</Text>
      <FlatList
        data={motos}
        renderItem={renderMoto}
        keyExtractor={(item) => item.id}
        refreshing={loading}
        onRefresh={loadMotos}
      />
    </View>
  );
};

const styles = {
  container: {
    flex: 1,
    padding: 16,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  motoCard: {
    backgroundColor: '#f5f5f5',
    padding: 16,
    marginBottom: 12,
    borderRadius: 8,
  },
  motoModelo: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  motoPlaca: {
    fontSize: 16,
    color: '#666',
  },
  motoBateria: {
    fontSize: 14,
    color: '#333',
  },
  motoZona: {
    fontSize: 14,
    color: '#333',
  },
  reservarButton: {
    backgroundColor: '#007AFF',
    padding: 12,
    borderRadius: 6,
    marginTop: 8,
  },
  reservarButtonText: {
    color: 'white',
    textAlign: 'center',
    fontWeight: 'bold',
  },
  statusEmUso: {
    color: '#FF3B30',
    fontWeight: 'bold',
    marginTop: 8,
  },
};

export default MotosList;
```

### Exemplo Flutter

```dart
// services/vision_moto_api.dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class VisionMotoAPI {
  static const String baseURL = 'http://localhost:5001/api/mobile';
  String? _token;

  Future<Map<String, dynamic>> login(String email, String senha) async {
    final response = await http.post(
      Uri.parse('$baseURL/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'senha': senha}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _token = data['token'];
      return data;
    } else {
      throw Exception('Erro ao fazer login');
    }
  }

  Future<Map<String, dynamic>> getMotos() async {
    final response = await http.get(
      Uri.parse('$baseURL/motos'),
      headers: {
        'Authorization': 'Bearer $_token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Erro ao buscar motos');
    }
  }

  Future<Map<String, dynamic>> reservarMoto(String motoId, String usuarioId) async {
    final response = await http.post(
      Uri.parse('$baseURL/motos/$motoId/reservar'),
      headers: {
        'Authorization': 'Bearer $_token',
        'Content-Type': 'application/json',
      },
      body: jsonEncode({'usuario_id': usuarioId}),
    );

    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Erro ao reservar moto');
    }
  }
}
```

### Configuração de Rede

Para desenvolvimento local, adicione no `android/app/src/main/AndroidManifest.xml`:

```xml
<application
    android:usesCleartextTraffic="true"
    ...>
```

Para iOS, adicione no `ios/Runner/Info.plist`:

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```
