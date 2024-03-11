const express = require("express");
const { spawn, exec } = require("child_process");
require("colors");

const app = express();

app.post("/", async (req, res) => {
  const startArticle = req.body?.startArticle;
  const endArticle = req.body?.endArticle;
  const botFunc = 'test.py';
  const botFin = false;

  // wrap this in a promise
  // add random button to client
  const wikiBot = spawn('python', [`${botFunc}`]);

  wikiBot.stdout.on('data', (data) => {
    console.log(`Server: stdout: ${data}`);
  });

  wikiBot.stderr.on('data', (data) => {
    console.log(`Server: stderr: ${data}`);
  });

  wikiBot.on('close', (code) => {
    console.log(`Server: Wiki Bot closed with code ${code}`);
  });

  //res.status(200).json("boing");
});

app.use((req, res, next) => {
  res.status(404).send("404 Not Found");
});

const port = process.env.PORT || 4000;

// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`.magenta);
});
