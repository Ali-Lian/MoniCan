const express = require('express');
const mysql = require('mysql');
const cors = require('cors');
require('dotenv').config(); // 載入 .env 檔案

const app = express();

app.use(cors());

const pool = mysql.createPool({
  host: process.env.DB_HOST,
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME
});

app.get('/community', (req, res) => {
  pool.query('SELECT * FROM community', (err, results) => {
    if (err) {
      console.error('Error querying database:', err);
      res.status(500).send('Error querying database');
      return;
    }
    res.json(results);
  });
});

app.get('/TrashCan', (req, res) => {
  pool.query('SELECT * FROM trashcan', (err, results) => {
    if (err) {
      console.error('Error querying database:', err);
      res.status(500).send('Error querying database');
      return;
    }
    res.json(results);
  });
});

app.get('/Record', (req, res) => {
  pool.query('SELECT * FROM record', (err, results) => {
    if (err) {
      console.error('Error querying database:', err);
      res.status(500).send('Error querying database');
      return;
    }
    res.json(results);
  });
});

app.get('/newRecord', (req, res) => {
  pool.query('SELECT r.* FROM record r INNER JOIN (SELECT trashCanID, MAX(recordID) AS maxRecordID FROM record GROUP BY trashCanID) maxRecords ON r.trashCanID = maxRecords.trashCanID AND r.recordID = maxRecords.maxRecordID', (err, results) => {
    if (err) {
      console.error('Error querying database:', err);
      res.status(500).send('Error querying database');
      return;
    }
    res.json(results);
  });
});

app.get('/customer', (req, res) => {
  pool.query('SELECT * FROM customer', (err, results) => {
    if (err) {
      console.error('Error querying database:', err);
      res.status(500).send('Error querying database');
      return;
    }
    res.json(results);
  });
});


app.listen(3000, () => {
  console.log('Server is running on port 3000');
});