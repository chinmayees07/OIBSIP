const express = require('express');
const path = require('path');
const app = express();
const PORT = 5000;
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));
app.get('/api/health', (req,res)=>res.json({ok:true,message:'Server is running'}));
app.listen(PORT, ()=>console.log(`BMI Calculator running at http://localhost:${PORT}`));
