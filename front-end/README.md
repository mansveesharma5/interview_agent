# Virtual Environment Activate
-(Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned) ; (& d:\Python_Interview_Agent\back-end\v_env\Scripts\Activate.ps1)

# For moving the folder to other system then don't use above absolute path, use relative path
- v_env\Scripts\activate.bat

# Backend run 
- uvicorn main:app --reload
- OR fastapi dev

# Frontend run
- npm run dev

# Before Deployment in frontend run
- npm run build

- pip install fastapi uvicorn google-generativeai python-dotenv PyPDF2 python-multipart
- pip install fastapi uvicorn python-multipart
- pip freeze > requirements.txt
- pip install google-generativeai python-dotenv
-Install Resume Parser
- pip install pdfplumber

Install Required Libraries (Front-end)
- npm install react-icons
- npm install react-markdown
- npm install remark-gfm
- npm install framer-motion
- npm install react-syntax-highlighter
- npm install react-copy-to-clipboard
- npm install react-icons framer-motion uuid
- pip install reportlab

Install Required Libraries (Back-end)
- pip install PyPDF2
- pip install python-multipart

# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
