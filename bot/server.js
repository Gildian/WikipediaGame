const express = require("express");
const { spawn } = require("child_process");
const fs = require('fs');
require("colors");

const app = express();

app.post("/", async (req, res) => {
  const isRandom = req.body?.isRandom || true;
  const startArticle = req.body?.startArticle;
  const endArticle = req.body?.endArticle;
  const algo = req.body?.algo || 'best_first_search';
  const botFile = 'main.py';
  let botData;
  let args = [`${botFile}`, 'client'];

  if (isRandom === 'random') {
    args.push('random');
  }
  else if (!isRandom) {
    args.push(`${startArticle}`, `${endArticle}`)
  }

  args.push(`${algo}`)

  const wikiBot = spawn('python', args);

  wikiBot.on('close', (code) => {
    fs.readFile('./path.json', 'utf8', (err, jsonString) => {
      if (err) {
        console.log("Error reading json file:", err);
        return;
      }

      try {
        botData = JSON.parse(jsonString);
        console.log(botData);
      } catch (err) {
        console.log('Error parsing JSON string:', err);
      }
    });

    console.log(`Server: Wiki Bot closed with code ${code}`);
  });

  res.status(200).json("boing");
});

app.use((req, res, next) => {
  res.status(404).send("404 Not Found");
});

const port = process.env.PORT || 4000;

// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`.magenta);
});
