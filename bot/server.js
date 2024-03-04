const express = require('express');

const app = express();

app.post('/', (req, res) => {
  res.send(200).json('boing');
});

app.use((req, res, next) => {
  res.status(404).send('404 Not Found');
});

const port = process.env.PORT || 4000;

// Start the server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});