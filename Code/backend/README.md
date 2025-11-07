# Backend API pour LLM CO2 Impact

## Installation

```bash
cd backend
pip install -r requirements.txt
```

## Démarrage

```bash
python main.py
```

Le serveur démarre sur http://localhost:5000

## Endpoints disponibles

### GET /api/health
Vérification de l'état du serveur
```json
{
  "status": "ok",
  "total_rows": 161483,
  "models": ["CodeLlama 7b", "Gemma 2b", ...],
  "platforms": ["laptop1", "laptop2", "workstation", "server"]
}
```

### GET /api/energy-by-model
Consommation moyenne d'énergie par modèle et plateforme
```json
[
  {
    "model": "Gemma 2b",
    "Workstation": 0.8,
    "Server": 0,
    "Laptop1": 0.6,
    "Laptop2": 0.7
  }
]
```

### GET /api/energy-timeline
Évolution de la consommation dans le temps
```json
[
  {
    "time": "10:00",
    "CodeLlama70b_WO": 4.2,
    "Gemma2b_la": 0.6,
    "Llama370b_se": 6.2
  }
]
```

### GET /api/energy-efficiency
Données d'efficacité énergétique
```json
[
  {
    "responseLength": 150,
    "energy": 0.6,
    "model": "Gemma 2b",
    "duration": 12.5
  }
]
```

### POST /api/calculate-co2
Calcul du CO2 pour un prompt spécifique
```json
Request:
{
  "model": "Gemma 2b",
  "platform": "laptop1",
  "energy_source": "mix_france",
  "prompt": "Write a function..."
}

Response:
{
  "co2_kg": 0.000192,
  "energy_kwh": 0.006,
  "co2_per_kwh": 32,
  "energy_source": "mix_france"
}
```

### GET /api/models
Liste des modèles disponibles

### GET /api/platforms/<model>
Plateformes disponibles pour un modèle spécifique
