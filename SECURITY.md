# 🔒 Security Guidelines for IntelliAssist.AI

## 🚨 API Key Protection

### ✅ What's Protected
- **Environment Files**: All `.env*` files are gitignored
- **API Keys**: Groq and Hugging Face keys are secure
- **Logs**: Application logs excluded from git
- **Uploads**: User upload directory is gitignored
- **Cache Files**: Python cache and build files excluded

### 🔑 API Keys Setup

#### Backend Environment (.env)
```bash
# Copy the example and add your keys
cp backend/env.example backend/.env

# Edit with your actual API keys
GROQ_API_KEY=your_actual_groq_key_here
HF_API_KEY=your_actual_hf_key_here
```

#### Getting API Keys

**Groq API** (for LLaMA 3):
- Sign up: https://console.groq.com/
- Generate API key
- Add to `backend/.env`

**Hugging Face** (for Vision/Audio):
- Sign up: https://huggingface.co/
- Create token: https://huggingface.co/settings/tokens
- Add to `backend/.env`

### 🛡️ Security Best Practices

#### Never Commit:
- ❌ `.env` files
- ❌ API keys in code
- ❌ Secrets in comments
- ❌ Production URLs in dev code

#### Always Do:
- ✅ Use environment variables
- ✅ Rotate API keys regularly
- ✅ Use different keys for dev/prod
- ✅ Monitor API usage
- ✅ Set rate limits

### 📋 Security Checklist

- [ ] `.env` file created from example
- [ ] API keys added to `.env`
- [ ] `.env` appears in `.gitignore`
- [ ] `git status` doesn't show `.env`
- [ ] Different keys for dev/production
- [ ] Keys have appropriate permissions

### 🚨 If Keys Are Compromised

1. **Immediately revoke** the compromised keys
2. **Generate new keys** from the respective services
3. **Update `.env`** with new keys
4. **Check git history** for any accidental commits
5. **Monitor usage** for unusual activity

### 🔍 Testing Security

```bash
# Verify .env is ignored
git check-ignore backend/.env

# Should return the file path if properly ignored

# Check what files would be committed
git status

# .env should NOT appear in untracked files
```

### 📞 Emergency Contacts

If you suspect a security breach:
- Groq Support: Check their documentation
- Hugging Face: Check their security guidelines
- Immediately rotate all API keys

## 📚 Additional Resources

- [Groq API Documentation](https://console.groq.com/docs)
- [Hugging Face Security](https://huggingface.co/docs/hub/security)
- [Git Security Best Practices](https://docs.github.com/en/code-security)

---
**Remember**: Security is everyone's responsibility. When in doubt, ask! 