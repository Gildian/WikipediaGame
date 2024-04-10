const express = require("express");
const { spawn } = require("child_process");
const fs = require('fs');
const path = require('path');
const colors = require("colors");
const cors = require('cors');

const app = express();
app.use(cors());

app.post("/", async (req, res) => {
  const { isRandom = true, startArticle, endArticle, algo = 'best_first_search' } = req.body;
  const botFile = 'main.py';
  const botDataPath = './path.json';
  const args = [botFile, 'client'];

  switch (isRandom) {
    case true:
      args.push('random');
      break;
    case false:
      args.push(startArticle, endArticle);
      break;
  }

  args.push(algo);
  console.log(args);

  const wikiBot = spawn('python', args);

  wikiBot.stdout.on('data', (data) => {
    const dataString = data.toString();
    if (dataString.length !== 2 && (dataString.includes('/') || dataString.includes('|') || dataString.includes('\\'))) {
      console.log(dataString);
    }
  });

  wikiBot.on('close', (code) => {
    fs.readFile(path.join(__dirname, botDataPath), 'utf8', (err, jsonString) => {
      if (err) {
        console.log("Error reading json file:", err);
        return;
      }

      try {
        const botData = JSON.parse(jsonString);
        console.log(botData);
        res.status(200).json(botData);
      } catch (err) {
        console.log('Error parsing JSON string:', err);
      }
    });

    console.log(`Server: Wiki Bot closed with code ${code}`);
  });
});

app.use((req, res, next) => {
  res.status(404).send("404 Not Found");
});

const port = process.env.PORT || 4000;

// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`.magenta);
});
