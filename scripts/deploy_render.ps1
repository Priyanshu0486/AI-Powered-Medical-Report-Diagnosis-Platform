# 🚀 Quick Render Deployment Script
# Medical Diagnosis API - Deploy to Render

# Step 1: Push to GitHub
Write-Host "📋 Step 1: Preparing for Render deployment..." -ForegroundColor Blue
Write-Host ""

# Check if we're in a git repository
if (-not (Test-Path ".git")) {
    Write-Host "❌ Not in a Git repository. Initializing..." -ForegroundColor Red
    git init
    git add .
    git commit -m "Initial commit for Render deployment"
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
} else {
    Write-Host "✅ Git repository detected" -ForegroundColor Green
}

# Check for uncommitted changes
$status = git status --porcelain
if ($status) {
    Write-Host "📝 Found uncommitted changes. Committing..." -ForegroundColor Yellow
    git add .
    git commit -m "Update configuration for Render deployment"
    Write-Host "✅ Changes committed" -ForegroundColor Green
} else {
    Write-Host "✅ No uncommitted changes" -ForegroundColor Green
}

Write-Host ""
Write-Host "🔧 Render Deployment Configuration:" -ForegroundColor Cyan
Write-Host "   ✅ render.yaml created" -ForegroundColor Green
Write-Host "   ✅ requirements.txt updated" -ForegroundColor Green  
Write-Host "   ✅ start_server.py created" -ForegroundColor Green
Write-Host "   ✅ Production CORS configured" -ForegroundColor Green

Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Blue
Write-Host ""

Write-Host "1. Push to GitHub:" -ForegroundColor White
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/Medical-Report-Diagnosis.git" -ForegroundColor Gray
Write-Host "   git branch -M main" -ForegroundColor Gray
Write-Host "   git push -u origin main" -ForegroundColor Gray
Write-Host ""

Write-Host "2. Deploy on Render:" -ForegroundColor White
Write-Host "   • Go to: https://render.com" -ForegroundColor Gray
Write-Host "   • Click 'New' → 'Blueprint'" -ForegroundColor Gray
Write-Host "   • Connect your GitHub account" -ForegroundColor Gray
Write-Host "   • Select 'Medical-Report-Diagnosis' repository" -ForegroundColor Gray
Write-Host "   • Click 'Apply' (render.yaml will be detected)" -ForegroundColor Gray
Write-Host ""

Write-Host "3. Configure Environment Variables in Render:" -ForegroundColor White
$envVars = @(
    "MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/",
    "DATABASE_NAME=medical_diagnosis",
    "PINECONE_API_KEY=your_pinecone_api_key", 
    "PINECONE_INDEX_NAME=medical-reports",
    "GROQ_API_KEY=your_groq_api_key",
    "HUGGINGFACE_API_TOKEN=your_hf_token",
    "ENVIRONMENT=production"
)

foreach ($var in $envVars) {
    Write-Host "   • $var" -ForegroundColor Gray
}

Write-Host ""
Write-Host "4. Your API will be available at:" -ForegroundColor White
Write-Host "   🌐 https://medical-diagnosis-api.onrender.com" -ForegroundColor Green
Write-Host "   📚 https://medical-diagnosis-api.onrender.com/docs" -ForegroundColor Green
Write-Host "   💚 https://medical-diagnosis-api.onrender.com/health" -ForegroundColor Green

Write-Host ""
Write-Host "🎯 Pro Tips:" -ForegroundColor Magenta
Write-Host "   • Free tier has 750 hours/month" -ForegroundColor Gray
Write-Host "   • Service sleeps after 15 min of inactivity" -ForegroundColor Gray
Write-Host "   • Use UptimeRobot to keep it warm" -ForegroundColor Gray
Write-Host "   • Upgrade to Starter ($7/month) for always-on" -ForegroundColor Gray

Write-Host ""
Write-Host "📞 Support:" -ForegroundColor Blue
Write-Host "   • Render Docs: https://render.com/docs" -ForegroundColor Gray
Write-Host "   • Community: https://community.render.com" -ForegroundColor Gray

Write-Host ""
Write-Host "🎉 Ready for Render deployment! Follow the steps above." -ForegroundColor Green

# Optional: Open Render in browser
$openBrowser = Read-Host "Open Render.com in browser? (y/n)"
if ($openBrowser -eq "y" -or $openBrowser -eq "Y") {
    Start-Process "https://render.com/register"
}