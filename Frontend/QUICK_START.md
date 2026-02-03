# 🚀 Accident Detection UI - Quick Start Guide

Get your React 19 frontend running in **3 minutes**!

---

## ⚡ Prerequisites

- **Node.js** v18 or higher ([Download](https://nodejs.org/))
- **npm** (comes with Node.js)

Check your versions:
```bash
node --version
npm --version
```

---

## 📦 Installation

### Step 1: Navigate to Project
```bash
cd accident-detection-ui
```

### Step 2: Install Dependencies
```bash
npm install
```

This will install:
- React 19
- Vite
- Tailwind CSS
- Axios
- All other dependencies

**Wait time:** ~1-2 minutes

---

## 🎯 Running the Application

### Development Mode
```bash
npm run dev
```

The app will automatically open in your browser at:
```
http://localhost:3000
```

**That's it!** 🎉

---

## 🎨 What You'll See

1. **Upload Page** - Drag & drop video files
2. **Processing Animation** - Real-time progress tracking
3. **Results Display** - Accident detection results
4. **AI Explanation** - Detailed analysis explanation
5. **Theme Toggle** - Switch between light/dark modes

---

## 🔧 Environment Configuration (Optional)

Create a `.env` file in the root directory:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` to configure:
- API endpoint URL
- File size limits
- Allowed video formats

**Default values work out of the box!**

---

## 🧪 Testing the App

### Without Backend (Demo Mode)
The app includes **mock data** and works standalone:

1. Upload any video file (MP4, AVI, MOV)
2. Watch the processing animation
3. View mock analysis results
4. Explore all 5 UI states

### With Your Backend
Update `.env`:
```env
VITE_API_BASE_URL=http://your-backend-url:port/api
```

Your backend should implement:
- `POST /api/upload` - Upload video
- `POST /api/analyze` - Analyze video
- `GET /api/explanation/:id` - Get explanation

See `src/services/api.js` for details.

---

## 📱 Features to Try

✅ **Drag & Drop** - Drop video files directly  
✅ **Theme Toggle** - Click sun/moon icon (top right)  
✅ **Responsive Design** - Resize your browser  
✅ **All 5 States** - Upload → Processing → Result → Explanation → Error  
✅ **Toast Notifications** - Success/error messages  

---

## 🛠️ Available Commands

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

---

## 🎓 For Your Thesis

### Taking Screenshots

1. **Light Mode**: Default theme
2. **Dark Mode**: Click theme toggle
3. **All States**: Navigate through upload → results
4. **Responsive**: Resize browser for mobile view

### Demo Preparation

1. Have sample videos ready (MP4 format)
2. Test all features beforehand
3. Practice the upload → result flow
4. Prepare explanation of architecture

---

## ❓ Troubleshooting

### Port Already in Use?
```bash
# Edit vite.config.js and change port:
server: {
  port: 3001,  // Change this
}
```

### Dependencies Not Installing?
```bash
# Clear npm cache
npm cache clean --force
npm install
```

### Build Errors?
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Theme Not Persisting?
- Check browser localStorage is enabled
- Try a different browser

---

## 📚 Next Steps

1. ✅ App is running
2. 📖 Read full `README.md` for details
3. 🔌 Connect your backend API
4. 🎨 Customize colors/branding
5. 📸 Take screenshots for thesis

---

## 🆘 Need Help?

- Check `README.md` for full documentation
- Review code comments in source files
- Inspect browser console for errors
- Check network tab for API calls

---

**Congratulations!** Your frontend is ready! 🎉

*Now go build something amazing for your AIML project!* 🚀
