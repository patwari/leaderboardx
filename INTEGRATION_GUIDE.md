# LeaderboardX Integration Guide

Complete guide for integrating LeaderboardX leaderboards into your game.

## 🚀 Quick Start

### 1. Get Your Credentials
After registering your studio and creating a game, you'll receive:
- **Game ID**: Unique identifier for your game
- **API Key**: Secret key for authentication

### 2. Basic Score Submission
```http
POST /api/v1/client/games/{game_id}/leaderboards/{leaderboard_key}/submit
Content-Type: application/json
X-API-Key: your-game-api-key

{
  "player_id": "player123",
  "score": 85420,
  "player_name": "PlayerNinja",
  "player_data": {
    "level": 15,
    "character": "wizard"
  }
}
```

### 3. Fetch Leaderboard
```http
GET /api/v1/client/games/{game_id}/leaderboards/{leaderboard_key}/top?limit=10
X-API-Key: your-game-api-key
```

## 🔐 Authentication

### API Key Setup
Include your API key in every request:
```javascript
// JavaScript example
const headers = {
  'Content-Type': 'application/json',
  'X-API-Key': 'your-game-api-key'
};
```

### Security Best Practices
- ⚠️ **Never expose API keys in client-side code**
- ✅ Store API keys securely on your game server
- ✅ Use HTTPS for all API calls
- ✅ Implement server-side score validation
- ✅ Regenerate API keys if compromised

## 📊 Core API Endpoints

### Submit Score
Submit a player's score to a leaderboard.

**Endpoint**: `POST /api/v1/client/games/{game_id}/leaderboards/{leaderboard_key}/submit`

**Parameters**:
- `game_id`: Your game's unique identifier
- `leaderboard_key`: Leaderboard identifier (e.g., "daily_scores")

**Request Body**:
```json
{
  \"player_id\": \"string\",      // Required: Unique player identifier\n  \"score\": \"number\",        // Required: Player's score\n  \"player_name\": \"string\",   // Optional: Display name\n  \"player_data\": \"object\"     // Optional: Additional player info\n}
```

**Response**:
```json
{
  \"success\": true,
  \"score_id\": 12345,
  \"leaderboard_id\": 67,
  \"submitted_at\": \"2023-12-30T10:30:00Z\"
}
```

### Get Top Scores
Retrieve the highest scores from a leaderboard.

**Endpoint**: `GET /api/v1/client/games/{game_id}/leaderboards/{leaderboard_key}/top`

**Query Parameters**:
- `limit`: Number of scores to return (default: 10, max: 100)

**Response**:
```json
{
  \"leaderboard\": {
    \"key\": \"daily_scores\",
    \"name\": \"Daily High Scores\",
    \"game_id\": \"my-awesome-game\"
  },
  \"scores\": [
    {
      \"rank\": 1,
      \"player_id\": \"PlayerNinja\",
      \"score\": 95420,
      \"submitted_at\": \"2023-12-30T09:15:00Z\"
    }
  ],
  \"total_players\": 1337
}
```

### Get Player Rank
Get a specific player's rank and score.

**Endpoint**: `GET /api/v1/client/games/{game_id}/leaderboards/{leaderboard_key}/player/{player_id}`

**Response**:
```json
{
  \"player_id\": \"PlayerNinja\",
  \"rank\": 15,
  \"score\": 85420,
  \"leaderboard\": {
    \"key\": \"daily_scores\",
    \"name\": \"Daily High Scores\",
    \"game_id\": \"my-awesome-game\"
  }
}
```

## 💻 SDK Examples

### Unity (C#)
```csharp
using UnityEngine;
using System.Collections;
using System.Text;

public class LeaderboardManager : MonoBehaviour 
{
    private const string API_KEY = \"your-game-api-key\";
    private const string BASE_URL = \"https://api.leaderboardx.com\";
    private const string GAME_ID = \"your-game-id\";

    public IEnumerator SubmitScore(string playerId, int score, string playerName = null)
    {
        string url = $\"{BASE_URL}/api/v1/client/games/{GAME_ID}/leaderboards/main/submit\";
        
        var scoreData = new {
            player_id = playerId,
            score = score,
            player_name = playerName
        };
        
        string jsonData = JsonUtility.ToJson(scoreData);
        
        using (UnityWebRequest request = new UnityWebRequest(url, \"POST\"))
        {
            request.SetRequestHeader(\"Content-Type\", \"application/json\");
            request.SetRequestHeader(\"X-API-Key\", API_KEY);
            request.uploadHandler = new UploadHandlerRaw(Encoding.UTF8.GetBytes(jsonData));
            request.downloadHandler = new DownloadHandlerBuffer();

            yield return request.SendWebRequest();

            if (request.result == UnityWebRequest.Result.Success)
            {
                Debug.Log(\"Score submitted successfully!\");
            }
            else
            {
                Debug.LogError($\"Error: {request.error}\");
            }
        }
    }
}
```

### JavaScript/Node.js
```javascript
class LeaderboardAPI {
    constructor(gameId, apiKey) {
        this.gameId = gameId;
        this.apiKey = apiKey;
        this.baseURL = 'https://api.leaderboardx.com';
    }

    async submitScore(playerId, score, playerName = null, playerData = {}) {
        const response = await fetch(
            `${this.baseURL}/api/v1/client/games/${this.gameId}/leaderboards/main/submit`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': this.apiKey
                },
                body: JSON.stringify({
                    player_id: playerId,
                    score: score,
                    player_name: playerName,
                    player_data: playerData
                })
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    }

    async getTopScores(leaderboardKey = 'main', limit = 10) {
        const response = await fetch(
            `${this.baseURL}/api/v1/client/games/${this.gameId}/leaderboards/${leaderboardKey}/top?limit=${limit}`,
            {
                headers: {
                    'X-API-Key': this.apiKey
                }
            }
        );

        return await response.json();
    }
}

// Usage
const leaderboard = new LeaderboardAPI('your-game-id', 'your-api-key');
await leaderboard.submitScore('player123', 95420, 'PlayerNinja');
```

### Python
```python
import requests
from typing import Optional, Dict, Any

class LeaderboardAPI:
    def __init__(self, game_id: str, api_key: str):
        self.game_id = game_id
        self.api_key = api_key
        self.base_url = \"https://api.leaderboardx.com\"
        self.headers = {
            \"Content-Type\": \"application/json\",
            \"X-API-Key\": api_key
        }

    def submit_score(
        self, 
        player_id: str, 
        score: float, 
        player_name: Optional[str] = None,
        player_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        url = f\"{self.base_url}/api/v1/client/games/{self.game_id}/leaderboards/main/submit\"
        
        data = {
            \"player_id\": player_id,
            \"score\": score
        }
        
        if player_name:
            data[\"player_name\"] = player_name
        if player_data:
            data[\"player_data\"] = player_data

        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_top_scores(self, leaderboard_key: str = \"main\", limit: int = 10) -> Dict[str, Any]:
        url = f\"{self.base_url}/api/v1/client/games/{self.game_id}/leaderboards/{leaderboard_key}/top\"
        params = {\"limit\": limit}
        
        response = requests.get(url, params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()

# Usage
api = LeaderboardAPI(\"your-game-id\", \"your-api-key\")
result = api.submit_score(\"player123\", 95420, \"PlayerNinja\")
```

## 🔄 Real-time Updates

### WebSocket Connection (Advanced)
For real-time leaderboard updates in your game:

```javascript
const ws = new WebSocket('wss://api.leaderboardx.com/ws/games/your-game-id/leaderboards/main');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'score_update') {
        updateLeaderboardUI(data.scores);
    }
};
```

## ⚡ Rate Limits

### Limits by Subscription Tier
- **Free**: 10,000 requests/month
- **Pro**: 100,000 requests/month  
- **Enterprise**: Custom limits

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1672401600
```

### Best Practices
- Implement exponential backoff for retries
- Cache leaderboard data locally when possible
- Batch score submissions if submitting multiple scores
- Monitor rate limit headers and adjust accordingly

## 🚫 Error Handling

### Common Error Responses
```json
// Invalid API Key
{
  \"detail\": \"Invalid or inactive API key\",
  \"status_code\": 401
}

// Rate limit exceeded
{
  \"detail\": \"Rate limit exceeded\",
  \"status_code\": 429
}

// Leaderboard not found
{
  \"detail\": \"Leaderboard not found or inactive\",
  \"status_code\": 404
}
```

### Error Handling Example
```javascript
try {
    const result = await leaderboard.submitScore('player123', 95420);
    console.log('Score submitted:', result);
} catch (error) {
    if (error.status === 429) {
        // Rate limited - wait and retry
        setTimeout(() => retrySubmission(), 1000);
    } else if (error.status === 401) {
        // Invalid API key - check credentials
        console.error('API key invalid or expired');
    } else {
        console.error('Submission failed:', error.message);
    }
}
```

## 🧪 Testing

### Sandbox Environment
Use our sandbox environment for testing:
- **Base URL**: `https://sandbox-api.leaderboardx.com`
- **Test API Keys**: Use keys prefixed with `test_`
- **Reset Data**: Sandbox data resets daily

### Testing Checklist
- [ ] Score submission works correctly
- [ ] Leaderboard retrieval displays proper rankings
- [ ] Error handling works for invalid requests
- [ ] Rate limiting is handled gracefully
- [ ] Player data is stored and retrieved correctly

---

*Need help with integration? Contact our support team at support@leaderboardx.com or join our Discord community.*