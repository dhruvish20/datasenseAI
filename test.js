import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 100,
  duration: '3m',
};

const VALID_FILE_IDS = [
  "1349a6f3-cb1a-4611-ad3e-c647b88714f9"
];

const QUESTIONS = [
  "plot sales over time",
  "show distribution of profit",
  "average discount",
  "summary of quantity and shipping cost",
];

// const question = "average discount";  // Fixed question


export default function () {
  const file_id = VALID_FILE_IDS[Math.floor(Math.random() * VALID_FILE_IDS.length)];
  const question = QUESTIONS[Math.floor(Math.random() * QUESTIONS.length)];
  // const question = "average discount"; 

  const fakeIp = `192.168.0.${Math.floor(Math.random() * 255)}`;
  // const fakeIp = "192.168.1.100";  

  const res = http.post("http://backend:8000/ask/", JSON.stringify({
    file_id,
    question,
  }), {
    headers: {
      "Content-Type": "application/json",
      "X-Forwarded-For": fakeIp  
    },
  });


  check(res, {
    'status is 200 or 202': (r) => r.status === 200 || r.status === 202,
  });

  sleep(1);
}
