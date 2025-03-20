# API Documentation

The Yale Trading Simulation Platform provides internal APIs for accessing stock data, user information, and trading functionality. This documentation is intended for developers working on the platform.

## Authentication

API endpoints require authentication using JWT tokens.

### Obtaining a Token

```
POST /api/auth/token
```

**Request Body:**
```json
{
  "email": "user@yale.edu",
  "password": "your_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

### Using the Token

Include the token in the Authorization header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Stock Data API

### Get Stock Information

```
GET /api/stocks/<ticker>
```

**Parameters:**
- `ticker` (path): Stock ticker symbol (e.g., AAPL)

**Response:**
```json
{
  "ticker": "AAPL",
  "name": "Apple Inc.",
  "current_price": 145.86,
  "change": 0.64,
  "change_percent": 0.44,
  "market_cap": "2.41T",
  "volume": 58642124,
  "pe_ratio": 28.34,
  "dividend_yield": 0.60,
  "fifty_two_week": {
    "high": 182.94,
    "low": 124.17
  }
}
```

### Get Historical Data

```
GET /api/stocks/<ticker>/history
```

**Parameters:**
- `ticker` (path): Stock ticker symbol
- `period` (query): Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 5y)
- `interval` (query): Data interval (1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)

**Response:**
```json
{
  "ticker": "AAPL",
  "period": "1mo",
  "interval": "1d",
  "data": [
    {
      "timestamp": "2023-03-01T00:00:00",
      "open": 143.50,
      "high": 146.75,
      "low": 142.85,
      "close": 145.86,
      "volume": 58642124
    },
    // Additional data points...
  ]
}
```

### Search Stocks

```
GET /api/stocks/search
```

**Parameters:**
- `query` (query): Search term

**Response:**
```json
{
  "results": [
    {
      "ticker": "AAPL",
      "name": "Apple Inc.",
      "exchange": "NASDAQ"
    },
    {
      "ticker": "AAPL.BA",
      "name": "Apple Inc.",
      "exchange": "Buenos Aires"
    },
    // Additional results...
  ]
}
```

## User API

### Get User Profile

```
GET /api/users/me
```

**Response:**
```json
{
  "id": 123,
  "email": "user@yale.edu",
  "first_name": "John",
  "last_name": "Doe",
  "net_id": "jd123",
  "cash_balance": 10250.75,
  "created_at": "2023-01-15T08:30:45",
  "followers_count": 12,
  "following_count": 25
}
```

### Get User Portfolio

```
GET /api/users/me/portfolio
```

**Response:**
```json
{
  "cash_balance": 10250.75,
  "total_value": 25680.42,
  "holdings": [
    {
      "ticker": "AAPL",
      "shares": 10,
      "average_price": 145.32,
      "current_price": 145.86,
      "current_value": 1458.60,
      "gain_loss": 5.40,
      "gain_loss_percent": 0.37
    },
    // Additional holdings...
  ]
}
```

### Get User Transactions

```
GET /api/users/me/transactions
```

**Parameters:**
- `page` (query): Page number
- `per_page` (query): Items per page
- `type` (query, optional): Filter by transaction type (buy, sell)

**Response:**
```json
{
  "transactions": [
    {
      "id": 456,
      "ticker": "AAPL",
      "transaction_type": "buy",
      "shares": 5,
      "price": 145.32,
      "total_amount": 726.60,
      "timestamp": "2023-02-10T14:23:18",
      "is_public": true
    },
    // Additional transactions...
  ],
  "page": 1,
  "total_pages": 3,
  "total_items": 28
}
```

## Trading API

### Place Order

```
POST /api/trading/order
```

**Request Body:**
```json
{
  "ticker": "AAPL",
  "order_type": "market",
  "transaction_type": "buy",
  "shares": 5,
  "is_public": true,
  "content": "I believe Apple will outperform due to AI integration."
}
```

**Response:**
```json
{
  "order_id": 789,
  "status": "completed",
  "ticker": "AAPL",
  "transaction_type": "buy",
  "shares": 5,
  "price": 145.86,
  "total_amount": 729.30,
  "timestamp": "2023-03-15T09:45:22",
  "is_public": true,
  "post_id": 123
}
```

### Get Order Status

```
GET /api/trading/order/<order_id>
```

**Parameters:**
- `order_id` (path): Order ID

**Response:**
```json
{
  "order_id": 789,
  "status": "completed",
  "ticker": "AAPL",
  "transaction_type": "buy",
  "shares": 5,
  "price": 145.86,
  "total_amount": 729.30,
  "timestamp": "2023-03-15T09:45:22"
}
```

## Social API

### Get Feed

```
GET /api/social/feed
```

**Parameters:**
- `page` (query): Page number
- `per_page` (query): Items per page

**Response:**
```json
{
  "posts": [
    {
      "id": 123,
      "user": {
        "id": 456,
        "first_name": "Jane",
        "last_name": "Smith",
        "net_id": "js456"
      },
      "ticker": "AAPL",
      "trade_type": "buy",
      "quantity": 5,
      "price": 145.86,
      "content": "I believe Apple will outperform due to AI integration.",
      "created_at": "2023-03-15T09:45:22",
      "likes": 12,
      "dislikes": 2,
      "comments_count": 3
    },
    // Additional posts...
  ],
  "page": 1,
  "total_pages": 8,
  "total_items": 76
}
```

### Get Post Comments

```
GET /api/social/posts/<post_id>/comments
```

**Parameters:**
- `post_id` (path): Post ID
- `page` (query): Page number
- `per_page` (query): Items per page

**Response:**
```json
{
  "comments": [
    {
      "id": 789,
      "user": {
        "id": 321,
        "first_name": "Robert",
        "last_name": "Johnson",
        "net_id": "rj321"
      },
      "content": "Good call, their new product line looks promising.",
      "created_at": "2023-03-15T10:12:45"
    },
    // Additional comments...
  ],
  "page": 1,
  "total_pages": 1,
  "total_items": 3
}
```

### Add Comment

```
POST /api/social/posts/<post_id>/comments
```

**Parameters:**
- `post_id` (path): Post ID

**Request Body:**
```json
{
  "content": "I agree with your analysis on Apple's AI strategy."
}
```

**Response:**
```json
{
  "id": 790,
  "user": {
    "id": 123,
    "first_name": "John",
    "last_name": "Doe",
    "net_id": "jd123"
  },
  "content": "I agree with your analysis on Apple's AI strategy.",
  "created_at": "2023-03-15T11:05:33"
}
```

### Like Post

```
POST /api/social/posts/<post_id>/like
```

**Parameters:**
- `post_id` (path): Post ID

**Response:**
```json
{
  "post_id": 123,
  "likes": 13,
  "user_reaction": "like"
}
```

## Error Handling

All API endpoints return standard HTTP status codes:

- 200: Success
- 400: Bad Request (invalid parameters)
- 401: Unauthorized (invalid or expired token)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (resource doesn't exist)
- 500: Server Error

Error responses include a JSON body:

```json
{
  "error": "Invalid ticker symbol",
  "status_code": 400,
  "details": "Ticker 'INVALID' not found in our database"
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse:

- Authentication: 10 requests per minute
- Stock data: 60 requests per minute
- Trading: 30 requests per minute
- Social: 60 requests per minute

Rate limit headers are included in all responses:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1623456789
```

## Webhooks (Coming Soon)

Future API versions will support webhooks for:
- Price alerts
- Order execution notifications
- Portfolio threshold events

## API Versioning

The current API version is v1. All endpoints are prefixed with `/api/v1/`.

Future versions will be available at `/api/v2/`, etc.

## Development and Testing

For development and testing purposes, a sandbox environment is available:

```
https://sandbox.ytsp.example.com/api/v1/
```

The sandbox environment includes:
- Delayed market data
- Virtual user accounts
- Simulated order execution

## Support

For API support, contact the development team at ytsp-dev@example.com 