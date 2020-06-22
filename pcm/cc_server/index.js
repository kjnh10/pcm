const app = require('express')();
const bodyParser = require('body-parser');

const port = 8080;

app.use(bodyParser.json());

const util = require('util');
const exec = util.promisify(require('child_process').exec);

async function prepare(url) {
  const { stdout, stderr } = await exec(`pwd && pcm ppp ${url}`);
  console.log('stdout:', stdout);
  console.log('stderr:', stderr);
}

app.post('/', (req, res) => {
  const data = req.body;

  console.log(`Problem name: ${data.name}`);
  console.log(`Problem group: ${data.group}`);
  console.log('Full body:');
  console.log(JSON.stringify(data, null, 4));
  prepare(data.url);

  res.sendStatus(200);
});

app.listen(port, err => {
  if (err) {
    console.error(err);
    process.exit(1);
  }

  console.log(`Listening on port ${port}`);
});
