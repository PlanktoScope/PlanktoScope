import express from "express";
import cors from "cors";

const app = express();

let hardware = "PlanktoScope v3.0";
let country = "FR";
let timezone = "Europe/Paris";

app.use(cors());
app.use(express.json());

app.get("/hardware", (req, res) => {
  res.json({ value: hardware });
});

app.post("/hardware", (req, res) => {
  hardware = req.body.value;
  res.end();
});

app.get("/country", (req, res) => {
  res.json({ value: country });
});

app.post("/country", (req, res) => {
  country = req.body.value;
  res.end();
});

app.get("/timezone", (req, res) => {
  res.json({ value: timezone });
});

app.post("/timezone", (req, res) => {
  timezone = req.body.value;
  res.end();
});

app.listen(8585);
