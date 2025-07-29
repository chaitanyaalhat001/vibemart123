# 🚀 Deploying VibeMart to Vercel

This guide will help you deploy your VibeMart Django application to Vercel for free.

## 📋 Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **PostgreSQL Database**: You'll need a free PostgreSQL database (recommended: [Supabase](https://supabase.com) or [Neon](https://neon.tech))

## 🗄️ Database Setup

Since Vercel doesn't support SQLite in production, you need a PostgreSQL database:

### Option 1: Supabase (Recommended)
1. Go to [supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings → Database
4. Copy the connection details

### Option 2: Neon
1. Go to [neon.tech](https://neon.tech)
2. Create a new project
3. Copy the connection string

## 🔧 Vercel Configuration

### 1. Connect Repository
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your GitHub repository

### 2. Environment Variables
In your Vercel project settings, add these environment variables:

```bash
SECRET_KEY=your-super-secret-django-key-here
DEBUG=False
DATABASE_NAME=your_database_name
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_HOST=your_database_host
DATABASE_PORT=5432
```

### 3. Build Settings
Vercel should automatically detect Django. If not, set:
- **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
- **Output Directory**: Leave empty
- **Install Command**: `pip install -r requirements.txt`

## 🚀 Deployment Steps

### 1. Push Your Code
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

### 2. Deploy on Vercel
1. In Vercel dashboard, click "Deploy"
2. Wait for the build to complete
3. Your app will be available at `your-app-name.vercel.app`

### 3. Run Database Migrations
After successful deployment, you need to run migrations:

```bash
# You'll need to do this via Vercel CLI or a one-time deployment script
vercel env pull .env.local
python manage.py migrate
python manage.py setup_sample_data  # Optional: Load sample data
```

## ⚠️ Important Notes

### Media Files Limitation
- Vercel doesn't support persistent file storage
- Uploaded images will be lost on each deployment
- For production, consider using:
  - **Cloudinary** for image hosting
  - **AWS S3** for file storage
  - **Supabase Storage** for files

### Database Considerations
- Make sure your PostgreSQL database allows external connections
- Keep your database credentials secure
- Consider using connection pooling for better performance

### Static Files
- Static files are automatically collected during build
- CSS, JS, and images in `/static/` will work correctly

## 🔍 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check your `requirements.txt` has all dependencies
   - Ensure Python version compatibility

2. **Database Connection Error**
   - Verify all database environment variables
   - Check if database allows external connections
   - Ensure SSL mode is set correctly

3. **Static Files Not Loading**
   - Check `STATIC_ROOT` configuration in settings
   - Verify `collectstatic` runs during build

4. **403 Forbidden Error**
   - Add your Vercel domain to `ALLOWED_HOSTS`
   - Check environment variables are set correctly

### Debug Commands
```bash
# Check environment variables
vercel env ls

# View build logs
vercel logs

# Run local build
vercel build
```

## 🎯 Post-Deployment Checklist

- [ ] App loads successfully
- [ ] Database connections work
- [ ] User registration/login works
- [ ] Admin panel accessible
- [ ] Static files load correctly
- [ ] Sample data loaded (optional)

## 🔄 Updates and Maintenance

### Updating Your App
1. Make changes to your code
2. Push to GitHub
3. Vercel automatically redeploys

### Database Migrations
For schema changes:
```bash
# Generate migrations locally
python manage.py makemigrations

# Commit and push
git add migrations/
git commit -m "Add new migrations"
git push

# Migrations will run automatically on deployment
```

## 📞 Support

If you encounter issues:
1. Check Vercel's build logs
2. Verify environment variables
3. Test database connection
4. Check Django logs

---

🎉 **Congratulations!** Your VibeMart application should now be live on Vercel! 