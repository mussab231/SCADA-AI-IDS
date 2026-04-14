FROM node:20-alpine

WORKDIR /app

# نسخ ملفات الحزم وتثبيتها
COPY package*.json ./
RUN npm install

# نسخ باقي الملفات
COPY . .

# فتح المنفذ الخاص بـ Vite
EXPOSE 5173

# تشغيل الخادم مع السماح بالاتصال الخارجي (مهم جداً للوصول من المتصفح)
CMD ["npm", "run", "dev", "--", "--host"]