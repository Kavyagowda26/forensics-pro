# Contributing to Forensics Pro

Thank you for your interest in contributing!

## Development Setup

`ash
# Clone and setup
git clone https://github.com/yourusername/forensics-pro.git
cd forensics-pro

# Start development environment
docker-compose up -d

# Access at http://localhost:3000
`

## Code Style

- Python: PEP 8
- JavaScript: Standard JS
- Commit messages: Descriptive and concise

## Testing

Before submitting:

`ash
# Test backend API
curl http://localhost:5000/api/health

# Test frontend
http://localhost:3000
`

## PR Process

1. Fork repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit PR with description
6. Address review feedback
7. Merge upon approval
