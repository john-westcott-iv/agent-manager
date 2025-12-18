# Backend Team Guidelines

## Architecture Patterns

### Service Layer
All business logic should be in service classes, not in API endpoints.

```python
# Good
class UserService:
    def create_user(self, data: UserCreate) -> User:
        # Business logic here
        pass

# Bad - logic in endpoint
@app.post("/users")
def create_user(data: UserCreate):
    # Don't put business logic here
    pass
```

### Error Handling
Use custom exceptions with proper HTTP status codes.

```python
class UserNotFoundError(HTTPException):
    def __init__(self, user_id: int):
        super().__init__(
            status_code=404,
            detail=f"User {user_id} not found"
        )
```

## Testing Guidelines

- Unit tests for services
- Integration tests for API endpoints
- Use fixtures for database setup
- Mock external services

## On-Call Rotation

See team wiki for current rotation schedule.

